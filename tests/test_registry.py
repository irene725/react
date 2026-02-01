"""AlgorithmRegistry 테스트."""

import pytest
from src.algorithms import LengthCheckAlgorithm, KeywordCheckAlgorithm
from src.registry import AlgorithmRegistry


@pytest.fixture
def registry():
    """각 테스트마다 새로운 레지스트리 생성."""
    AlgorithmRegistry.reset()
    return AlgorithmRegistry(criteria_path="src/criteria")


class TestAlgorithmRegistry:
    """AlgorithmRegistry 테스트."""

    def test_register_algorithm(self, registry):
        """알고리즘 등록."""
        algo = LengthCheckAlgorithm()
        registry.register(algo)

        assert registry.has_algorithm("length_check")

    def test_register_duplicate_raises_error(self, registry):
        """중복 등록 시 에러."""
        algo1 = LengthCheckAlgorithm()
        algo2 = LengthCheckAlgorithm()

        registry.register(algo1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(algo2)

    def test_get_algorithm(self, registry):
        """알고리즘 조회."""
        algo = LengthCheckAlgorithm()
        registry.register(algo)

        retrieved = registry.get_algorithm("length_check")
        assert retrieved is algo

    def test_get_nonexistent_algorithm_raises_error(self, registry):
        """존재하지 않는 알고리즘 조회 시 에러."""
        with pytest.raises(KeyError, match="not registered"):
            registry.get_algorithm("nonexistent")

    def test_list_algorithms(self, registry):
        """알고리즘 목록 조회."""
        registry.register(LengthCheckAlgorithm())
        registry.register(KeywordCheckAlgorithm())

        algorithms = registry.list_algorithms()

        assert "length_check" in algorithms
        assert "keyword_check" in algorithms

    def test_get_criteria_document(self, registry):
        """판단 기준 문서 조회."""
        document = registry.get_criteria_document("length_check")

        assert "길이 체크" in document
        assert "판단 기준" in document

    def test_get_nonexistent_criteria_raises_error(self, registry):
        """존재하지 않는 판단 기준 문서 조회 시 에러."""
        with pytest.raises(FileNotFoundError):
            registry.get_criteria_document("nonexistent_algorithm")

    def test_unregister_algorithm(self, registry):
        """알고리즘 등록 해제."""
        algo = LengthCheckAlgorithm()
        registry.register(algo)

        assert registry.has_algorithm("length_check")

        registry.unregister("length_check")

        assert not registry.has_algorithm("length_check")

    def test_unregister_nonexistent_raises_error(self, registry):
        """존재하지 않는 알고리즘 해제 시 에러."""
        with pytest.raises(KeyError, match="not registered"):
            registry.unregister("nonexistent")

    def test_get_algorithm_info(self, registry):
        """알고리즘 정보 조회."""
        algo = LengthCheckAlgorithm()
        registry.register(algo)

        info = registry.get_algorithm_info("length_check")

        assert info["name"] == "length_check"
        assert "description" in info
