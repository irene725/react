"""텍스트 분석 에이전트 커스텀 예외 클래스."""


class TextAnalyzerError(Exception):
    """텍스트 분석기 기본 예외."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class AlgorithmError(TextAnalyzerError):
    """알고리즘 관련 예외."""
    pass


class AlgorithmNotFoundError(AlgorithmError):
    """알고리즘을 찾을 수 없을 때."""

    def __init__(self, algorithm_name: str):
        super().__init__(
            f"Algorithm '{algorithm_name}' not found",
            {"algorithm_name": algorithm_name}
        )
        self.algorithm_name = algorithm_name


class AlgorithmExecutionError(AlgorithmError):
    """알고리즘 실행 중 오류."""

    def __init__(self, algorithm_name: str, original_error: Exception):
        super().__init__(
            f"Failed to execute algorithm '{algorithm_name}': {original_error}",
            {"algorithm_name": algorithm_name, "original_error": str(original_error)}
        )
        self.algorithm_name = algorithm_name
        self.original_error = original_error


class AlgorithmRegistrationError(AlgorithmError):
    """알고리즘 등록 중 오류."""

    def __init__(self, algorithm_name: str, reason: str):
        super().__init__(
            f"Failed to register algorithm '{algorithm_name}': {reason}",
            {"algorithm_name": algorithm_name, "reason": reason}
        )
        self.algorithm_name = algorithm_name
        self.reason = reason


class JudgeError(TextAnalyzerError):
    """Judge 관련 예외."""
    pass


class JudgeEvaluationError(JudgeError):
    """Judge 평가 중 오류."""

    def __init__(self, algorithm_name: str, original_error: Exception):
        super().__init__(
            f"Judge evaluation failed for '{algorithm_name}': {original_error}",
            {"algorithm_name": algorithm_name, "original_error": str(original_error)}
        )
        self.algorithm_name = algorithm_name
        self.original_error = original_error


class JudgeResponseParseError(JudgeError):
    """Judge 응답 파싱 오류."""

    def __init__(self, response_text: str, original_error: Exception = None):
        super().__init__(
            "Failed to parse Judge response",
            {"response_preview": response_text[:200], "original_error": str(original_error) if original_error else None}
        )
        self.response_text = response_text
        self.original_error = original_error


class LLMError(TextAnalyzerError):
    """LLM API 관련 예외."""
    pass


class LLMConnectionError(LLMError):
    """LLM API 연결 오류."""

    def __init__(self, provider: str, original_error: Exception):
        super().__init__(
            f"Failed to connect to {provider} API: {original_error}",
            {"provider": provider, "original_error": str(original_error)}
        )
        self.provider = provider
        self.original_error = original_error


class LLMTimeoutError(LLMError):
    """LLM API 타임아웃."""

    def __init__(self, provider: str, timeout: int):
        super().__init__(
            f"{provider} API request timed out after {timeout}s",
            {"provider": provider, "timeout": timeout}
        )
        self.provider = provider
        self.timeout = timeout


class LLMRateLimitError(LLMError):
    """LLM API 속도 제한."""

    def __init__(self, provider: str, retry_after: int = None):
        msg = f"{provider} API rate limit exceeded"
        if retry_after:
            msg += f", retry after {retry_after}s"
        super().__init__(msg, {"provider": provider, "retry_after": retry_after})
        self.provider = provider
        self.retry_after = retry_after


class CriteriaError(TextAnalyzerError):
    """판단 기준 관련 예외."""
    pass


class CriteriaNotFoundError(CriteriaError):
    """판단 기준 문서를 찾을 수 없을 때."""

    def __init__(self, algorithm_name: str, criteria_path: str):
        super().__init__(
            f"Criteria document not found for '{algorithm_name}'",
            {"algorithm_name": algorithm_name, "criteria_path": criteria_path}
        )
        self.algorithm_name = algorithm_name
        self.criteria_path = criteria_path


class PlanError(TextAnalyzerError):
    """Plan 관련 예외."""
    pass


class InvalidPlanError(PlanError):
    """잘못된 Plan."""

    def __init__(self, reason: str):
        super().__init__(f"Invalid plan: {reason}", {"reason": reason})
        self.reason = reason


class ExecutionError(TextAnalyzerError):
    """실행 관련 예외."""
    pass


class StepExecutionError(ExecutionError):
    """스텝 실행 오류."""

    def __init__(self, step_id: int, algorithm_name: str, original_error: Exception):
        super().__init__(
            f"Step {step_id} ({algorithm_name}) execution failed: {original_error}",
            {"step_id": step_id, "algorithm_name": algorithm_name, "original_error": str(original_error)}
        )
        self.step_id = step_id
        self.algorithm_name = algorithm_name
        self.original_error = original_error


class InputValidationError(TextAnalyzerError):
    """입력 검증 오류."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Invalid input '{field}': {reason}",
            {"field": field, "reason": reason}
        )
        self.field = field
        self.reason = reason
