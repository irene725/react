"""Text Analysis Agent System."""

__version__ = "0.1.0"

from .main import TextAnalyzer
from .models import (
    PlanStep,
    Plan,
    StepResult,
    JudgmentResult,
    ExecutionResult,
    AnalysisReport,
)
from .algorithms import BaseAlgorithm, LengthCheckAlgorithm, KeywordCheckAlgorithm
from .registry import AlgorithmRegistry
from .planner import Planner
from .judge import ReactJudge, MockReactJudge
from .executor import Executor
from .reporter import Reporter
from .exceptions import (
    TextAnalyzerError,
    AlgorithmError,
    AlgorithmNotFoundError,
    AlgorithmExecutionError,
    AlgorithmRegistrationError,
    JudgeError,
    JudgeEvaluationError,
    JudgeResponseParseError,
    LLMError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    CriteriaError,
    CriteriaNotFoundError,
    PlanError,
    InvalidPlanError,
    ExecutionError,
    StepExecutionError,
    InputValidationError,
)

__all__ = [
    "TextAnalyzer",
    "PlanStep",
    "Plan",
    "StepResult",
    "JudgmentResult",
    "ExecutionResult",
    "AnalysisReport",
    "BaseAlgorithm",
    "LengthCheckAlgorithm",
    "KeywordCheckAlgorithm",
    "AlgorithmRegistry",
    "Planner",
    "ReactJudge",
    "MockReactJudge",
    "Executor",
    "Reporter",
    # Exceptions
    "TextAnalyzerError",
    "AlgorithmError",
    "AlgorithmNotFoundError",
    "AlgorithmExecutionError",
    "AlgorithmRegistrationError",
    "JudgeError",
    "JudgeEvaluationError",
    "JudgeResponseParseError",
    "LLMError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "CriteriaError",
    "CriteriaNotFoundError",
    "PlanError",
    "InvalidPlanError",
    "ExecutionError",
    "StepExecutionError",
    "InputValidationError",
]
