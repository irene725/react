# Task List: 텍스트 분석 에이전트 시스템

## Phase 1: MVP

### Task 1: 프로젝트 초기 설정
- [x] 프로젝트 디렉토리 구조 생성
- [x] `requirements.txt` 작성 (langchain, openai/anthropic, pydantic 등)
- [x] `config/settings.py` 설정 파일 생성
- [x] Python 가상환경 설정

### Task 2: 데이터 모델 구현
- [ ] `src/models/plan.py` - PlanStep, Plan 데이터클래스 구현
- [ ] `src/models/result.py` - StepResult, JudgmentResult, ExecutionResult 데이터클래스 구현
- [ ] `src/models/report.py` - AnalysisReport 모델 구현
- [ ] `src/models/__init__.py` - 모델 export

### Task 3: 알고리즘 인터페이스 및 Mock 구현
- [ ] `src/algorithms/base.py` - BaseAlgorithm 추상 클래스 구현
- [ ] `src/algorithms/mock_algorithms.py` - LengthCheckAlgorithm 구현
- [ ] `src/algorithms/mock_algorithms.py` - KeywordCheckAlgorithm 구현
- [ ] `src/algorithms/__init__.py` - 알고리즘 export

### Task 4: 판단 기준 문서 작성
- [ ] `src/criteria/length_check.md` - 길이 체크 판단 기준 문서
- [ ] `src/criteria/keyword_check.md` - 키워드 체크 판단 기준 문서

### Task 5: Algorithm Registry 구현
- [ ] `src/registry/algorithm_registry.py` - AlgorithmRegistry 클래스 구현
  - [ ] `register()` 메서드
  - [ ] `get_algorithm()` 메서드
  - [ ] `get_criteria_document()` 메서드
  - [ ] `list_algorithms()` 메서드
- [ ] `src/registry/__init__.py` - registry export

### Task 6: Planner 구현
- [ ] `src/planner/planner.py` - Planner 클래스 구현
  - [ ] `create_plan()` 메서드
  - [ ] `_get_description()` 헬퍼 메서드
- [ ] `src/planner/__init__.py` - planner export

### Task 7: ReAct Judge Agent 구현
- [ ] `src/judge/prompts.py` - Judge용 시스템 프롬프트 정의
- [ ] `src/judge/react_judge.py` - ReactJudge 클래스 구현
  - [ ] LLM 연동 (LangChain 활용)
  - [ ] `evaluate()` 메서드 - reasoning 기반 판단 로직
  - [ ] JudgmentResult 반환 로직
- [ ] `src/judge/__init__.py` - judge export

### Task 8: Executor 구현
- [ ] `src/executor/executor.py` - Executor 클래스 구현
  - [ ] `execute()` 메서드
  - [ ] 알고리즘 순차 실행 로직
  - [ ] Judge 호출 연동
  - [ ] 조기 종료 (Early Exit) 로직
- [ ] `src/executor/__init__.py` - executor export

### Task 9: Reporter 구현
- [ ] `src/reporter/reporter.py` - Reporter 클래스 구현
  - [ ] `generate()` 메서드 - Markdown 리포트 생성
  - [ ] 실행 결과 요약 포맷팅
  - [ ] 조기 종료 시 정보 포함
- [ ] `src/reporter/__init__.py` - reporter export

### Task 10: 메인 진입점 구현
- [ ] `src/main.py` - TextAnalyzer 클래스 구현
  - [ ] 컴포넌트 초기화
  - [ ] `analyze()` 메서드 - Plan → Execute → Report 흐름
- [ ] `src/__init__.py` - 메인 모듈 export

### Task 11: 예제 및 테스트
- [ ] `examples/run_analysis.py` - 실행 예제 코드 작성
- [ ] 정상 케이스 테스트 (모든 알고리즘 통과)
- [ ] 조기 종료 케이스 테스트 (문제 발견 시 중단)

---

## Phase 2: 완성도

### Task 12: CLI 인터페이스
- [ ] CLI 명령어 구현 (argparse 또는 click)
- [ ] 텍스트 파일 입력 지원
- [ ] 결과 출력 옵션 (console, file)

### Task 13: 에러 핸들링
- [ ] 커스텀 예외 클래스 정의
- [ ] 알고리즘 실행 에러 처리
- [ ] LLM API 호출 에러 처리
- [ ] 타임아웃 설정 및 처리

### Task 14: 로깅
- [ ] 로깅 설정 (logging 모듈)
- [ ] Judge reasoning 과정 로그 기록
- [ ] 실행 흐름 로그 기록
- [ ] 디버그 모드 지원

---

## 체크리스트

### 완료 기준
- [ ] 모든 데이터 모델이 정상 동작
- [ ] Mock 알고리즘 2개가 Registry에 등록되어 실행 가능
- [ ] Planner가 올바른 Plan 생성
- [ ] ReAct Judge가 판단 기준에 따라 일관된 판단 수행
- [ ] Executor가 조기 종료 로직 정상 처리
- [ ] Reporter가 Markdown 리포트 생성
- [ ] 예제 코드 실행 성공

### 주의사항
- [ ] ReAct Judge의 일관성을 위해 판단 기준 문서 명확히 작성
- [ ] Judge LLM 호출 시 타임아웃 설정
- [ ] Judge의 reasoning 과정을 로그로 기록
