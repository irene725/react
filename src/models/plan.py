from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
from datetime import datetime


@dataclass
class PlanStep:
    """실행 계획의 단위를 나타내는 구조체."""

    step_id: int                              # 실행 순서 (1부터 시작)
    algorithm_name: str                       # 실행할 알고리즘 이름
    description: str                          # 이 단계가 하는 일 설명
    input_spec: Dict[str, Any] = field(default_factory=dict)  # 입력 명세
    depends_on: List[int] = field(default_factory=list)       # 의존하는 step_id 목록

    def __post_init__(self):
        if self.input_spec is None:
            self.input_spec = {}
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class Plan:
    """전체 실행 계획."""

    steps: List[PlanStep]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.now().isoformat()
        if "total_steps" not in self.metadata:
            self.metadata["total_steps"] = len(self.steps)

    def get_step(self, step_id: int) -> Optional[PlanStep]:
        """step_id로 PlanStep을 찾아 반환."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_execution_order(self) -> List[PlanStep]:
        """의존성을 고려한 실행 순서 반환."""
        return sorted(self.steps, key=lambda s: s.step_id)
