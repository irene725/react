"""ReAct 패턴을 구현한 Judge Agent."""

import json
import logging
import re
from typing import Dict, Any, Optional, List, Tuple

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatLiteLLM
from openai import APITimeoutError as OpenAITimeoutError, RateLimitError as OpenAIRateLimitError
from anthropic import APITimeoutError as AnthropicTimeoutError, RateLimitError as AnthropicRateLimitError
import litellm

from ..models import JudgmentResult
from ..registry import AlgorithmRegistry
from ..exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
)
from .tools import JudgeTools, TOOLS_DESCRIPTION


logger = logging.getLogger(__name__)


# ReAct 시스템 프롬프트
REACT_SYSTEM_PROMPT = f"""You are a ReAct Judge Agent that evaluates algorithm results using the Reasoning + Acting pattern.

## Available Tools
{TOOLS_DESCRIPTION}

## Response Format

You MUST follow this exact format for EVERY response:

Thought: [Your reasoning about what to do next]
Action: [tool_name]
Action Input: [input for the tool - must be valid JSON for tools that require it]

After receiving an observation, continue with another Thought/Action/Action Input cycle until you're ready to submit your judgment.

When you have enough information, use submit_judgment to provide your final verdict.

## Important Rules
1. Always start by getting the criteria document
2. Analyze the execution result against the criteria
3. Use check_threshold and calculate_percentage to verify conditions
4. Base your judgment on specific criteria from the document
5. You MUST eventually call submit_judgment to complete the evaluation
"""


class ReactJudge:
    """ReAct (Reasoning + Acting) 패턴을 구현한 Judge Agent.

    알고리즘 실행 결과를 판단 기준 문서와 비교하여
    반복적인 추론-행동 사이클을 통해 판단을 수행합니다.
    """

    MAX_ITERATIONS = 10  # 무한 루프 방지

    def __init__(
        self,
        registry: AlgorithmRegistry,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        timeout: int = 30,
        api_key: Optional[str] = None,
        max_iterations: int = 10
    ):
        """
        Args:
            registry: 알고리즘 레지스트리 (판단 기준 문서 조회용)
            llm_provider: LLM 제공자 ("openai", "anthropic", 또는 "litellm")
            model_name: 사용할 모델 이름 (litellm의 경우 "provider/model" 형식)
            temperature: LLM 온도 설정
            timeout: API 호출 타임아웃 (초)
            api_key: API 키 (None이면 환경변수에서 로드)
            max_iterations: 최대 반복 횟수
        """
        self.registry = registry
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.timeout = timeout
        self.max_iterations = max_iterations

        self.llm = self._create_llm(api_key)
        self.tools = JudgeTools(registry)

    def _create_llm(self, api_key: Optional[str] = None):
        """LLM 인스턴스를 생성."""
        if self.llm_provider == "openai":
            kwargs = {
                "model": self.model_name,
                "temperature": self.temperature,
                "timeout": self.timeout,
            }
            if api_key is not None:
                kwargs["api_key"] = api_key
            return ChatOpenAI(**kwargs)
        elif self.llm_provider == "anthropic":
            kwargs = {
                "model": self.model_name,
                "temperature": self.temperature,
                "timeout": self.timeout,
            }
            if api_key is not None:
                kwargs["api_key"] = api_key
            return ChatAnthropic(**kwargs)
        elif self.llm_provider == "litellm":
            kwargs = {
                "model": self.model_name,
                "temperature": self.temperature,
                "timeout": self.timeout,
            }
            if api_key is not None:
                kwargs["api_key"] = api_key
            return ChatLiteLLM(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _parse_action(self, response_text: str) -> Tuple[Optional[str], Optional[str], Optional[Any]]:
        """LLM 응답에서 Thought, Action, Action Input을 파싱.

        Returns:
            (thought, action_name, action_input) 튜플
        """
        thought = None
        action = None
        action_input = None

        # Thought 추출
        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|$)", response_text, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        # Action 추출
        action_match = re.search(r"Action:\s*(\w+)", response_text)
        if action_match:
            action = action_match.group(1).strip()

        # Action Input 추출
        input_match = re.search(r"Action Input:\s*(.+?)(?=Thought:|Observation:|$)", response_text, re.DOTALL)
        if input_match:
            raw_input = input_match.group(1).strip()
            # JSON 파싱 시도
            try:
                action_input = json.loads(raw_input)
            except json.JSONDecodeError:
                # JSON이 아니면 문자열로 사용
                action_input = raw_input

        return thought, action, action_input

    def evaluate(
        self,
        algorithm_name: str,
        execution_result: Dict[str, Any]
    ) -> JudgmentResult:
        """ReAct 루프를 통해 알고리즘 실행 결과를 평가.

        Args:
            algorithm_name: 평가할 알고리즘 이름
            execution_result: 알고리즘 실행 결과

        Returns:
            JudgmentResult: 판단 결과
        """
        # 초기 프롬프트 구성
        result_json = json.dumps(execution_result, ensure_ascii=False, indent=2)
        initial_prompt = f"""Evaluate the following algorithm result:

## Algorithm: {algorithm_name}

## Execution Result:
```json
{result_json}
```

Start by getting the criteria document, then analyze the result and submit your judgment."""

        messages = [
            SystemMessage(content=REACT_SYSTEM_PROMPT),
            HumanMessage(content=initial_prompt)
        ]

        context = {
            "algorithm_name": algorithm_name,
            "execution_result": execution_result
        }

        judgment_data = None
        iterations = 0
        reasoning_trace = []  # 추론 과정 기록

        logger.info(f"Starting ReAct evaluation for {algorithm_name}")

        while iterations < self.max_iterations:
            iterations += 1
            logger.debug(f"ReAct iteration {iterations}")

            # LLM 호출
            try:
                response = self._call_llm(messages)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                raise

            response_text = response.content
            logger.debug(f"LLM response:\n{response_text}")

            # Action 파싱
            thought, action, action_input = self._parse_action(response_text)

            if thought:
                reasoning_trace.append(f"Thought: {thought}")
                logger.debug(f"Thought: {thought}")

            if not action:
                logger.warning("No action found in response, prompting for action")
                messages.append(AIMessage(content=response_text))
                messages.append(HumanMessage(content="Please provide an Action. Use submit_judgment when ready to provide your final verdict."))
                continue

            logger.debug(f"Action: {action}, Input: {action_input}")
            reasoning_trace.append(f"Action: {action}")

            # submit_judgment 처리
            if action == "submit_judgment":
                if isinstance(action_input, dict):
                    judgment_data = action_input
                    logger.info(f"Judgment submitted after {iterations} iterations")
                    break
                else:
                    messages.append(AIMessage(content=response_text))
                    messages.append(HumanMessage(
                        content="Error: submit_judgment requires JSON input with has_problem, severity, reasoning, and summary fields."
                    ))
                    continue

            # 도구 실행
            observation = self.tools.execute(action, action_input, context)
            reasoning_trace.append(f"Observation: {observation[:200]}...")

            logger.debug(f"Observation: {observation[:200]}...")

            # 대화에 추가
            messages.append(AIMessage(content=response_text))
            messages.append(HumanMessage(content=f"Observation: {observation}"))

        # 판단 결과 생성
        if judgment_data:
            return JudgmentResult(
                algorithm_name=algorithm_name,
                has_problem=judgment_data.get("has_problem", False),
                severity=judgment_data.get("severity", "none"),
                reasoning=judgment_data.get("reasoning", "") + f"\n\n[ReAct Trace: {iterations} iterations]",
                summary=judgment_data.get("summary", "")
            )
        else:
            # 최대 반복 횟수 초과
            logger.warning(f"Max iterations ({self.max_iterations}) reached without judgment")
            return JudgmentResult(
                algorithm_name=algorithm_name,
                has_problem=False,
                severity="none",
                reasoning=f"ReAct loop did not complete. Trace:\n" + "\n".join(reasoning_trace[-10:]),
                summary="Evaluation incomplete - max iterations reached"
            )

    def _call_llm(self, messages: List) -> Any:
        """LLM을 호출하고 에러를 처리."""
        try:
            return self.llm.invoke(messages)
        except (OpenAITimeoutError, AnthropicTimeoutError, litellm.Timeout) as e:
            logger.error(f"LLM timeout: {e}")
            raise LLMTimeoutError(self.llm_provider, self.timeout) from e
        except (OpenAIRateLimitError, AnthropicRateLimitError, litellm.RateLimitError) as e:
            logger.error(f"LLM rate limit: {e}")
            raise LLMRateLimitError(self.llm_provider) from e
        except Exception as e:
            logger.error(f"LLM connection error: {e}")
            raise LLMConnectionError(self.llm_provider, e) from e


class MockReactJudge:
    """테스트용 Mock Judge.

    LLM 호출 없이 규칙 기반으로 판단합니다.
    ReAct 패턴을 시뮬레이션합니다.
    """

    def __init__(self, registry: AlgorithmRegistry):
        self.registry = registry
        self.tools = JudgeTools(registry)

    def evaluate(
        self,
        algorithm_name: str,
        execution_result: Dict[str, Any]
    ) -> JudgmentResult:
        """규칙 기반으로 실행 결과를 평가 (ReAct 시뮬레이션)."""
        reasoning_trace = []

        # Step 1: Get criteria (simulated)
        reasoning_trace.append(f"Thought: I need to evaluate {algorithm_name} result")
        reasoning_trace.append("Action: get_criteria")
        reasoning_trace.append(f"Observation: Loaded criteria for {algorithm_name}")

        if algorithm_name == "length_check":
            return self._evaluate_length_check(execution_result, reasoning_trace)
        elif algorithm_name == "keyword_check":
            return self._evaluate_keyword_check(execution_result, reasoning_trace)
        else:
            return JudgmentResult(
                algorithm_name=algorithm_name,
                has_problem=False,
                severity="none",
                reasoning="Unknown algorithm, assuming no problem\n\n" + "\n".join(reasoning_trace),
                summary="No issues detected"
            )

    def _evaluate_length_check(self, result: Dict[str, Any], trace: List[str]) -> JudgmentResult:
        """길이 체크 결과 평가."""
        is_within_range = result.get("is_within_range", True)
        length_diff = result.get("length_diff", 0)
        min_length = result.get("min_length", 10)
        raw_result = result.get("raw_result", 0)

        # Step 2: Check if within range
        trace.append(f"Thought: Check if text length {raw_result} is within range")
        trace.append("Action: check_threshold")
        trace.append(f"Observation: is_within_range = {is_within_range}")

        if is_within_range:
            trace.append("Thought: Text length is acceptable, submitting judgment")
            trace.append("Action: submit_judgment")

            return JudgmentResult(
                algorithm_name="length_check",
                has_problem=False,
                severity="none",
                reasoning=f"Text length ({raw_result}) is within the allowed range ({min_length}-{result.get('max_length', 10000)}).\n\n[ReAct Trace: 3 iterations]\n" + "\n".join(trace),
                summary="Text length is acceptable."
            )

        # Step 3: Calculate percentage difference
        trace.append(f"Thought: Length is outside range, calculating severity")
        trace.append("Action: calculate_percentage")
        threshold_10_percent = min_length * 0.1
        diff_percentage = (length_diff / min_length) * 100 if min_length > 0 else 0
        trace.append(f"Observation: Difference is {diff_percentage:.1f}% of minimum")

        if length_diff <= threshold_10_percent:
            severity = "warning"
            reasoning = f"Text length ({raw_result}) is slightly below minimum ({min_length}). Difference: {length_diff} characters ({diff_percentage:.1f}%)."
        else:
            severity = "critical"
            reasoning = f"Text length ({raw_result}) is significantly below minimum ({min_length}). Difference: {length_diff} characters ({diff_percentage:.1f}% > 10% threshold)."

        trace.append(f"Thought: Severity determined as {severity}")
        trace.append("Action: submit_judgment")

        return JudgmentResult(
            algorithm_name="length_check",
            has_problem=True,
            severity=severity,
            reasoning=reasoning + f"\n\n[ReAct Trace: 4 iterations]\n" + "\n".join(trace),
            summary=f"Text length issue: {length_diff} characters {'below' if raw_result < min_length else 'above'} limit."
        )

    def _evaluate_keyword_check(self, result: Dict[str, Any], trace: List[str]) -> JudgmentResult:
        """키워드 체크 결과 평가."""
        has_forbidden = result.get("has_forbidden_keywords", False)
        keyword_count = result.get("keyword_count", 0)
        found_keywords = result.get("raw_result", [])

        # Step 2: Check for forbidden keywords
        trace.append("Thought: Check if any forbidden keywords were found")
        trace.append("Action: check_threshold")
        trace.append(f"Observation: has_forbidden_keywords = {has_forbidden}, count = {keyword_count}")

        if not has_forbidden:
            trace.append("Thought: No forbidden keywords, submitting clean judgment")
            trace.append("Action: submit_judgment")

            return JudgmentResult(
                algorithm_name="keyword_check",
                has_problem=False,
                severity="none",
                reasoning="No forbidden keywords were found in the text.\n\n[ReAct Trace: 3 iterations]\n" + "\n".join(trace),
                summary="No forbidden keywords detected."
            )

        # Step 3: Determine severity based on count
        trace.append(f"Thought: Found {keyword_count} forbidden keywords, determining severity")

        if keyword_count == 1:
            severity = "warning"
            reasoning = f"Found 1 forbidden keyword: '{found_keywords[0]}'. This may be a minor issue."
        else:
            severity = "critical"
            reasoning = f"Found {keyword_count} forbidden keywords: {', '.join(repr(k) for k in found_keywords)}. Multiple violations detected."

        trace.append(f"Thought: Severity is {severity} based on keyword count")
        trace.append("Action: submit_judgment")

        return JudgmentResult(
            algorithm_name="keyword_check",
            has_problem=True,
            severity=severity,
            reasoning=reasoning + f"\n\n[ReAct Trace: 4 iterations]\n" + "\n".join(trace),
            summary=f"Found {keyword_count} forbidden keyword(s): {', '.join(found_keywords)}"
        )
