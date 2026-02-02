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

    def save_reasoning_trace(
        self,
        report: AnalysisReport,
        filepath: str
    ) -> None:
        """상세 추론 과정을 파일로 저장.

        Args:
            report: 분석 리포트
            filepath: 저장 경로
        """
        content = self._build_reasoning_trace_markdown(report.execution_result)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def _build_reasoning_trace_markdown(self, result: ExecutionResult) -> str:
        """상세 추론 과정을 Markdown으로 생성.

        Args:
            result: 실행 결과

        Returns:
            Markdown 문자열
        """
        lines = []

        # 헤더
        lines.append("# ReAct Judge 상세 추론 과정")
        lines.append("")
        lines.append(f"**생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("이 파일은 ReAct Judge Agent가 각 알고리즘 결과를 평가하는 과정을 상세히 보여줍니다.")
        lines.append("")

        # 각 단계별 추론 과정
        for step_result in result.step_results:
            lines.append("")
            lines.append("=" * 80)
            lines.append("")
            lines.append(f"## Step {step_result.step.step_id}: {step_result.step.algorithm_name}")
            lines.append("")
            lines.append(f"**알고리즘**: {step_result.step.algorithm_name}")
            lines.append(f"**설명**: {step_result.step.description}")
            lines.append("")

            # 실행 결과
            lines.append("### 알고리즘 실행 결과")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(step_result.execution_result, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")

            # 상세 추론 과정
            if step_result.judgment.detailed_trace:
                lines.append("### ReAct 추론 과정")
                lines.append("")

                for trace_item in step_result.judgment.detailed_trace:
                    iteration = trace_item["iteration"]
                    lines.append(f"#### 🔄 Iteration {iteration}")
                    lines.append("")

                    # Thought
                    if trace_item["thought"]:
                        lines.append(f"**💭 Thought:**")
                        lines.append("")
                        lines.append(f"> {trace_item['thought']}")
                        lines.append("")

                    # Action
                    if trace_item["action"]:
                        lines.append(f"**🔧 Action:** `{trace_item['action']}`")
                        lines.append("")

                        # Action Input
                        if trace_item["action_input"]:
                            lines.append("**📥 Action Input:**")
                            lines.append("")
                            if isinstance(trace_item["action_input"], (dict, list)):
                                lines.append("```json")
                                lines.append(json.dumps(trace_item["action_input"], ensure_ascii=False, indent=2))
                                lines.append("```")
                            else:
                                lines.append(f"```\n{trace_item['action_input']}\n```")
                            lines.append("")

                    # Observation
                    if trace_item["observation"]:
                        lines.append("**👁️ Observation:**")
                        lines.append("")
                        obs_text = trace_item["observation"]
                        # 긴 observation은 요약
                        if len(obs_text) > 500:
                            lines.append("<details>")
                            lines.append("<summary>결과 보기 (긴 내용)</summary>")
                            lines.append("")
                            lines.append("```")
                            lines.append(obs_text)
                            lines.append("```")
                            lines.append("")
                            lines.append("</details>")
                        else:
                            lines.append("```")
                            lines.append(obs_text)
                            lines.append("```")
                        lines.append("")

                    # Full LLM Response - 긴 경우만 접기
                    if trace_item["llm_response"]:
                        llm_resp = trace_item["llm_response"]
                        if len(llm_resp) > 300:
                            lines.append("<details>")
                            lines.append("<summary>📝 전체 LLM 응답 보기</summary>")
                            lines.append("")
                            lines.append("```")
                            lines.append(llm_resp)
                            lines.append("```")
                            lines.append("")
                            lines.append("</details>")
                        lines.append("")

                    lines.append("")

            # 최종 판단
            lines.append("### ✅ 최종 판단")
            lines.append("")
            severity_icon = {
                "none": "✅",
                "warning": "⚠️",
                "critical": "🚨"
            }.get(step_result.judgment.severity, "❓")
            lines.append(f"**판단**: {severity_icon} {step_result.judgment.severity.upper()}")
            lines.append(f"**문제 발견**: {'예' if step_result.judgment.has_problem else '아니오'}")
            lines.append("")
            lines.append(f"**추론**:")
            lines.append("")
            lines.append(f"> {step_result.judgment.reasoning}")
            lines.append("")
            lines.append(f"**요약**: {step_result.judgment.summary}")
            lines.append("")
            lines.append("")

        return "\n".join(lines)
