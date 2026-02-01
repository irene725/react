from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAlgorithm(ABC):
    """알고리즘의 기본 추상 클래스.

    모든 분석 알고리즘은 이 클래스를 상속받아 구현해야 합니다.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """알고리즘의 고유 이름."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """알고리즘에 대한 설명."""
        pass

    @abstractmethod
    def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """알고리즘을 실행하고 결과를 반환.

        Args:
            text: 분석할 텍스트
            **kwargs: 추가 파라미터

        Returns:
            Dict[str, Any]: 알고리즘 실행 결과
                - 반드시 'raw_result' 키를 포함해야 함
                - 기타 알고리즘별 추가 데이터 포함 가능
        """
        pass

    def validate_input(self, text: str) -> bool:
        """입력 텍스트의 유효성을 검증.

        Args:
            text: 검증할 텍스트

        Returns:
            bool: 유효한 경우 True
        """
        return text is not None and isinstance(text, str)
