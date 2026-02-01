# 텍스트 분석 리포트

**생성 시각**: 2026-02-01 15:23:33

## 요약

✅ **모든 검사를 통과했습니다.** 발견된 문제가 없습니다.

## 실행 정보

- **전체 단계 수**: 2
- **실행된 단계 수**: 2
- **상태**: ✅ 모두 통과

## 단계별 분석 결과

### Step 1: length_check

**설명**: 텍스트 길이가 10~10000자 범위 내에 있는지 검사

**판단 결과**: ✅ NONE

**상세 분석**:

> Text length (83) is within the allowed range (10-10000).

**요약**: Text length is acceptable.

<details>
<summary>실행 결과 상세</summary>

```json
{
  "raw_result": 83,
  "is_within_range": true,
  "min_length": 10,
  "max_length": 10000,
  "length_diff": 0
}
```

</details>

### Step 2: keyword_check

**설명**: 텍스트에 금지된 키워드가 포함되어 있는지 검사

**판단 결과**: ✅ NONE

**상세 분석**:

> No forbidden keywords were found in the text.

**요약**: No forbidden keywords detected.

<details>
<summary>실행 결과 상세</summary>

```json
{
  "raw_result": [],
  "has_forbidden_keywords": false,
  "keyword_count": 0,
  "keyword_positions": {},
  "checked_keywords": [
    "욕설",
    "비속어",
    "금지어",
    "스팸",
    "광고"
  ]
}
```

</details>

## 결론

분석 대상 텍스트는 모든 검사 기준을 충족합니다. 추가적인 조치가 필요하지 않습니다.