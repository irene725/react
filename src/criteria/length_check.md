# 길이 체크 (Length Check) 판단 기준

## 개요
텍스트의 길이가 허용된 범위 내에 있는지 판단합니다.

## 판단 기준

### 문제 없음 (No Problem)
- `is_within_range`가 `true`인 경우
- 텍스트 길이가 설정된 최소/최대 범위 내에 있음

### 경고 (Warning)
- `is_within_range`가 `false`이고
- `length_diff`가 범위의 10% 이내인 경우
- 예: 최소 길이 100에서 텍스트가 95자인 경우 (5자 부족, 5%)

### 심각 (Critical)
- `is_within_range`가 `false`이고
- `length_diff`가 범위의 10%를 초과하는 경우
- 예: 최소 길이 100에서 텍스트가 50자인 경우 (50자 부족, 50%)

## 결과 해석

| 필드 | 설명 |
|------|------|
| `raw_result` | 실제 텍스트 길이 |
| `is_within_range` | 범위 내 여부 (boolean) |
| `min_length` | 설정된 최소 허용 길이 |
| `max_length` | 설정된 최대 허용 길이 |
| `length_diff` | 범위와의 차이 (범위 내면 0) |

## 판단 예시

### 예시 1: 정상
```json
{
  "raw_result": 150,
  "is_within_range": true,
  "min_length": 10,
  "max_length": 10000,
  "length_diff": 0
}
```
→ **severity: none** - 텍스트 길이가 정상 범위 내입니다.

### 예시 2: 경고
```json
{
  "raw_result": 8,
  "is_within_range": false,
  "min_length": 10,
  "max_length": 10000,
  "length_diff": 2
}
```
→ **severity: warning** - 텍스트가 최소 길이보다 2자 부족합니다 (20% 미달).

### 예시 3: 심각
```json
{
  "raw_result": 3,
  "is_within_range": false,
  "min_length": 10,
  "max_length": 10000,
  "length_diff": 7
}
```
→ **severity: critical** - 텍스트가 최소 길이보다 7자 부족합니다 (70% 미달).
