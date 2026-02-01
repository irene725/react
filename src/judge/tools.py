"""ReAct Judge에서 사용하는 도구들."""

import json
from typing import Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class Tool:
    """도구 정의."""
    name: str
    description: str
    func: Callable


class JudgeTools:
    """ReAct Judge에서 사용할 수 있는 도구 모음.

    Available Tools:
        - get_criteria: 판단 기준 문서 로드
        - check_threshold: 임계값 조건 확인
        - calculate_percentage: 백분율 계산
        - submit_judgment: 최종 판단 제출
    """

    def __init__(self, registry):
        """
        Args:
            registry: AlgorithmRegistry 인스턴스 (판단 기준 문서 조회용)
        """
        self.registry = registry
        self._tools: Dict[str, Tool] = {}
        self._setup_tools()

    def _setup_tools(self):
        """도구들을 설정."""
        self._tools = {
            "get_criteria": Tool(
                name="get_criteria",
                description="Load judgment criteria document for an algorithm",
                func=self._get_criteria
            ),
            "check_threshold": Tool(
                name="check_threshold",
                description="Check if a value meets a threshold condition",
                func=self._check_threshold
            ),
            "calculate_percentage": Tool(
                name="calculate_percentage",
                description="Calculate what percentage one value is of another",
                func=self._calculate_percentage
            ),
            "submit_judgment": Tool(
                name="submit_judgment",
                description="Submit the final judgment",
                func=self._submit_judgment
            ),
        }

    @property
    def available_tools(self) -> Dict[str, Tool]:
        """사용 가능한 도구 목록 반환."""
        return self._tools

    def get_tool(self, name: str) -> Tool:
        """이름으로 도구를 가져옴.

        Args:
            name: 도구 이름

        Returns:
            Tool 인스턴스

        Raises:
            KeyError: 존재하지 않는 도구인 경우
        """
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def execute(self, tool_name: str, input_data: Any, context: Dict[str, Any] = None) -> str:
        """도구를 실행하고 결과를 반환.

        Args:
            tool_name: 실행할 도구 이름
            input_data: 도구에 전달할 입력
            context: 추가 컨텍스트 (algorithm_name 등)

        Returns:
            도구 실행 결과 문자열
        """
        context = context or {}

        if tool_name not in self._tools:
            return f"Error: Unknown tool '{tool_name}'. Available tools: {list(self._tools.keys())}"

        tool = self._tools[tool_name]

        try:
            if tool_name == "get_criteria":
                # algorithm_name은 context에서 가져오거나 input_data 사용
                algo_name = context.get("algorithm_name", input_data)
                return tool.func(algo_name)
            elif tool_name in ["check_threshold", "calculate_percentage", "submit_judgment"]:
                if isinstance(input_data, dict):
                    return tool.func(input_data)
                else:
                    return f"Error: {tool_name} requires JSON input"
            else:
                return tool.func(input_data)
        except Exception as e:
            return f"Error executing {tool_name}: {e}"

    # ===== Tool Implementations =====

    def _get_criteria(self, algorithm_name: str) -> str:
        """판단 기준 문서를 로드.

        Args:
            algorithm_name: 알고리즘 이름

        Returns:
            판단 기준 문서 내용 또는 에러 메시지
        """
        try:
            criteria = self.registry.get_criteria_document(algorithm_name)
            return f"Criteria document loaded:\n\n{criteria}"
        except Exception as e:
            return f"Error loading criteria: {e}"

    def _check_threshold(self, input_data: Dict[str, Any]) -> str:
        """임계값 조건을 확인.

        Args:
            input_data: {
                "value": number,
                "threshold": number,
                "operator": "gt"|"gte"|"lt"|"lte"|"eq"
            }

        Returns:
            JSON 형식의 결과 또는 에러 메시지
        """
        try:
            value = float(input_data.get("value", 0))
            threshold = float(input_data.get("threshold", 0))
            operator = input_data.get("operator", "gte")

            operators = {
                "gt": (lambda v, t: v > t, ">"),
                "gte": (lambda v, t: v >= t, ">="),
                "lt": (lambda v, t: v < t, "<"),
                "lte": (lambda v, t: v <= t, "<="),
                "eq": (lambda v, t: v == t, "=="),
            }

            if operator not in operators:
                return f"Error: Unknown operator '{operator}'. Use: gt, gte, lt, lte, eq"

            func, symbol = operators[operator]
            result = func(value, threshold)

            return json.dumps({
                "result": result,
                "comparison": f"{value} {symbol} {threshold} = {result}"
            })
        except Exception as e:
            return f"Error checking threshold: {e}"

    def _calculate_percentage(self, input_data: Dict[str, Any]) -> str:
        """백분율을 계산.

        Args:
            input_data: {
                "value": number,
                "total": number
            }

        Returns:
            JSON 형식의 결과 또는 에러 메시지
        """
        try:
            value = float(input_data.get("value", 0))
            total = float(input_data.get("total", 1))

            if total == 0:
                return json.dumps({"error": "Cannot divide by zero"})

            percentage = (value / total) * 100

            return json.dumps({
                "percentage": round(percentage, 2),
                "calculation": f"{value} / {total} * 100 = {percentage:.2f}%"
            })
        except Exception as e:
            return f"Error calculating percentage: {e}"

    def _submit_judgment(self, input_data: Dict[str, Any]) -> str:
        """최종 판단을 제출.

        이 도구는 특별한 반환값으로 ReAct 루프 종료를 신호합니다.

        Args:
            input_data: {
                "has_problem": bool,
                "severity": "none"|"warning"|"critical",
                "reasoning": str,
                "summary": str
            }

        Returns:
            특별한 종료 신호 문자열
        """
        return "__JUDGMENT_SUBMITTED__"


# 도구 설명 (시스템 프롬프트용)
TOOLS_DESCRIPTION = """
1. **get_criteria** - Load the judgment criteria document for an algorithm
   - Input: algorithm_name (string)
   - Output: The criteria document content

2. **check_threshold** - Check if a value meets a threshold condition
   - Input: {"value": number, "threshold": number, "operator": "gt"|"gte"|"lt"|"lte"|"eq"}
   - Output: {"result": true/false, "comparison": "value operator threshold"}

3. **calculate_percentage** - Calculate what percentage one value is of another
   - Input: {"value": number, "total": number}
   - Output: {"percentage": number, "calculation": "value/total*100"}

4. **submit_judgment** - Submit your final judgment (use this when you've reached a conclusion)
   - Input: {"has_problem": true/false, "severity": "none"|"warning"|"critical", "reasoning": "...", "summary": "..."}
   - Output: Judgment recorded
"""
