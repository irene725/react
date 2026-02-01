"""Executor 테스트."""

import pytest
from src.algorithms import LengthCheckAlgorithm, KeywordCheckAlgorithm
from src.registry import AlgorithmRegistry
from src.planner import Planner
from src.judge import MockReactJudge
from src.executor import Executor


@pytest.fixture
def registry():
    """알고리즘이 등록된 레지스트리."""
    AlgorithmRegistry.reset()
    reg = AlgorithmRegistry(criteria_path="src/criteria")
    reg.register(LengthCheckAlgorithm())
    reg.register(KeywordCheckAlgorithm())
    return reg


@pytest.fixture
def judge(registry):
    """Mock Judge 인스턴스."""
    return MockReactJudge(registry)


@pytest.fixture
def planner(registry):
    """Planner 인스턴스."""
    return Planner(
        registry=registry,
        algorithm_order=["length_check", "keyword_check"]
    )


@pytest.fixture
def executor(registry, judge):
    """Executor 인스턴스."""
    return Executor(
        registry=registry,
        judge=judge,
        early_exit_on_critical=True
    )


class TestExecutor:
    """Executor 테스트."""

    def test_execute_all_pass(self, executor, planner):
        """모든 검사 통과."""
        text = "이것은 충분히 긴 정상적인 텍스트입니다. 문제가 없습니다."
        plan = planner.create_plan(text)

        result = executor.execute(plan)

        assert result.status == "all_passed"
        assert result.has_problem is False
        assert result.stopped_at is None
        assert result.executed_step_count == 2

    def test_execute_with_warning(self, executor, planner):
        """경고 발생 (계속 진행)."""
        text = "123456789"  # 9글자 - 최소 길이(10)보다 1자 부족 (10% 이내 = warning)
        plan = planner.create_plan(text)

        result = executor.execute(plan)

        # 경고가 있어도 계속 진행
        assert result.executed_step_count == 2

    def test_execute_early_exit_on_critical(self, executor, planner):
        """Critical 문제로 조기 종료."""
        text = "짧"  # 매우 짧은 텍스트
        plan = planner.create_plan(text)

        result = executor.execute(plan)

        assert result.status == "problem_found"
        assert result.has_problem is True
        assert result.stopped_at is not None
        assert result.stopped_at.algorithm_name == "length_check"
        assert result.executed_step_count == 1

    def test_execute_no_early_exit(self, registry, judge, planner):
        """조기 종료 비활성화."""
        executor = Executor(
            registry=registry,
            judge=judge,
            early_exit_on_critical=False
        )

        text = "짧"  # 매우 짧은 텍스트
        plan = planner.create_plan(text)

        result = executor.execute(plan)

        # 조기 종료 없이 모든 스텝 실행
        assert result.executed_step_count == 2
        assert result.stopped_at is None

    def test_execute_keyword_problem(self, executor, planner):
        """키워드 문제 발견."""
        text = "이것은 충분히 긴 텍스트이지만 광고와 스팸이 포함되어 있습니다."
        plan = planner.create_plan(text)

        result = executor.execute(plan)

        # 키워드가 2개라 critical이 되어 조기 종료
        assert result.status == "problem_found"
        assert result.has_problem is True

    def test_execute_single_algorithm(self, executor):
        """단일 알고리즘 실행."""
        result = executor.execute_single_algorithm(
            algorithm_name="length_check",
            text="테스트 텍스트입니다."
        )

        assert result.step.algorithm_name == "length_check"
        assert "raw_result" in result.execution_result

    def test_step_results_contain_judgments(self, executor, planner):
        """스텝 결과에 판단 포함."""
        text = "이것은 충분히 긴 정상적인 텍스트입니다."
        plan = planner.create_plan(text)

        result = executor.execute(plan)

        for step_result in result.step_results:
            assert step_result.judgment is not None
            assert hasattr(step_result.judgment, "has_problem")
            assert hasattr(step_result.judgment, "severity")
            assert hasattr(step_result.judgment, "reasoning")
