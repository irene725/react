"""텍스트 분석 에이전트 로깅 설정."""

import logging
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime


# 로거 이름 상수
LOGGER_NAME = "text_analyzer"
JUDGE_LOGGER_NAME = "text_analyzer.judge"
EXECUTOR_LOGGER_NAME = "text_analyzer.executor"
PLANNER_LOGGER_NAME = "text_analyzer.planner"


class ColoredFormatter(logging.Formatter):
    """컬러 출력을 지원하는 로그 포매터."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # 레벨 이름에 색상 적용
        record.levelname = f"{log_color}{record.levelname}{reset}"
        return super().format(record)


class JudgeReasoningFilter(logging.Filter):
    """Judge reasoning 로그만 필터링."""

    def filter(self, record):
        return hasattr(record, "reasoning") or "reasoning" in record.getMessage().lower()


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_judge_reasoning: bool = True,
    enable_color: bool = True,
    debug_mode: bool = False
) -> logging.Logger:
    """로깅을 설정합니다.

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 파일 로깅 비활성화)
        log_judge_reasoning: Judge reasoning 로그 활성화 여부
        enable_color: 콘솔 컬러 출력 활성화 여부
        debug_mode: 디버그 모드 (DEBUG 레벨 + 상세 포맷)

    Returns:
        설정된 루트 로거
    """
    # 디버그 모드면 레벨 오버라이드
    if debug_mode:
        level = "DEBUG"

    # 루트 로거 가져오기
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper()))

    # 기존 핸들러 제거
    logger.handlers = []

    # 포맷 설정
    if debug_mode:
        log_format = "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
    else:
        log_format = "%(asctime)s | %(levelname)s | %(message)s"

    date_format = "%Y-%m-%d %H:%M:%S"

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if enable_color and sys.stdout.isatty():
        console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        console_formatter = logging.Formatter(log_format, datefmt=date_format)

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # 파일에는 모든 레벨 기록
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Judge 로거 설정
    judge_logger = logging.getLogger(JUDGE_LOGGER_NAME)
    judge_logger.setLevel(logging.DEBUG if log_judge_reasoning else logging.INFO)

    # Executor 로거 설정
    executor_logger = logging.getLogger(EXECUTOR_LOGGER_NAME)
    executor_logger.setLevel(getattr(logging, level.upper()))

    # Planner 로거 설정
    planner_logger = logging.getLogger(PLANNER_LOGGER_NAME)
    planner_logger.setLevel(getattr(logging, level.upper()))

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """로거를 가져옵니다.

    Args:
        name: 로거 이름 (None이면 루트 로거)

    Returns:
        로거 인스턴스
    """
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)


def log_execution_start(text_length: int, algorithm_count: int):
    """실행 시작 로그."""
    logger = get_logger("executor")
    logger.info(
        f"Analysis started: text_length={text_length}, algorithms={algorithm_count}"
    )


def log_execution_end(status: str, executed_steps: int, total_steps: int):
    """실행 종료 로그."""
    logger = get_logger("executor")
    logger.info(
        f"Analysis completed: status={status}, executed={executed_steps}/{total_steps}"
    )


def log_step_start(step_id: int, algorithm_name: str):
    """스텝 시작 로그."""
    logger = get_logger("executor")
    logger.info(f"Step {step_id} started: {algorithm_name}")


def log_step_end(step_id: int, algorithm_name: str, has_problem: bool, severity: str):
    """스텝 종료 로그."""
    logger = get_logger("executor")
    if has_problem:
        if severity == "critical":
            logger.warning(
                f"Step {step_id} ({algorithm_name}): CRITICAL problem found"
            )
        else:
            logger.warning(
                f"Step {step_id} ({algorithm_name}): {severity.upper()} - problem found"
            )
    else:
        logger.info(f"Step {step_id} ({algorithm_name}): passed")


def log_judge_reasoning(algorithm_name: str, reasoning: str, summary: str):
    """Judge reasoning 로그."""
    logger = get_logger("judge")
    logger.debug(
        f"Judge reasoning for {algorithm_name}:\n"
        f"  Reasoning: {reasoning}\n"
        f"  Summary: {summary}"
    )


def log_early_exit(step_id: int, algorithm_name: str, reason: str):
    """조기 종료 로그."""
    logger = get_logger("executor")
    logger.warning(
        f"Early exit at step {step_id} ({algorithm_name}): {reason}"
    )


def create_log_file_path(base_dir: str = "logs") -> str:
    """타임스탬프가 포함된 로그 파일 경로 생성."""
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(Path(base_dir) / f"analysis_{timestamp}.log")
