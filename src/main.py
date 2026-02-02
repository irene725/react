from typing import Optional, List, Dict, Any

from .models import AnalysisReport
from .algorithms import LengthCheckAlgorithm, KeywordCheckAlgorithm
from .registry import AlgorithmRegistry
from .planner import Planner
from .judge import ReactJudge, MockReactJudge
from .executor import Executor
from .reporter import Reporter
from .logging_config import get_logger


logger = get_logger()


class TextAnalyzer:
    """텍스트 분석 에이전트의 메인 클래스.

    Plan-and-Execute 패턴과 ReAct Judge를 활용하여
    텍스트를 분석하고 문제 여부를 판단합니다.
    """

    def __init__(
        self,
        algorithm_order: Optional[List[str]] = None,
        use_llm_judge: bool = False,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        llm_api_key: Optional[str] = None,
        criteria_path: str = "src/criteria",
        early_exit_on_critical: bool = True,
        auto_save_report: bool = False,
        report_output_path: str = "report.md",
        auto_save_reasoning_trace: bool = False,
        reasoning_trace_path: str = "reasoning_trace.md"
    ):
        """
        Args:
            algorithm_order: 알고리즘 실행 순서
            use_llm_judge: LLM 기반 Judge 사용 여부 (False면 Mock Judge 사용)
            llm_provider: LLM 제공자 ("openai" 또는 "anthropic")
            llm_model: 사용할 모델 이름
            llm_api_key: API 키
            criteria_path: 판단 기준 문서 경로
            early_exit_on_critical: critical 문제 발견 시 조기 종료 여부
            auto_save_report: 분석 후 자동으로 리포트 파일 저장 여부
            report_output_path: 리포트 저장 경로 (auto_save_report=True일 때)
            auto_save_reasoning_trace: 상세 추론 과정 자동 저장 여부
            reasoning_trace_path: 추론 과정 저장 경로 (auto_save_reasoning_trace=True일 때)
        """
        # Registry 초기화 (싱글톤 리셋 후 새로 생성)
        AlgorithmRegistry.reset()
        self.registry = AlgorithmRegistry(criteria_path=criteria_path)

        # 기본 알고리즘 등록
        self._register_default_algorithms()

        # 컴포넌트 초기화
        self.algorithm_order = algorithm_order or ["length_check", "keyword_check"]

        self.planner = Planner(
            registry=self.registry,
            algorithm_order=self.algorithm_order
        )

        if use_llm_judge:
            self.judge = ReactJudge(
                registry=self.registry,
                llm_provider=llm_provider,
                model_name=llm_model,
                api_key=llm_api_key
            )
        else:
            self.judge = MockReactJudge(registry=self.registry)

        self.executor = Executor(
            registry=self.registry,
            judge=self.judge,
            early_exit_on_critical=early_exit_on_critical
        )

        self.reporter = Reporter()

        # 리포트 자동 저장 설정
        self.auto_save_report = auto_save_report
        self.report_output_path = report_output_path
        self.auto_save_reasoning_trace = auto_save_reasoning_trace
        self.reasoning_trace_path = reasoning_trace_path

    def _register_default_algorithms(self) -> None:
        """기본 알고리즘들을 등록."""
        self.registry.register(LengthCheckAlgorithm())
        self.registry.register(KeywordCheckAlgorithm())

    def analyze(
        self,
        text: str,
        input_specs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> AnalysisReport:
        """텍스트를 분석하고 리포트를 생성.

        Args:
            text: 분석할 텍스트
            input_specs: 각 알고리즘에 전달할 추가 입력 명세

        Returns:
            AnalysisReport: 분석 리포트
        """
        logger.info(f"Starting analysis for text of length {len(text)}")

        # 1. Plan 생성
        plan = self.planner.create_plan(text, input_specs)
        logger.info(f"Plan created with {len(plan.steps)} steps")

        # 2. Plan 실행
        execution_result = self.executor.execute(plan)
        logger.info(f"Execution completed with status: {execution_result.status}")

        # 3. 리포트 생성
        report = self.reporter.generate(execution_result)
        logger.info("Report generated")

        # 4. 자동 저장 (옵션)
        if self.auto_save_report:
            self.reporter.save_report(report, self.report_output_path)
            logger.info(f"Report automatically saved to {self.report_output_path}")

        # 5. 추론 과정 자동 저장 (옵션)
        if self.auto_save_reasoning_trace:
            self.reporter.save_reasoning_trace(report, self.reasoning_trace_path)
            logger.info(f"Reasoning trace automatically saved to {self.reasoning_trace_path}")

        return report

    def analyze_and_save(
        self,
        text: str,
        output_path: str,
        input_specs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> AnalysisReport:
        """텍스트를 분석하고 리포트를 파일로 저장.

        Args:
            text: 분석할 텍스트
            output_path: 리포트 저장 경로
            input_specs: 각 알고리즘에 전달할 추가 입력 명세

        Returns:
            AnalysisReport: 분석 리포트
        """
        report = self.analyze(text, input_specs)
        self.reporter.save_report(report, output_path)
        logger.info(f"Report saved to {output_path}")
        return report

    def get_registered_algorithms(self) -> List[str]:
        """등록된 알고리즘 목록을 반환."""
        return self.registry.list_algorithms()

    def register_algorithm(self, algorithm) -> None:
        """새 알고리즘을 등록.

        Args:
            algorithm: BaseAlgorithm을 상속한 알고리즘 인스턴스
        """
        self.registry.register(algorithm)
