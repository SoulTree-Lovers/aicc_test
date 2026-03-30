# RAG 관측 로그 스키마

## 이벤트명
- `rag_query_evaluated`

## 필수 필드
| field | type | 설명 |
|---|---|---|
| `query` | string | 사용자 원문 질의 |
| `retrieved_docs` | array<object> | 검색된 문서 목록(최대 5~10 권장) |
| `confidence` | number | 모델 최종 응답 신뢰도(0.0~1.0) |
| `handoff` | object | 이관 판단 정보 |
| `latency_ms` | integer | 엔드투엔드 지연(ms) |

## 세부 구조
```json
{
  "query": "해외 로밍 요금 상세 내역을 보고 싶습니다.",
  "retrieved_docs": [
    {
      "doc_id": "billing_kr_0421",
      "title": "로밍 청구 상세 조회 가이드",
      "score": 0.91,
      "source": "kb"
    }
  ],
  "confidence": 0.88,
  "handoff": {
    "required": false,
    "target": null,
    "reason": null
  },
  "latency_ms": 742
}
```

## 검증 규칙
- `query`: 빈 문자열 불가.
- `retrieved_docs[*].score`: 0.0~1.0.
- `confidence`: 0.0~1.0.
- `handoff.required=true` 인 경우 `target` 필수.
- `latency_ms`: 0 이상 정수.
