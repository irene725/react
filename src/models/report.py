from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .result import ExecutionResult, StepResult


@dataclass
class AnalysisReport:
    """분석 리포트."""

    execution_result: ExecutionResult
    report_content: str                       # Markdown 형식 리포트 내용
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def status(self) -> str:
        """실행 상태."""
        return self.execution_result.status

    @property
    def has_problem(self) -> bool:
        """문제 발견 여부."""
        return self.execution_result.has_problem

    @property
    def step_results(self) -> List[StepResult]:
        """단계별 결과."""
        return self.execution_result.step_results

    @property
    def stopped_at_algorithm(self) -> Optional[str]:
        """조기 종료된 알고리즘 이름."""
        if self.execution_result.stopped_at:
            return self.execution_result.stopped_at.algorithm_name
        return None
