"""TextAnalyzer 통합 테스트."""

import pytest
import os
import tempfile
from src import TextAnalyzer


class TestTextAnalyzer:
    """TextAnalyzer 통합 테스트."""

    def test_analyze_normal_text(self):
        """정상 텍스트 분석."""
        analyzer = TextAnalyzer()
        text = "이것은 충분히 긴 정상적인 텍스트입니다. 특별한 문제가 없습니다."

        report = analyzer.analyze(text)

        assert report.status == "all_passed"
        assert report.has_problem is False

    def test_analyze_short_text(self):
        """짧은 텍스트 분석."""
        analyzer = TextAnalyzer()
        text = "짧"

        report = analyzer.analyze(text)

        assert report.has_problem is True
        assert report.stopped_at_algorithm == "length_check"

    def test_analyze_with_forbidden_keywords(self):
        """금지 키워드 포함 텍스트."""
        analyzer = TextAnalyzer()
        text = "이 텍스트는 충분히 길지만 광고와 스팸 키워드가 있습니다."

        report = analyzer.analyze(text)

        assert report.has_problem is True

    def test_report_content_is_markdown(self):
        """리포트 내용이 Markdown 형식."""
        analyzer = TextAnalyzer()
        text = "이것은 테스트 텍스트입니다. 충분히 긴 내용입니다."

        report = analyzer.analyze(text)

        assert "# 텍스트 분석 리포트" in report.report_content
        assert "## 요약" in report.report_content

    def test_analyze_and_save(self):
        """리포트 파일 저장."""
        analyzer = TextAnalyzer()
        text = "이것은 테스트 텍스트입니다. 충분히 긴 내용입니다."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            report = analyzer.analyze_and_save(text, output_path)

            assert os.path.exists(output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "# 텍스트 분석 리포트" in content
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_get_registered_algorithms(self):
        """등록된 알고리즘 목록."""
        analyzer = TextAnalyzer()

        algorithms = analyzer.get_registered_algorithms()

        assert "length_check" in algorithms
        assert "keyword_check" in algorithms

    def test_custom_algorithm_order(self):
        """커스텀 알고리즘 순서."""
        analyzer = TextAnalyzer(algorithm_order=["keyword_check", "length_check"])
        text = "이것은 테스트 텍스트입니다. 충분히 긴 내용입니다."

        report = analyzer.analyze(text)

        # 첫 번째 실행된 알고리즘이 keyword_check
        first_step = report.step_results[0]
        assert first_step.step.algorithm_name == "keyword_check"

    def test_early_exit_disabled(self):
        """조기 종료 비활성화."""
        analyzer = TextAnalyzer(early_exit_on_critical=False)
        text = "짧"

        report = analyzer.analyze(text)

        # 조기 종료 없이 모든 알고리즘 실행
        assert report.execution_result.executed_step_count == 2

    def test_step_results_available(self):
        """단계별 결과 접근."""
        analyzer = TextAnalyzer()
        text = "이것은 충분히 긴 정상적인 텍스트입니다."

        report = analyzer.analyze(text)

        assert len(report.step_results) == 2

        for step_result in report.step_results:
            assert step_result.execution_result is not None
            assert step_result.judgment is not None
