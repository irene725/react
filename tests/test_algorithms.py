"""알고리즘 테스트."""

import pytest
from src.algorithms import LengthCheckAlgorithm, KeywordCheckAlgorithm


class TestLengthCheckAlgorithm:
    """LengthCheckAlgorithm 테스트."""

    def test_text_within_range(self):
        """텍스트가 범위 내일 때."""
        algo = LengthCheckAlgorithm(min_length=10, max_length=100)
        result = algo.execute("이것은 테스트 텍스트입니다.")

        assert result["is_within_range"] is True
        assert result["length_diff"] == 0

    def test_text_too_short(self):
        """텍스트가 너무 짧을 때."""
        algo = LengthCheckAlgorithm(min_length=10, max_length=100)
        result = algo.execute("짧음")

        assert result["is_within_range"] is False
        assert result["raw_result"] == 2
        assert result["length_diff"] == 8

    def test_text_too_long(self):
        """텍스트가 너무 길 때."""
        algo = LengthCheckAlgorithm(min_length=1, max_length=5)
        result = algo.execute("매우 긴 텍스트입니다")

        assert result["is_within_range"] is False
        assert result["length_diff"] > 0

    def test_empty_text(self):
        """빈 텍스트."""
        algo = LengthCheckAlgorithm()
        result = algo.execute("")

        assert result["raw_result"] == 0
        assert result["is_within_range"] is False

    def test_name_property(self):
        """name 프로퍼티 확인."""
        algo = LengthCheckAlgorithm()
        assert algo.name == "length_check"


class TestKeywordCheckAlgorithm:
    """KeywordCheckAlgorithm 테스트."""

    def test_no_forbidden_keywords(self):
        """금지 키워드가 없을 때."""
        algo = KeywordCheckAlgorithm(forbidden_keywords=["금지", "위험"])
        result = algo.execute("이것은 정상적인 텍스트입니다.")

        assert result["has_forbidden_keywords"] is False
        assert result["keyword_count"] == 0
        assert result["raw_result"] == []

    def test_one_forbidden_keyword(self):
        """금지 키워드가 1개 있을 때."""
        algo = KeywordCheckAlgorithm(forbidden_keywords=["금지", "위험"])
        result = algo.execute("이 텍스트에는 금지된 내용이 있습니다.")

        assert result["has_forbidden_keywords"] is True
        assert result["keyword_count"] == 1
        assert "금지" in result["raw_result"]

    def test_multiple_forbidden_keywords(self):
        """금지 키워드가 여러 개 있을 때."""
        algo = KeywordCheckAlgorithm(forbidden_keywords=["금지", "위험"])
        result = algo.execute("금지된 내용과 위험한 내용이 있습니다.")

        assert result["has_forbidden_keywords"] is True
        assert result["keyword_count"] == 2

    def test_case_insensitive(self):
        """대소문자 구분 없이 검사."""
        algo = KeywordCheckAlgorithm(
            forbidden_keywords=["SPAM"],
            case_sensitive=False
        )
        result = algo.execute("This is spam content.")

        assert result["has_forbidden_keywords"] is True

    def test_case_sensitive(self):
        """대소문자 구분하여 검사."""
        algo = KeywordCheckAlgorithm(
            forbidden_keywords=["SPAM"],
            case_sensitive=True
        )
        result = algo.execute("This is spam content.")

        assert result["has_forbidden_keywords"] is False

    def test_keyword_positions(self):
        """키워드 위치 추적."""
        algo = KeywordCheckAlgorithm(forbidden_keywords=["금지"])
        result = algo.execute("금지된 내용 금지!")

        assert "금지" in result["keyword_positions"]
        positions = result["keyword_positions"]["금지"]
        assert len(positions) == 2  # 2번 출현

    def test_name_property(self):
        """name 프로퍼티 확인."""
        algo = KeywordCheckAlgorithm()
        assert algo.name == "keyword_check"
