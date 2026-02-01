import logging
from typing import Union, Optional, List

from ..models import Plan, PlanStep, StepResult, ExecutionResult, JudgmentResult
from ..registry import AlgorithmRegistry
from ..judge import ReactJudge, MockReactJudge
from ..exceptions import (
    AlgorithmExecutionError,
    JudgeEvaluationError,
    StepExecutionError,
)


logger = logging.getLogger(__name__)


class Executor:
    """Plan에 따라 알고리즘을 순차 실행하는 Executor.

    각 알고리즘 실행 후 Judge를 호출하여 결과를 판단하고,
    심각한 문제 발견 시 조기 종료합니다.
    """

    def __init__(
        self,
        registry: AlgorithmRegistry,
        judge: Union[ReactJudge, MockReactJudge],
        early_exit_on_critical: bool = True
    ):
        """
        Args:
            registry: 알고리즘 레지스트리
            judge: 판단을 수행할 Judge 인스턴스
            early_exit_on_critical: critical 판정 시 조기 종료 여부
        """
        self.registry = registry
        self.judge = judge
        self.early_exit_on_critical = early_exit_on_critical

    def execute(self, plan: Plan) -> ExecutionResult:
        """Plan을 실행하고 결과를 반환.

        Args:
            plan: 실행할 계획

        Returns:
            ExecutionResult: 실행 결과
        """
        step_results: List[StepResult] = []
        stopped_at: Optional[PlanStep] = None
        status = "all_passed"

        execution_order = plan.get_execution_order()
        logger.info(f"Starting execution with {len(execution_order)} steps")

        for step in execution_order:
            logger.info(f"Executing step {step.step_id}: {step.algorithm_name}")

            # 알고리즘 실행
            step_result = self._execute_step(step)
            step_results.append(step_result)

            # 판단 결과 확인
            judgment = step_result.judgment

            logger.info(
                f"Step {step.step_id} judgment: "
                f"has_problem={judgment.has_problem}, "
                f"severity={judgment.severity}"
            )

            if judgment.has_problem:
                if judgment.severity == "critical" and self.early_exit_on_critical:
                    logger.warning(
                        f"Critical problem found at step {step.step_id}. "
                        f"Early exit triggered."
                    )
                    stopped_at = step
                    status = "problem_found"
                    break
                elif judgment.severity == "warning":
                    # 경고는 기록하되 계속 진행
                    logger.warning(
                        f"Warning at step {step.step_id}: {judgment.summary}"
                    )

        # 모든 스텝 완료 후 문제 발견 여부 최종 확인
        if status == "all_passed":
            for result in step_results:
                if result.judgment.has_problem:
                    status = "problem_found"
                    break

        return ExecutionResult(
            plan=plan,
            step_results=step_results,
            status=status,
            stopped_at=stopped_at
        )

    def _execute_step(self, step: PlanStep) -> StepResult:
        """단일 스텝을 실행.

        Args:
            step: 실행할 스텝

        Returns:
            StepResult: 스텝 실행 결과

        Raises:
            StepExecutionError: 스텝 실행 중 복구 불가능한 오류 발생 시
        """
        algorithm = self.registry.get_algorithm(step.algorithm_name)

        # 입력 명세에서 텍스트와 추가 파라미터 추출
        input_spec = step.input_spec.copy()
        text = input_spec.pop("text", "")

        # 알고리즘 실행
        algorithm_error = None
        try:
            execution_result = algorithm.execute(text, **input_spec)
        except Exception as e:
            algorithm_error = AlgorithmExecutionError(step.algorithm_name, e)
            logger.error(f"Algorithm execution failed: {algorithm_error}")
            execution_result = {
                "raw_result": None,
                "error": str(e),
                "error_type": type(e).__name__,
                "success": False
            }

        # Judge 호출
        try:
            judgment = self.judge.evaluate(
                algorithm_name=step.algorithm_name,
                execution_result=execution_result
            )
        except Exception as e:
            judge_error = JudgeEvaluationError(step.algorithm_name, e)
            logger.error(f"Judge evaluation failed: {judge_error}")
            judgment = JudgmentResult(
                algorithm_name=step.algorithm_name,
                has_problem=False,
                severity="none",
                reasoning=f"Judge evaluation failed: {e}",
                summary="Could not evaluate result"
            )

        return StepResult(
            step=step,
            execution_result=execution_result,
            judgment=judgment
        )

    def execute_single_algorithm(
        self,
        algorithm_name: str,
        text: str,
        **kwargs
    ) -> StepResult:
        """단일 알고리즘만 실행하고 결과를 반환.

        Args:
            algorithm_name: 알고리즘 이름
            text: 분석할 텍스트
            **kwargs: 알고리즘에 전달할 추가 파라미터

        Returns:
            StepResult: 실행 결과
        """
        step = PlanStep(
            step_id=1,
            algorithm_name=algorithm_name,
            description=f"Execute {algorithm_name}",
            input_spec={"text": text, **kwargs}
        )
        return self._execute_step(step)
