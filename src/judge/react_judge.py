import json
import logging
from typing import Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..models import JudgmentResult
from ..registry import AlgorithmRegistry
from .prompts import SYSTEM_PROMPT, format_user_prompt


logger = logging.getLogger(__name__)


class ReactJudge:
    """ReAct 패턴을 활용한 Judge Agent.

    알고리즘 실행 결과를 판단 기준 문서와 비교하여
    reasoning 기반의 판단을 수행합니다.
    """

    def __init__(
        self,
        registry: AlgorithmRegistry,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        timeout: int = 30,
        api_key: Optional[str] = None
    ):
        """
        Args:
            registry: 알고리즘 레지스트리 (판단 기준 문서 조회용)
            llm_provider: LLM 제공자 ("openai" 또는 "anthropic")
            model_name: 사용할 모델 이름
            temperature: LLM 온도 설정
            timeout: API 호출 타임아웃 (초)
            api_key: API 키 (None이면 환경변수에서 로드)
        """
        self.registry = registry
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.timeout = timeout

        self.llm = self._create_llm(api_key)

    def _create_llm(self, api_key: Optional[str] = None):
        """LLM 인스턴스를 생성."""
        if self.llm_provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                timeout=self.timeout,
                api_key=api_key
            )
        elif self.llm_provider == "anthropic":
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                timeout=self.timeout,
                api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def evaluate(
        self,
        algorithm_name: str,
        execution_result: Dict[str, Any]
    ) -> JudgmentResult:
        """알고리즘 실행 결과를 평가.

        Args:
            algorithm_name: 평가할 알고리즘 이름
            execution_result: 알고리즘 실행 결과

        Returns:
            JudgmentResult: 판단 결과

        Raises:
            FileNotFoundError: 판단 기준 문서가 없는 경우
            Exception: LLM 호출 실패 시
        """
        # 판단 기준 문서 로드
        criteria_document = self.registry.get_criteria_document(algorithm_name)

        # 프롬프트 생성
        result_json = json.dumps(execution_result, ensure_ascii=False, indent=2)
        user_prompt = format_user_prompt(
            algorithm_name=algorithm_name,
            execution_result=result_json,
            criteria_document=criteria_document
        )

        logger.debug(f"Evaluating {algorithm_name} with result: {result_json[:200]}...")

        # LLM 호출
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)
        response_text = response.content

        logger.debug(f"LLM response: {response_text[:500]}...")

        # 응답 파싱
        return self._parse_response(algorithm_name, response_text)

    def _parse_response(self, algorithm_name: str, response_text: str) -> JudgmentResult:
        """LLM 응답을 파싱하여 JudgmentResult를 생성.

        Args:
            algorithm_name: 알고리즘 이름
            response_text: LLM 응답 텍스트

        Returns:
            JudgmentResult 객체
        """
        try:
            # JSON 블록 추출
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            return JudgmentResult(
                algorithm_name=algorithm_name,
                has_problem=data.get("has_problem", False),
                severity=data.get("severity", "none"),
                reasoning=data.get("reasoning", ""),
                summary=data.get("summary", "")
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # 파싱 실패 시 기본 응답 반환
            return JudgmentResult(
                algorithm_name=algorithm_name,
                has_problem=False,
                severity="none",
                reasoning=f"Failed to parse response: {response_text}",
                summary="Judgment parsing failed, assuming no problem"
            )


class MockReactJudge:
    """테스트용 Mock Judge.

    LLM 호출 없이 규칙 기반으로 판단합니다.
    """

    def __init__(self, registry: AlgorithmRegistry):
        self.registry = registry

    def evaluate(
        self,
        algorithm_name: str,
        execution_result: Dict[str, Any]
    ) -> JudgmentResult:
        """규칙 기반으로 실행 결과를 평가."""

        if algorithm_name == "length_check":
            return self._evaluate_length_check(execution_result)
        elif algorithm_name == "keyword_check":
            return self._evaluate_keyword_check(execution_result)
        else:
            return JudgmentResult(
                algorithm_name=algorithm_name,
                has_problem=False,
                severity="none",
                reasoning="Unknown algorithm, assuming no problem",
                summary="No issues detected"
            )

    def _evaluate_length_check(self, result: Dict[str, Any]) -> JudgmentResult:
        """길이 체크 결과 평가."""
        is_within_range = result.get("is_within_range", True)
        length_diff = result.get("length_diff", 0)
        min_length = result.get("min_length", 10)
        raw_result = result.get("raw_result", 0)

        if is_within_range:
            return JudgmentResult(
                algorithm_name="length_check",
                has_problem=False,
                severity="none",
                reasoning=f"Text length ({raw_result}) is within the allowed range ({min_length}-{result.get('max_length', 10000)}).",
                summary="Text length is acceptable."
            )

        # 범위 벗어남 - 심각도 계산
        threshold_10_percent = min_length * 0.1
        if length_diff <= threshold_10_percent:
            severity = "warning"
            reasoning = f"Text length ({raw_result}) is slightly below minimum ({min_length}). Difference: {length_diff} characters."
        else:
            severity = "critical"
            reasoning = f"Text length ({raw_result}) is significantly below minimum ({min_length}). Difference: {length_diff} characters (>{threshold_10_percent:.0f} threshold)."

        return JudgmentResult(
            algorithm_name="length_check",
            has_problem=True,
            severity=severity,
            reasoning=reasoning,
            summary=f"Text length issue: {length_diff} characters {'below' if raw_result < min_length else 'above'} limit."
        )

    def _evaluate_keyword_check(self, result: Dict[str, Any]) -> JudgmentResult:
        """키워드 체크 결과 평가."""
        has_forbidden = result.get("has_forbidden_keywords", False)
        keyword_count = result.get("keyword_count", 0)
        found_keywords = result.get("raw_result", [])

        if not has_forbidden:
            return JudgmentResult(
                algorithm_name="keyword_check",
                has_problem=False,
                severity="none",
                reasoning="No forbidden keywords were found in the text.",
                summary="No forbidden keywords detected."
            )

        if keyword_count == 1:
            severity = "warning"
            reasoning = f"Found 1 forbidden keyword: '{found_keywords[0]}'. This may be a minor issue."
        else:
            severity = "critical"
            reasoning = f"Found {keyword_count} forbidden keywords: {', '.join(repr(k) for k in found_keywords)}. Multiple violations detected."

        return JudgmentResult(
            algorithm_name="keyword_check",
            has_problem=True,
            severity=severity,
            reasoning=reasoning,
            summary=f"Found {keyword_count} forbidden keyword(s): {', '.join(found_keywords)}"
        )
