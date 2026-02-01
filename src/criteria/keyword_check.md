# 키워드 체크 (Keyword Check) 판단 기준

## 개요
텍스트에 금지된 키워드가 포함되어 있는지 판단합니다.

## 판단 기준

### 문제 없음 (No Problem)
- `has_forbidden_keywords`가 `false`인 경우
- 금지된 키워드가 발견되지 않음

### 경고 (Warning)
- `has_forbidden_keywords`가 `true`이고
- 발견된 키워드가 1개인 경우
- 단순 실수 또는 문맥상 허용 가능한 사용일 수 있음

### 심각 (Critical)
- `has_forbidden_keywords`가 `true`이고
- 발견된 키워드가 2개 이상인 경우
- 의도적인 규정 위반으로 판단

## 결과 해석

| 필드 | 설명 |
|------|------|
| `raw_result` | 발견된 금지 키워드 목록 |
| `has_forbidden_keywords` | 금지 키워드 발견 여부 (boolean) |
| `keyword_count` | 발견된 키워드 수 |
| `keyword_positions` | 각 키워드의 발견 위치 |
| `checked_keywords` | 검사 대상 키워드 목록 |

## 판단 예시

### 예시 1: 정상
```json
{
  "raw_result": [],
  "has_forbidden_keywords": false,
  "keyword_count": 0,
  "keyword_positions": {},
  "checked_keywords": ["욕설", "비속어", "금지어"]
}
```
→ **severity: none** - 금지된 키워드가 발견되지 않았습니다.

### 예시 2: 경고
```json
{
  "raw_result": ["광고"],
  "has_forbidden_keywords": true,
  "keyword_count": 1,
  "keyword_positions": {"광고": [15]},
  "checked_keywords": ["욕설", "비속어", "금지어", "광고"]
}
```
→ **severity: warning** - 금지 키워드 '광고'가 1회 발견되었습니다.

### 예시 3: 심각
```json
{
  "raw_result": ["욕설", "비속어"],
  "has_forbidden_keywords": true,
  "keyword_count": 2,
  "keyword_positions": {"욕설": [5, 30], "비속어": [20]},
  "checked_keywords": ["욕설", "비속어", "금지어"]
}
```
→ **severity: critical** - 금지 키워드 '욕설', '비속어'가 발견되었습니다. 총 3회 출현.

## 특이 사항
- 키워드 검사는 대소문자를 구분하지 않을 수 있음 (`case_sensitive` 설정에 따름)
- 동일 키워드의 다중 출현은 `keyword_positions`에서 확인 가능
- 문맥을 고려한 판단이 필요할 수 있음
