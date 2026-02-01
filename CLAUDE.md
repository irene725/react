# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

텍스트 분석 에이전트 시스템 - Plan-and-Execute 패턴과 ReAct Judge Agent를 활용하여 텍스트 데이터를 분석하고 문제 여부를 판단하는 시스템.

## Architecture

```
Planner → Executor → ReAct Judge → Reporter
```

- **Planner**: 구조화된 실행 계획(List[PlanStep]) 생성
- **Executor**: Plan에 따라 알고리즘 순차 실행, 문제 발견 시 조기 종료
- **ReAct Judge**: 각 알고리즘 결과를 판단 기준 문서와 비교하여 reasoning 기반 판단
- **Reporter**: 분석 결과를 Markdown 리포트로 생성

## Commands

```bash
# 가상환경 설정 및 의존성 설치
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 예제 실행
python examples/run_analysis.py

# 테스트 실행
pytest tests/
pytest tests/test_specific.py -v  # 단일 테스트

# 타입 체크
mypy src/
```

## Key Data Models

- `PlanStep`: 실행 계획의 단위 (step_id, algorithm_name, description, input_spec, depends_on)
- `Plan`: 전체 실행 계획 (steps, metadata)
- `JudgmentResult`: Judge 판단 결과 (has_problem, severity, reasoning, summary)
- `ExecutionResult`: 전체 실행 결과 (plan, step_results, status, stopped_at)

## Configuration

환경변수는 `.env` 파일에 설정:
- `OPENAI_API_KEY` 또는 `ANTHROPIC_API_KEY`: LLM API 키

## Development Notes

- 알고리즘 추가 시 `BaseAlgorithm` 추상 클래스를 상속하고 `AlgorithmRegistry`에 등록
- 각 알고리즘은 `src/criteria/` 디렉토리에 판단 기준 문서(.md) 필요
- ReAct Judge의 일관성을 위해 판단 기준 문서를 명확하게 작성
