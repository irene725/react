from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
from datetime import datetime

from .plan import Plan, PlanStep


@dataclass
class JudgmentResult:
    """Judge의 판단 결과."""

    algorithm_name: str
    has_problem: bool                         # 문제 여부
    severity: str                             # "critical" | "warning" | "none"
    reasoning: str                            # 판단 과정 설명
    summary: str                              # 1-2문장 요약
    detailed_trace: Optional[List[Dict[str, Any]]] = None  # 상세 추론 과정 (ReAct 사이클)

    def __post_init__(self):
        valid_severities = ["critical", "warning", "none"]
        if self.severity not in valid_severities:
            raise ValueError(f"severity must be one of {valid_severities}, got '{self.severity}'")


@dataclass
class StepResult:
    """각 단계 실행 결과."""

    step: PlanStep                            # 실행된 단계
    execution_result: Dict[str, Any]          # 알고리즘 실행 결과
    judgment: JudgmentResult                  # Judge 판단 결과
    executed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExecutionResult:
    """전체 실행 결과."""

    plan: Plan                                # 실행된 계획
    step_results: List[StepResult]            # 각 단계 결과
    status: str                               # "problem_found" | "all_passed"
    stopped_at: Optional[PlanStep] = None     # 조기 종료 시 중단된 단계

    def __post_init__(self):
        valid_statuses = ["problem_found", "all_passed"]
        if self.status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}, got '{self.status}'")

    @property
    def has_problem(self) -> bool:
        """문제가 발견되었는지 여부."""
        return self.status == "problem_found"

    @property
    def executed_step_count(self) -> int:
        """실행된 단계 수."""
        return len(self.step_results)

    @property
    def total_step_count(self) -> int:
        """전체 단계 수."""
        return len(self.plan.steps)
