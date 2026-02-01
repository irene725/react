# PRD: 텍스트 분석 에이전트 시스템 (Plan-and-Execute + ReAct Judge)

## 1. 프로젝트 개요

### 1.1 목적
입력된 텍스트 데이터에 대해 다수의 분석 알고리즘을 실행하고, 각 알고리즘별 전용 판단 기준에 따라 문제 여부를 판단하는 시스템 구축

### 1.2 핵심 특징
- **Plan-and-Execute 패턴**: 구조화된 실행 계획(PlanStep)을 생성하고 순차 실행
- **ReAct Judge Agent**: 각 알고리즘 결과를 판단 기준 문서와 비교하여 reasoning 기반 판단
- **조기 종료 (Early Exit)**: 문제 발견 시 나머지 알고리즘 실행 없이 즉시 리포트 생성
- **명확한 역할 분리**: Planner, Executor, Judge, Reporter 각각 독립적 책임

---

## 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         Planner                                 │
│  - 구조화된 실행 계획(Plan) 생성                                  │
│  - Output: List[PlanStep]                                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Executor                                 │
│  - Plan에 따라 알고리즘 순차 실행                                 │
│  - 각 실행 후 ReAct Judge 호출                                   │
│  - has_problem=true 시 loop 탈출                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ReAct Judge Agent                            │
│  [Thought] 판단 기준 문서를 확인해보자...                         │
│  [Thought] 결과값 length=1500이 threshold 1000을 초과한다       │
│  [Thought] 기준에 따르면 이건 Critical에 해당한다                 │
│  [Final Answer] has_problem: true, severity: critical           │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Reporter                                 │
│  - 모든 판단 결과 종합                                           │
│  - Markdown 리포트 생성                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 핵심 데이터 모델

### 3.1 PlanStep

실행 계획의 단위를 나타내는 구조체

```python
from dataclasses import dataclass
from typing import Optional, List, Any, Dict

@dataclass
class PlanStep:
    step_id: int                          # 실행 순서 (1부터 시작)
    algorithm_name: str                   # 실행할 알고리즘 이름
    description: str                      # 이 단계가 하는 일 설명
    input_spec: Dict[str, Any]            # 입력 명세 (어떤 데이터를 사용하는지)
    depends_on: List[int] = None          # 의존하는 step_id 목록 (없으면 독립 실행)
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
```

### 3.2 Plan

전체 실행 계획

```python
@dataclass
class Plan:
    steps: List[PlanStep]
    metadata: Dict[str, Any] = None       # 계획 관련 메타데이터
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def get_step(self, step_id: int) -> Optional[PlanStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_execution_order(self) -> List[PlanStep]:
        """의존성을 고려한 실행 순서 반환"""
        return sorted(self.steps, key=lambda s: s.step_id)
```

### 3.3 StepResult

각 단계 실행 결과

```python
@dataclass
class StepResult:
    step: PlanStep                        # 실행된 단계
    execution_result: Dict[str, Any]      # 알고리즘 실행 결과
    judgment: 'JudgmentResult'            # Judge 판단 결과
    executed_at: str                      # 실행 시각 (ISO format)
```

### 3.4 JudgmentResult

Judge의 판단 결과

```python
@dataclass
class JudgmentResult:
    algorithm_name: str
    has_problem: bool                     # 문제 여부
    severity: str                         # "critical" | "warning" | "none"
    reasoning: str                        # 판단 과정 설명
    summary: str                          # 1-2문장 요약
```

### 3.5 ExecutionResult

전체 실행 결과

```python
@dataclass
class ExecutionResult:
    plan: Plan                            # 실행된 계획
    step_results: List[StepResult]        # 각 단계 결과
    status: str                           # "problem_found" | "all_passed"
    stopped_at: Optional[PlanStep]        # 조기 종료 시 중단된 단계
```

---

## 4. 핵심 컴포넌트

### 4.1 Planner

**역할**: 구조화된 실행 계획 생성

```python
class Planner:
    def __init__(self, config: Config):
        self.config = config
    
    def create_plan(
        self, 
        text: str, 
        available_algorithms: List[str]
    ) -> Plan:
        """
        실행 계획 생성
        
        Args:
            text: 분석할 텍스트
            available_algorithms: 사용 가능한 알고리즘 목록
            
        Returns:
            Plan: 구조화된 실행 계획
        """
        steps = []
        for idx, algo_name in enumerate(self.config.algorithm_order, start=1):
            if algo_name not in available_algorithms:
                continue
                
            step = PlanStep(
                step_id=idx,
                algorithm_name=algo_name,
                description=self._get_description(algo_name),
                input_spec={"text": "original_input"},
                depends_on=[idx - 1] if idx > 1 else []
            )
            steps.append(step)
        
        return Plan(
            steps=steps,
            metadata={
                "created_at": datetime.now().isoformat(),
                "total_steps": len(steps)
            }
        )
```

---

### 4.2 Executor

**역할**: Plan에 따라 알고리즘 실행 및 Judge 호출, 조기 종료 처리

```python
class Executor:
    def __init__(self, registry: AlgorithmRegistry, judge: ReactJudge):
        self.registry = registry
        self.judge = judge
    
    def execute(self, text: str, plan: Plan) -> ExecutionResult:
        step_results = []
        stopped_at = None
        
        for step in plan.get_execution_order():
            # 1. 알고리즘 실행
            algo = self.registry.get_algorithm(step.algorithm_name)
            algo_result = algo.execute(text)
            
            # 2. ReAct Judge로 판단
            criteria_doc = self.registry.get_criteria_document(step.algorithm_name)
            judgment = self.judge.evaluate(
                algorithm_name=step.algorithm_name,
                execution_result=algo_result,
                criteria_document=criteria_doc
            )
            
            # 3. 결과 저장
            step_result = StepResult(
                step=step,
                execution_result=algo_result,
                judgment=judgment,
                executed_at=datetime.now().isoformat()
            )
            step_results.append(step_result)
            
            # 4. 문제 발견 시 조기 종료
            if judgment.has_problem:
                stopped_at = step
                break
        
        return ExecutionResult(
            plan=plan,
            step_results=step_results,
            status="problem_found" if stopped_at else "all_passed",
            stopped_at=stopped_at
        )
```

---

### 4.3 ReAct Judge Agent

**역할**: 알고리즘 실행 결과를 판단 기준 문서에 따라 평가

**System Prompt**:
```
당신은 텍스트 분석 결과를 판단하는 Judge입니다.

주어진 정보:
1. 알고리즘 이름
2. 알고리즘 실행 결과
3. 판단 기준 문서

작업:
판단 기준 문서에 따라 실행 결과가 문제가 있는지 판단하세요.

Reasoning 과정을 거쳐 최종 판단을 내리세요:
- 판단 기준의 각 조건을 확인
- 실행 결과 값과 비교
- 해당하는 severity 결정
- 최종 판단 도출
```

**ReAct 동작 예시**:
```
Input:
- algorithm_name: "length_check"
- execution_result: {"length": 1500}
- criteria_document: "length > 1000 → Critical..."

[Thought] 판단 기준을 확인하자. length > 1000이면 Critical, > 500이면 Warning이다.
[Thought] 실행 결과의 length는 1500이다.
[Thought] 1500 > 1000 이므로 Critical 조건에 해당한다.
[Final Answer]
{
    "has_problem": true,
    "severity": "critical",
    "reasoning": "length 값이 1500으로 threshold 1000을 초과함",
    "summary": "텍스트 길이가 허용 범위를 초과했습니다."
}
```

---

### 4.4 Reporter

**역할**: 분석 결과 종합 리포트 생성

```python
class Reporter:
    def generate(self, execution_result: ExecutionResult) -> str:
        """Markdown 형식 리포트 반환"""
        pass
```

---

### 4.5 Algorithm Registry

**역할**: 알고리즘과 판단 기준 문서 관리

```python
class AlgorithmRegistry:
    def register(self, name: str, algorithm: BaseAlgorithm, criteria_doc_path: str)
    def get_algorithm(self, name: str) -> BaseAlgorithm
    def get_criteria_document(self, name: str) -> str
    def list_algorithms(self) -> List[str]
```

---

## 5. 인터페이스 정의

### 5.1 BaseAlgorithm (추상 클래스)

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAlgorithm(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @abstractmethod
    def execute(self, text: str) -> Dict[str, Any]:
        pass
```

### 5.2 메인 진입점

```python
class TextAnalyzer:
    def __init__(self, config: Config):
        self.planner = Planner(config)
        self.executor = Executor(config)
        self.reporter = Reporter()
    
    def analyze(self, text: str) -> AnalysisReport:
        # 1. Plan
        plan = self.planner.create_plan(text)
        
        # 2. Execute (includes ReAct Judge)
        execution_result = self.executor.execute(text, plan)
        
        # 3. Report
        report = self.reporter.generate(execution_result)
        
        return report
```

---

## 6. 테스트용 Mock 알고리즘

### 6.1 LengthCheckAlgorithm

```python
class LengthCheckAlgorithm(BaseAlgorithm):
    name = "length_check"
    description = "텍스트 길이를 체크합니다"
    
    def execute(self, text: str) -> dict:
        return {"length": len(text)}
```

**판단 기준 문서 (criteria/length_check.md)**:
```markdown
# 길이 체크 판단 기준

## 조건
- length > 1000 → Critical (문제 있음)
- length > 500 → Warning (문제 있음)
- length <= 500 → 정상 (문제 없음)
```

### 6.2 KeywordCheckAlgorithm

```python
class KeywordCheckAlgorithm(BaseAlgorithm):
    name = "keyword_check"
    description = "금지 키워드 포함 여부를 체크합니다"
    
    def execute(self, text: str) -> dict:
        banned = ["금지어1", "금지어2"]
        found = [w for w in banned if w in text]
        return {"found": found, "count": len(found)}
```

**판단 기준 문서 (criteria/keyword_check.md)**:
```markdown
# 키워드 체크 판단 기준

## 조건
- count >= 2 → Critical (문제 있음)
- count == 1 → Warning (문제 있음)
- count == 0 → 정상 (문제 없음)
```

---

## 7. 디렉토리 구조

```
text-analysis-agent/
├── README.md
├── requirements.txt
├── config/
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── plan.py              # PlanStep, Plan
│   │   ├── result.py            # StepResult, JudgmentResult, ExecutionResult
│   │   └── report.py            # AnalysisReport
│   ├── planner/
│   │   ├── __init__.py
│   │   └── planner.py
│   ├── executor/
│   │   ├── __init__.py
│   │   └── executor.py
│   ├── judge/
│   │   ├── __init__.py
│   │   ├── react_judge.py
│   │   └── prompts.py
│   ├── reporter/
│   │   ├── __init__.py
│   │   └── reporter.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── mock_algorithms.py
│   ├── criteria/
│   │   ├── length_check.md
│   │   └── keyword_check.md
│   └── registry/
│       ├── __init__.py
│       └── algorithm_registry.py
└── examples/
    └── run_analysis.py
```

---

## 8. 실행 흐름 예시

### Case: 조기 종료

```
Input: (1500자 텍스트)

[Planner] Plan 생성:
  Step 1: length_check - "텍스트 길이를 체크합니다" (depends_on: [])
  Step 2: keyword_check - "금지 키워드를 체크합니다" (depends_on: [1])

[Executor] Step 1 실행: length_check
  → execution_result: {"length": 1500}
  → [Judge] 
      [Thought] 기준: length > 1000 → Critical
      [Thought] 결과: length = 1500
      [Thought] 1500 > 1000 이므로 Critical
      [Final] has_problem=true, severity=critical
  → 문제 발견! Loop 종료.

[Reporter] 
  Status: problem_found
  Stopped at: Step 1 (length_check)
  Executed: 1/2 steps
```

---

## 9. 기술 스택

- Python 3.10+
- LangChain 또는 LangGraph (ReAct Judge 구현)
- OpenAI API 또는 Anthropic API (LLM)
- Pydantic (데이터 검증)

---

## 10. 구현 우선순위

### Phase 1: MVP
1. 데이터 모델 (PlanStep, Plan, StepResult, JudgmentResult, ExecutionResult)
2. BaseAlgorithm 추상 클래스
3. Mock 알고리즘 2개 + 판단 기준 문서
4. Algorithm Registry
5. Planner (규칙 기반)
6. ReAct Judge Agent
7. Executor
8. Reporter (기본)

### Phase 2: 완성도
1. CLI 인터페이스
2. 에러 핸들링
3. 로깅

---

## 11. 주의사항

1. **ReAct Judge의 일관성**: 판단 기준 문서를 명확하게 작성해야 LLM이 일관된 판단 가능
2. **타임아웃**: Judge LLM 호출 시 타임아웃 설정
3. **로깅**: Judge의 reasoning 과정을 로그로 기록 (디버깅 용이)