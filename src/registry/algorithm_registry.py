from typing import Dict, List, Optional, Type
from pathlib import Path

from ..algorithms.base import BaseAlgorithm


class AlgorithmRegistry:
    """알고리즘을 등록하고 관리하는 레지스트리.

    싱글톤 패턴을 사용하여 애플리케이션 전체에서 하나의 인스턴스만 사용합니다.
    """

    _instance: Optional["AlgorithmRegistry"] = None
    _algorithms: Dict[str, BaseAlgorithm]
    _criteria_path: Path

    def __new__(cls, criteria_path: str = "src/criteria") -> "AlgorithmRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._algorithms = {}
            cls._instance._criteria_path = Path(criteria_path)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """레지스트리를 초기화합니다 (테스트용)."""
        cls._instance = None

    def register(self, algorithm: BaseAlgorithm) -> None:
        """알고리즘을 레지스트리에 등록.

        Args:
            algorithm: 등록할 알고리즘 인스턴스

        Raises:
            ValueError: 이미 동일한 이름의 알고리즘이 등록되어 있는 경우
        """
        name = algorithm.name
        if name in self._algorithms:
            raise ValueError(f"Algorithm '{name}' is already registered")
        self._algorithms[name] = algorithm

    def get_algorithm(self, name: str) -> BaseAlgorithm:
        """이름으로 알고리즘을 조회.

        Args:
            name: 알고리즘 이름

        Returns:
            등록된 알고리즘 인스턴스

        Raises:
            KeyError: 등록되지 않은 알고리즘인 경우
        """
        if name not in self._algorithms:
            raise KeyError(f"Algorithm '{name}' is not registered")
        return self._algorithms[name]

    def get_criteria_document(self, algorithm_name: str) -> str:
        """알고리즘에 대한 판단 기준 문서를 조회.

        Args:
            algorithm_name: 알고리즘 이름

        Returns:
            판단 기준 문서 내용 (Markdown)

        Raises:
            FileNotFoundError: 판단 기준 문서가 없는 경우
        """
        criteria_file = self._criteria_path / f"{algorithm_name}.md"
        if not criteria_file.exists():
            raise FileNotFoundError(
                f"Criteria document not found for algorithm '{algorithm_name}': {criteria_file}"
            )
        return criteria_file.read_text(encoding="utf-8")

    def list_algorithms(self) -> List[str]:
        """등록된 모든 알고리즘 이름 목록을 반환.

        Returns:
            알고리즘 이름 목록
        """
        return list(self._algorithms.keys())

    def has_algorithm(self, name: str) -> bool:
        """알고리즘이 등록되어 있는지 확인.

        Args:
            name: 알고리즘 이름

        Returns:
            등록 여부
        """
        return name in self._algorithms

    def unregister(self, name: str) -> None:
        """알고리즘을 레지스트리에서 제거.

        Args:
            name: 제거할 알고리즘 이름

        Raises:
            KeyError: 등록되지 않은 알고리즘인 경우
        """
        if name not in self._algorithms:
            raise KeyError(f"Algorithm '{name}' is not registered")
        del self._algorithms[name]

    def get_algorithm_info(self, name: str) -> Dict[str, str]:
        """알고리즘의 상세 정보를 반환.

        Args:
            name: 알고리즘 이름

        Returns:
            알고리즘 정보 딕셔너리 (name, description)
        """
        algorithm = self.get_algorithm(name)
        return {
            "name": algorithm.name,
            "description": algorithm.description
        }
