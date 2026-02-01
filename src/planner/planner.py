from typing import List, Dict, Any, Optional

from ..models import PlanStep, Plan
from ..registry import AlgorithmRegistry


class Planner:
    """분석 실행 계획을 생성하는 Planner.

    설정된 알고리즘 순서에 따라 구조화된 실행 계획을 생성합니다.
    """

    def __init__(
        self,
        registry: AlgorithmRegistry,
        algorithm_order: Optional[List[str]] = None
    ):
        """
        Args:
            registry: 알고리즘 레지스트리
            algorithm_order: 알고리즘 실행 순서 (None이면 등록 순서 사용)
        """
        self.registry = registry
        self.algorithm_order = algorithm_order or registry.list_algorithms()

    def create_plan(
        self,
        text: str,
        input_specs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Plan:
        """분석 실행 계획을 생성.

        Args:
            text: 분석할 텍스트
            input_specs: 각 알고리즘에 전달할 추가 입력 명세
                        예: {"length_check": {"min_length": 20}}

        Returns:
            Plan: 생성된 실행 계획
        """
        input_specs = input_specs or {}
        steps: List[PlanStep] = []

        for idx, algorithm_name in enumerate(self.algorithm_order, start=1):
            if not self.registry.has_algorithm(algorithm_name):
                continue

            description = self._get_description(algorithm_name)
            spec = input_specs.get(algorithm_name, {})
            spec["text"] = text

            # 첫 번째 단계를 제외한 모든 단계는 이전 단계에 의존
            depends_on = [idx - 1] if idx > 1 else []

            step = PlanStep(
                step_id=idx,
                algorithm_name=algorithm_name,
                description=description,
                input_spec=spec,
                depends_on=depends_on
            )
            steps.append(step)

        metadata = {
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "text_length": len(text),
            "algorithm_count": len(steps)
        }

        return Plan(steps=steps, metadata=metadata)

    def _get_description(self, algorithm_name: str) -> str:
        """알고리즘의 설명을 가져옴.

        Args:
            algorithm_name: 알고리즘 이름

        Returns:
            알고리즘 설명 문자열
        """
        try:
            algorithm = self.registry.get_algorithm(algorithm_name)
            return algorithm.description
        except KeyError:
            return f"Execute {algorithm_name} algorithm"

    def validate_plan(self, plan: Plan) -> bool:
        """계획의 유효성을 검증.

        Args:
            plan: 검증할 계획

        Returns:
            유효한 경우 True
        """
        if not plan.steps:
            return False

        step_ids = {step.step_id for step in plan.steps}

        for step in plan.steps:
            # 알고리즘 존재 여부 확인
            if not self.registry.has_algorithm(step.algorithm_name):
                return False

            # 의존성 검증
            for dep_id in step.depends_on:
                if dep_id not in step_ids:
                    return False

        return True
