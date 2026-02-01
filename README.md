# Text Analysis Agent System

텍스트 데이터를 분석하고 문제 여부를 판단하는 에이전트 시스템입니다.

## 특징

- **Plan-and-Execute 패턴**: 구조화된 실행 계획을 생성하고 순차 실행
- **ReAct Judge Agent**: 각 알고리즘 결과를 판단 기준 문서와 비교하여 reasoning 기반 판단
- **조기 종료 (Early Exit)**: 문제 발견 시 즉시 리포트 생성
- **명확한 역할 분리**: Planner, Executor, Judge, Reporter

## 아키텍처

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Planner   │ --> │  Executor   │ --> │ ReAct Judge │ --> │  Reporter   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## 요구사항

- Python 3.10+
- LangChain
- OpenAI API 또는 Anthropic API
- Pydantic

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

```python
from src.main import TextAnalyzer
from config.settings import Config

config = Config()
analyzer = TextAnalyzer(config)

text = "분석할 텍스트..."
report = analyzer.analyze(text)
print(report)
```

## 프로젝트 구조

```
text-analysis-agent/
├── config/
│   └── settings.py
├── src/
│   ├── main.py
│   ├── models/
│   │   ├── plan.py
│   │   ├── result.py
│   │   └── report.py
│   ├── planner/
│   ├── executor/
│   ├── judge/
│   ├── reporter/
│   ├── algorithms/
│   ├── criteria/
│   └── registry/
└── examples/
    └── run_analysis.py
```

## 라이선스

MIT License
