"""텍스트 분석 에이전트 CLI."""

import sys
import click
from pathlib import Path

from .main import TextAnalyzer
from .logging_config import setup_logging, create_log_file_path


@click.group()
@click.version_option(version="0.1.0", prog_name="text-analyzer")
def cli():
    """텍스트 분석 에이전트 - Plan-and-Execute 패턴 기반 텍스트 분석 도구."""
    pass


@cli.command()
@click.argument("text", required=False)
@click.option(
    "-f", "--file",
    type=click.Path(exists=True, readable=True),
    help="분석할 텍스트 파일 경로"
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="리포트 저장 경로 (지정하지 않으면 콘솔 출력)"
)
@click.option(
    "--use-llm/--no-llm",
    default=False,
    help="LLM 기반 Judge 사용 여부 (기본: Mock Judge)"
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
    help="LLM 제공자 선택"
)
@click.option(
    "--model",
    default="gpt-4",
    help="사용할 LLM 모델 이름"
)
@click.option(
    "--no-early-exit",
    is_flag=True,
    default=False,
    help="Critical 문제 발견 시에도 조기 종료하지 않음"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    default=False,
    help="상세 출력 모드"
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="디버그 모드 (상세 로그 출력)"
)
@click.option(
    "--log-file",
    type=click.Path(),
    help="로그 파일 저장 경로"
)
@click.option(
    "--log-reasoning/--no-log-reasoning",
    default=True,
    help="Judge reasoning 로그 활성화/비활성화"
)
def analyze(text, file, output, use_llm, provider, model, no_early_exit, verbose, debug, log_file, log_reasoning):
    """텍스트를 분석하고 리포트를 생성합니다.

    TEXT: 분석할 텍스트 (직접 입력)

    예시:
        text-analyzer analyze "분석할 텍스트"
        text-analyzer analyze -f input.txt
        text-analyzer analyze -f input.txt -o report.md
        text-analyzer analyze -f input.txt --debug --log-file analysis.log
    """
    # 로깅 설정
    log_level = "DEBUG" if debug else ("INFO" if verbose else "WARNING")
    setup_logging(
        level=log_level,
        log_file=log_file,
        log_judge_reasoning=log_reasoning,
        debug_mode=debug
    )

    # 입력 텍스트 결정
    if file:
        input_text = Path(file).read_text(encoding="utf-8")
        if verbose:
            click.echo(f"파일에서 텍스트 로드: {file}")
    elif text:
        input_text = text
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
        if verbose:
            click.echo("stdin에서 텍스트 로드")
    else:
        click.echo("오류: 분석할 텍스트를 입력하세요.", err=True)
        click.echo("사용법: text-analyzer analyze \"텍스트\" 또는 -f 파일경로", err=True)
        sys.exit(1)

    if not input_text.strip():
        click.echo("오류: 빈 텍스트는 분석할 수 없습니다.", err=True)
        sys.exit(1)

    if verbose:
        click.echo(f"텍스트 길이: {len(input_text)}자")
        click.echo(f"LLM Judge: {'사용' if use_llm else '미사용 (Mock)'}")
        click.echo(f"조기 종료: {'비활성화' if no_early_exit else '활성화'}")
        click.echo("-" * 40)

    # TextAnalyzer 초기화
    try:
        analyzer = TextAnalyzer(
            use_llm_judge=use_llm,
            llm_provider=provider,
            llm_model=model,
            early_exit_on_critical=not no_early_exit
        )
    except Exception as e:
        click.echo(f"오류: 분석기 초기화 실패 - {e}", err=True)
        sys.exit(1)

    # 분석 실행
    try:
        if output:
            report = analyzer.analyze_and_save(input_text, output)
            click.echo(f"리포트 저장 완료: {output}")
        else:
            report = analyzer.analyze(input_text)
            click.echo(report.report_content)

        # 종료 코드 결정
        if report.has_problem:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        click.echo(f"오류: 분석 실패 - {e}", err=True)
        sys.exit(1)


@cli.command()
def algorithms():
    """등록된 알고리즘 목록을 출력합니다."""
    analyzer = TextAnalyzer()
    algos = analyzer.get_registered_algorithms()

    click.echo("등록된 알고리즘:")
    for name in algos:
        info = analyzer.registry.get_algorithm_info(name)
        click.echo(f"  - {name}: {info['description']}")


@cli.command()
@click.argument("algorithm_name")
def criteria(algorithm_name):
    """특정 알고리즘의 판단 기준 문서를 출력합니다.

    ALGORITHM_NAME: 알고리즘 이름 (예: length_check, keyword_check)
    """
    analyzer = TextAnalyzer()

    try:
        doc = analyzer.registry.get_criteria_document(algorithm_name)
        click.echo(doc)
    except FileNotFoundError:
        click.echo(f"오류: '{algorithm_name}' 알고리즘의 판단 기준 문서를 찾을 수 없습니다.", err=True)
        click.echo(f"사용 가능한 알고리즘: {', '.join(analyzer.get_registered_algorithms())}", err=True)
        sys.exit(1)


def main():
    """CLI 진입점."""
    cli()


if __name__ == "__main__":
    main()
