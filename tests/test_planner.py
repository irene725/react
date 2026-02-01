"""Planner 테스트."""

import pytest
from src.algorithms import LengthCheckAlgorithm, KeywordCheckAlgorithm
from src.registry import AlgorithmRegistry
from src.planner import Planner


@pytest.fixture
def registry():
    """알고리즘이 등록된 레지스트리."""
    AlgorithmRegistry.reset()
    reg = AlgorithmRegistry(criteria_path="src/criteria")
    reg.register(LengthCheckAlgorithm())
    reg.register(KeywordCheckAlgorithm())
    return reg


@pytest.fixture
def planner(registry):
    """Planner 인스턴스."""
    return Planner(
        registry=registry,
        algorithm_order=["length_check", "keyword_check"]
    )


class TestPlanner:
    """Planner 테스트."""

    def test_create_plan(self, planner):
        """Plan 생성."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        assert len(plan.steps) == 2
        assert plan.steps[0].algorithm_name == "length_check"
        assert plan.steps[1].algorithm_name == "keyword_check"

    def test_plan_step_ids(self, planner):
        """스텝 ID 순서."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        assert plan.steps[0].step_id == 1
        assert plan.steps[1].step_id == 2

    def test_plan_dependencies(self, planner):
        """스텝 의존성."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        assert plan.steps[0].depends_on == []
        assert plan.steps[1].depends_on == [1]

    def test_plan_input_spec_contains_text(self, planner):
        """입력 명세에 텍스트 포함."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        for step in plan.steps:
            assert "text" in step.input_spec
            assert step.input_spec["text"] == text

    def test_plan_with_custom_input_specs(self, planner):
        """커스텀 입력 명세."""
        text = "테스트 텍스트입니다."
        input_specs = {
            "length_check": {"min_length": 5}
        }

        plan = planner.create_plan(text, input_specs)

        assert plan.steps[0].input_spec["min_length"] == 5

    def test_plan_metadata(self, planner):
        """Plan 메타데이터."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        assert "created_at" in plan.metadata
        assert plan.metadata["text_length"] == len(text)
        assert plan.metadata["algorithm_count"] == 2

    def test_validate_valid_plan(self, planner):
        """유효한 Plan 검증."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        assert planner.validate_plan(plan) is True

    def test_get_execution_order(self, planner):
        """실행 순서 조회."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        order = plan.get_execution_order()

        assert order[0].step_id == 1
        assert order[1].step_id == 2

    def test_get_step(self, planner):
        """스텝 조회."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        step = plan.get_step(1)

        assert step is not None
        assert step.algorithm_name == "length_check"

    def test_get_nonexistent_step(self, planner):
        """존재하지 않는 스텝 조회."""
        text = "테스트 텍스트입니다."
        plan = planner.create_plan(text)

        step = plan.get_step(999)

        assert step is None
