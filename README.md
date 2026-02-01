# Text Analysis Agent System

텍스트 데이터를 분석하고 문제 여부를 판단하는 에이전트 시스템입니다.

## 특징

- **Plan-and-Execute 패턴**: 구조화된 실행 계획을 생성하고 순차 실행
- **ReAct Judge Agent**: Reasoning + Acting 패턴으로 반복적 추론-행동 사이클을 통한 판단
- **조기 종료 (Early Exit)**: Critical 문제 발견 시 즉시 리포트 생성
- **명확한 역할 분리**: Planner, Executor, Judge, Reporter

## 아키텍처

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Planner   │ --> │  Executor   │ --> │ ReAct Judge │ --> │  Reporter   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### ReAct Judge

ReAct Judge는 Reasoning + Acting 패턴을 구현합니다:

```
Thought → Action → Observation → Thought → Action → ... → submit_judgment
```

**사용 가능한 도구:**
- `get_criteria`: 판단 기준 문서 로드
- `check_threshold`: 임계값 조건 확인
- `calculate_percentage`: 백분율 계산
- `submit_judgment`: 최종 판단 제출

## 요구사항

- Python 3.8+
- LangChain
- OpenAI API 또는 Anthropic API
- Pydantic, Click

## 설치

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# API 키 설정
OPENAI_API_KEY=your-api-key
# 또는
ANTHROPIC_API_KEY=your-api-key
```

## 사용법

### CLI
pip install -e .
text-analyzer analyze -f examples/input.txt --use-llm --provider openai --model gpt-4 

```bash
# 텍스트 직접 분석
text-analyzer analyze "분석할 텍스트"

# 파일에서 텍스트 분석
text-analyzer analyze -f input.txt

# 리포트를 파일로 저장
text-analyzer analyze -f input.txt -o report.md

# LLM Judge 사용 (기본은 Mock Judge)
text-analyzer analyze -f input.txt --use-llm --provider openai --model gpt-4

# LiteLLM 사용 (다양한 LLM 프로바이더 지원)
text-analyzer analyze -f input.txt --use-llm --provider litellm --model openai/gpt-4
text-analyzer analyze -f input.txt --use-llm --provider litellm --model anthropic/claude-3-opus-20240229

# 디버그 모드
text-analyzer analyze -f input.txt --debug --log-file analysis.log

# 등록된 알고리즘 목록 확인
text-analyzer algorithms

# 판단 기준 문서 확인
text-analyzer criteria length_check
```

### Python API

```python
from src.main import TextAnalyzer

# Mock Judge 사용 (기본)
analyzer = TextAnalyzer()

# LLM Judge 사용
analyzer = TextAnalyzer(
    use_llm_judge=True,
    llm_provider="openai",
    llm_model="gpt-4"
)

# LiteLLM 사용 (다양한 프로바이더 통합)
analyzer = TextAnalyzer(
    use_llm_judge=True,
    llm_provider="litellm",
    llm_model="openai/gpt-4"  # 또는 "anthropic/claude-3-opus-20240229"
)

text = "분석할 텍스트..."
report = analyzer.analyze(text)
print(report.report_content)

# 파일로 저장
analyzer.analyze_and_save(text, "report.md")
```

## 프로젝트 구조

```
text-analysis-agent/
├── config/
│   ├── __init__.py
│   └── settings.py          # 설정 관리
├── src/
│   ├── __init__.py
│   ├── main.py               # TextAnalyzer 메인 클래스
│   ├── cli.py                # CLI 인터페이스
│   ├── exceptions.py         # 커스텀 예외 클래스
│   ├── logging_config.py     # 로깅 설정
│   ├── models/
│   │   ├── plan.py           # PlanStep, Plan 모델
│   │   ├── result.py         # StepResult, JudgmentResult, ExecutionResult
│   │   └── report.py         # AnalysisReport 모델
│   ├── planner/
│   │   └── planner.py        # 실행 계획 생성
│   ├── executor/
│   │   └── executor.py       # 계획 실행 및 조기 종료
│   ├── judge/
│   │   ├── react_judge.py    # ReAct 패턴 Judge Agent
│   │   ├── tools.py          # Judge 도구 구현
│   │   └── prompts.py        # 프롬프트 유틸리티
│   ├── reporter/
│   │   └── reporter.py       # Markdown 리포트 생성
│   ├── algorithms/
│   │   ├── base.py           # BaseAlgorithm 추상 클래스
│   │   └── mock_algorithms.py # LengthCheck, KeywordCheck 구현
│   ├── criteria/
│   │   ├── length_check.md   # 길이 체크 판단 기준
│   │   └── keyword_check.md  # 키워드 체크 판단 기준
│   └── registry/
│       └── algorithm_registry.py  # 알고리즘 레지스트리
├── tests/
│   ├── test_algorithms.py
│   ├── test_executor.py
│   ├── test_planner.py
│   ├── test_registry.py
│   └── test_text_analyzer.py
└── examples/
    └── run_analysis.py       # 실행 예제
```

## 테스트

```bash
# 전체 테스트 실행
pytest tests/

# 특정 테스트 파일 실행
pytest tests/test_executor.py -v

# 커버리지 포함
pytest tests/ --cov=src
```

## 알고리즘 추가하기

1. `BaseAlgorithm`을 상속한 새 알고리즘 클래스 구현
2. `src/criteria/`에 판단 기준 문서(.md) 작성
3. `AlgorithmRegistry`에 등록

```python
from src.algorithms.base import BaseAlgorithm

class MyAlgorithm(BaseAlgorithm):
    @property
    def name(self) -> str:
        return "my_algorithm"

    @property
    def description(self) -> str:
        return "My custom algorithm"

    def execute(self, text: str) -> dict:
        # 구현
        return {"result": ...}
```

## 라이선스

MIT License
