import json
from datetime import datetime
from typing import Optional

from ..models import ExecutionResult, AnalysisReport, StepResult


class Reporter:
    """분석 결과를 Markdown 리포트로 생성하는 Reporter."""

    def generate(self, execution_result: ExecutionResult) -> AnalysisReport:
        """실행 결과로부터 분석 리포트를 생성.

        Args:
            execution_result: Executor의 실행 결과

        Returns:
            AnalysisReport: 생성된 분석 리포트
        """
        report_content = self._build_markdown_report(execution_result)

        return AnalysisReport(
            execution_result=execution_result,
            report_content=report_content
        )

    def _build_markdown_report(self, result: ExecutionResult) -> str:
        """Markdown 형식의 리포트를 생성.

        Args:
            result: 실행 결과

        Returns:
            Markdown 문자열
        """
        lines = []

        # 헤더
        lines.append("# 텍스트 분석 리포트")
        lines.append("")
        lines.append(f"**생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 요약
        lines.append("## 요약")
        lines.append("")
        lines.append(self._get_summary_section(result))
        lines.append("")

        # 실행 정보
        lines.append("## 실행 정보")
        lines.append("")
        lines.append(f"- **전체 단계 수**: {result.total_step_count}")
        lines.append(f"- **실행된 단계 수**: {result.executed_step_count}")
        lines.append(f"- **상태**: {self._format_status(result.status)}")

        if result.stopped_at:
            lines.append(f"- **조기 종료**: Step {result.stopped_at.step_id} ({result.stopped_at.algorithm_name})에서 중단됨")
        lines.append("")

        # 단계별 결과
        lines.append("## 단계별 분석 결과")
        lines.append("")

        for step_result in result.step_results:
            lines.append(self._format_step_result(step_result))
            lines.append("")

        # 결론
        lines.append("## 결론")
        lines.append("")
        lines.append(self._get_conclusion(result))

        return "\n".join(lines)

    def _get_summary_section(self, result: ExecutionResult) -> str:
        """요약 섹션 생성."""
        if result.has_problem:
            problem_count = sum(
                1 for sr in result.step_results if sr.judgment.has_problem
            )
            critical_count = sum(
                1 for sr in result.step_results
                if sr.judgment.severity == "critical"
            )
            warning_count = sum(
                1 for sr in result.step_results
                if sr.judgment.severity == "warning"
            )

            summary = f"🚨 **{problem_count}개의 문제가 발견되었습니다.**\n"
            if critical_count > 0:
                summary += f"- Critical: {critical_count}개\n"
            if warning_count > 0:
                summary += f"- Warning: {warning_count}개"

            return summary
        else:
            return "✅ **모든 검사를 통과했습니다.** 발견된 문제가 없습니다."

    def _format_status(self, status: str) -> str:
        """상태 포맷팅."""
        status_map = {
            "all_passed": "✅ 모두 통과",
            "problem_found": "🚨 문제 발견"
        }
        return status_map.get(status, status)

    def _format_step_result(self, step_result: StepResult) -> str:
        """단일 스텝 결과 포맷팅."""
        step = step_result.step
        judgment = step_result.judgment

        severity_icon = {
            "none": "✅",
            "warning": "⚠️",
            "critical": "🚨"
        }.get(judgment.severity, "❓")

        lines = [
            f"### Step {step.step_id}: {step.algorithm_name}",
            "",
            f"**설명**: {step.description}",
            "",
            f"**판단 결과**: {severity_icon} {judgment.severity.upper()}",
            "",
            "**상세 분석**:",
            "",
            f"> {judgment.reasoning}",
            "",
            f"**요약**: {judgment.summary}",
            "",
            "<details>",
            "<summary>실행 결과 상세</summary>",
            "",
            "```json",
            json.dumps(step_result.execution_result, ensure_ascii=False, indent=2),
            "```",
            "",
            "</details>"
        ]

        return "\n".join(lines)

    def _get_conclusion(self, result: ExecutionResult) -> str:
        """결론 섹션 생성."""
        if not result.has_problem:
            return (
                "분석 대상 텍스트는 모든 검사 기준을 충족합니다. "
                "추가적인 조치가 필요하지 않습니다."
            )

        conclusions = []

        if result.stopped_at:
            conclusions.append(
                f"**조기 종료**: '{result.stopped_at.algorithm_name}' 검사에서 "
                f"심각한 문제가 발견되어 분석이 중단되었습니다. "
                f"나머지 {result.total_step_count - result.executed_step_count}개의 "
                "검사는 실행되지 않았습니다."
            )

        # 문제가 있는 단계들의 요약 추출
        for sr in result.step_results:
            if sr.judgment.has_problem:
                conclusions.append(
                    f"- **{sr.step.algorithm_name}**: {sr.judgment.summary}"
                )

        conclusions.append("\n**권장 조치**: 위에서 발견된 문제들을 검토하고 수정하시기 바랍니다.")

        return "\n".join(conclusions)

    def save_report(
        self,
        report: AnalysisReport,
        filepath: str
    ) -> None:
        """리포트를 파일로 저장.

        Args:
            report: 저장할 리포트
            filepath: 저장 경로
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report.report_content)
