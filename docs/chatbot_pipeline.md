# Chatbot Orchestration Pipeline

## 단계
1. `query_normalize`
2. `intent_classify`
3. `retrieve`
4. `rerank`
5. `answer_generate`
6. `safety_check`

## Intent Taxonomy
- 요금
- 장애
- 계약
- 납부
- 기타

## Retrieval & Rerank 정책
- Retrieve Top-k: `k=8`
- Rerank Top-n: `top=3`
- 기본 confidence 임계치: `0.65`

## Grounding 규칙
생성 단계는 반드시 `doc_id`와 `snippet`(핵심 문장)을 내부 근거로 사용해서 답변을 조립한다.

## Confidence 분기
- `confidence < 0.65`: 추가 정보 요청 또는 상담원 연결 분기
- `confidence >= 0.65`: 일반 응답

## 응답 JSON 스키마
```json
{
  "answer": "string",
  "citations": [{"doc_id": "string", "snippet": "string"}],
  "confidence": 0.0,
  "handoff_required": false,
  "next_question": "string|null"
}
```
