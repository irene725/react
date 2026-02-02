"""텍스트 분석 에이전트 실행 예제.

이 예제는 TextAnalyzer를 사용하여 텍스트를 분석하는 방법을 보여줍니다.
"""

import sys
import os
from src.logging_config import setup_logging

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import TextAnalyzer


# 로깅 설정
setup_logging(                                                                                             
      level="DEBUG",           # or "INFO" for less verbose                                                  
      debug_mode=True,         # Enables detailed format with file:line                                      
      enable_color=True,       # Colored output                                                              
      log_file="logs/analysis.log"  # Optional: also save to file                                            
  )    


def example_1_normal_text(analyzer: TextAnalyzer):
    """정상 텍스트 분석 예제 (모든 검사 통과)."""
    print("\n" + "=" * 60)
    print("예제 1: 정상 텍스트 분석")
    print("=" * 60)

    text = """
    안녕하세요. 이것은 정상적인 텍스트입니다.
    특별한 문제가 없는 일반적인 내용을 담고 있습니다.
    텍스트 분석 시스템이 이 텍스트를 검사하면
    모든 검사를 통과할 것으로 예상됩니다.
    """

    report = analyzer.analyze(text.strip())

    print("\n--- 분석 결과 ---")
    print(f"상태: {report.status}")
    print(f"문제 발견: {report.has_problem}")
    print("\n--- 리포트 ---")
    print(report.report_content)


def example_2_short_text(analyzer: TextAnalyzer):
    """짧은 텍스트 분석 예제 (길이 체크 실패)."""
    print("\n" + "=" * 60)
    print("예제 2: 짧은 텍스트 분석 (길이 체크 실패)")
    print("=" * 60)

    text = "짧음"  # 최소 길이 미달

    report = analyzer.analyze(text)

    print("\n--- 분석 결과 ---")
    print(f"상태: {report.status}")
    print(f"문제 발견: {report.has_problem}")
    print("\n--- 리포트 ---")
    print(report.report_content)


def example_3_forbidden_keywords(analyzer: TextAnalyzer):
    """금지 키워드 포함 텍스트 분석 예제."""
    print("\n" + "=" * 60)
    print("예제 3: 금지 키워드 포함 텍스트 분석")
    print("=" * 60)

    text = """
    이 텍스트는 충분히 긴 내용을 가지고 있습니다.
    하지만 광고와 스팸 같은 금지 키워드가 포함되어 있어서
    키워드 체크에서 문제가 발생할 것입니다.
    """

    report = analyzer.analyze(text.strip())

    print("\n--- 분석 결과 ---")
    print(f"상태: {report.status}")
    print(f"문제 발견: {report.has_problem}")
    print(f"조기 종료 알고리즘: {report.stopped_at_algorithm}")
    print("\n--- 리포트 ---")
    print(report.report_content)


def example_4_early_exit(analyzer: TextAnalyzer):
    """조기 종료 예제 (Critical 문제 발견 시 중단)."""
    print("\n" + "=" * 60)
    print("예제 4: 조기 종료 (매우 짧은 텍스트)")
    print("=" * 60)

    text = "짧"  # 매우 짧은 텍스트 - critical로 판단됨

    report = analyzer.analyze(text)

    print("\n--- 분석 결과 ---")
    print(f"상태: {report.status}")
    print(f"문제 발견: {report.has_problem}")
    print(f"실행된 단계: {report.execution_result.executed_step_count}/{report.execution_result.total_step_count}")
    print(f"조기 종료 알고리즘: {report.stopped_at_algorithm}")
    print("\n--- 리포트 ---")
    print(report.report_content)


def example_5_custom_settings(analyzer: TextAnalyzer):
    """커스텀 설정 예제."""
    print("\n" + "=" * 60)
    print("예제 5: 커스텀 설정으로 분석")
    print("=" * 60)

    text = "이것은 20자 이상의 텍스트입니다."

    # 커스텀 입력 명세: 최소 길이를 20으로 설정
    input_specs = {
        "length_check": {
            "min_length": 20,
            "max_length": 100
        }
    }

    report = analyzer.analyze(text, input_specs=input_specs)

    print("\n--- 분석 결과 ---")
    print(f"상태: {report.status}")
    print(f"문제 발견: {report.has_problem}")
    print("\n--- 리포트 ---")
    print(report.report_content)


def example_6_save_report(analyzer: TextAnalyzer):
    """리포트를 파일로 저장하는 예제."""
    print("\n" + "=" * 60)
    print("예제 6: 리포트 파일 저장")
    print("=" * 60)

    text = """
    이 텍스트는 분석 후 리포트가 파일로 저장됩니다.
    저장된 파일은 Markdown 형식으로 되어 있어
    다양한 도구에서 읽을 수 있습니다.
    """

    output_path = "examples/analysis_report.md"
    report = analyzer.analyze_and_save(text.strip(), output_path)

    print(f"\n리포트가 '{output_path}'에 저장되었습니다.")
    print(f"상태: {report.status}")


if __name__ == "__main__":
    print("텍스트 분석 에이전트 예제")
    print("=" * 60)

    # Analyzer 초기화 (LLM Judge 사용)
    analyzer = TextAnalyzer(use_llm_judge=True)

    # 모든 예제 실행
    example_1_normal_text(analyzer)
    # example_2_short_text(analyzer)
    # example_3_forbidden_keywords(analyzer)
    #
    # # Example 4는 early_exit_on_critical=True가 필요한 경우 별도 analyzer 사용
    # analyzer_with_early_exit = TextAnalyzer(use_llm_judge=True, early_exit_on_critical=True)
    # example_4_early_exit(analyzer_with_early_exit)
    #
    # example_5_custom_settings(analyzer)
    # example_6_save_report(analyzer)

    print("\n" + "=" * 60)
    print("모든 예제 실행 완료!")
    print("=" * 60)
