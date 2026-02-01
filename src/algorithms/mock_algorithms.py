from typing import Any, Dict, List
from .base import BaseAlgorithm


class LengthCheckAlgorithm(BaseAlgorithm):
    """텍스트 길이를 체크하는 알고리즘.

    텍스트의 길이가 지정된 범위 내에 있는지 검사합니다.
    """

    def __init__(self, min_length: int = 10, max_length: int = 10000):
        """
        Args:
            min_length: 최소 허용 길이 (기본값: 10)
            max_length: 최대 허용 길이 (기본값: 10000)
        """
        self.min_length = min_length
        self.max_length = max_length

    @property
    def name(self) -> str:
        return "length_check"

    @property
    def description(self) -> str:
        return f"텍스트 길이가 {self.min_length}~{self.max_length}자 범위 내에 있는지 검사"

    def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """텍스트 길이를 검사.

        Returns:
            Dict containing:
                - raw_result: 텍스트 길이
                - is_within_range: 범위 내 여부
                - min_length: 설정된 최소 길이
                - max_length: 설정된 최대 길이
                - length_diff: 범위와의 차이 (범위 내면 0)
        """
        if not self.validate_input(text):
            return {
                "raw_result": 0,
                "is_within_range": False,
                "error": "Invalid input text"
            }

        length = len(text)
        is_within_range = self.min_length <= length <= self.max_length

        length_diff = 0
        if length < self.min_length:
            length_diff = self.min_length - length
        elif length > self.max_length:
            length_diff = length - self.max_length

        return {
            "raw_result": length,
            "is_within_range": is_within_range,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "length_diff": length_diff
        }


class KeywordCheckAlgorithm(BaseAlgorithm):
    """금지 키워드를 체크하는 알고리즘.

    텍스트에 금지된 키워드가 포함되어 있는지 검사합니다.
    """

    DEFAULT_FORBIDDEN_KEYWORDS: List[str] = [
        "욕설",
        "비속어",
        "금지어",
        "스팸",
        "광고",
    ]

    def __init__(self, forbidden_keywords: List[str] = None, case_sensitive: bool = False):
        """
        Args:
            forbidden_keywords: 금지 키워드 목록 (None이면 기본 목록 사용)
            case_sensitive: 대소문자 구분 여부 (기본값: False)
        """
        self.forbidden_keywords = forbidden_keywords or self.DEFAULT_FORBIDDEN_KEYWORDS
        self.case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        return "keyword_check"

    @property
    def description(self) -> str:
        return "텍스트에 금지된 키워드가 포함되어 있는지 검사"

    def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """금지 키워드 존재 여부를 검사.

        Returns:
            Dict containing:
                - raw_result: 발견된 금지 키워드 목록
                - has_forbidden_keywords: 금지 키워드 발견 여부
                - keyword_count: 발견된 키워드 수
                - keyword_positions: 각 키워드의 발견 위치
        """
        if not self.validate_input(text):
            return {
                "raw_result": [],
                "has_forbidden_keywords": False,
                "error": "Invalid input text"
            }

        search_text = text if self.case_sensitive else text.lower()
        found_keywords = []
        keyword_positions = {}

        for keyword in self.forbidden_keywords:
            search_keyword = keyword if self.case_sensitive else keyword.lower()
            position = search_text.find(search_keyword)

            if position != -1:
                found_keywords.append(keyword)
                # 모든 출현 위치 찾기
                positions = []
                start = 0
                while True:
                    pos = search_text.find(search_keyword, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
                keyword_positions[keyword] = positions

        return {
            "raw_result": found_keywords,
            "has_forbidden_keywords": len(found_keywords) > 0,
            "keyword_count": len(found_keywords),
            "keyword_positions": keyword_positions,
            "checked_keywords": self.forbidden_keywords
        }
