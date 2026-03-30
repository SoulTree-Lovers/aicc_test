# 자동 평가 지표 정의 (Call Center RAG)

## 1) 정답성 (Answer Correctness)
- **목적**: 최종 답변이 정답 레퍼런스와 의미적으로 일치하는지 측정.
- **입력**: `prediction.answer`, `gold.answer`.
- **산식**:
  - LLM-as-a-judge 점수(0~1) + 키워드/슬롯 매칭 F1(0~1)의 가중 평균.
  - `correctness = 0.7 * judge_score + 0.3 * slot_f1`
- **합격 기준(권장)**: 평균 0.85 이상.

## 2) 근거정합성 (Grounding Consistency)
- **목적**: 답변의 핵심 주장들이 검색 문서에 의해 뒷받침되는지 측정.
- **입력**: `prediction.answer`, `retrieved_docs[]`.
- **산식**:
  - 주장 단위 분해 후 각 주장에 대해 `supported / contradicted / unknown` 판정.
  - `grounding = supported_claims / total_claims`
  - 패널티: `contradicted` 존재 시 -0.2(하한 0).
- **합격 기준(권장)**: 평균 0.90 이상, contradiction 비율 2% 이하.

## 3) 재질문 적절성 (Clarification Appropriateness)
- **목적**: 정보 부족 시 재질문을 해야 할 상황에서만 적절히 재질문하는지 평가.
- **입력**: `needs_clarification(gold)` 라벨, `prediction.follow_up`.
- **산식**:
  - 이진 분류 정확도 + 질문 품질(구체성/최소성) judge 점수.
  - `clarification = 0.6 * classification_f1 + 0.4 * question_quality`
- **합격 기준(권장)**: 평균 0.80 이상.

## 4) 이관 정확도 (Handoff Accuracy)
- **목적**: 상담사/전문부서 이관이 필요한 케이스를 정확히 탐지하고 올바른 타겟으로 이관하는지 평가.
- **입력**: `gold.handoff_required`, `gold.handoff_target`, `prediction.handoff`.
- **산식**:
  - 필요 여부 F1 + 타겟 정확도.
  - `handoff_accuracy = 0.5 * handoff_need_f1 + 0.5 * handoff_target_acc`
- **합격 기준(권장)**: 평균 0.90 이상.

## 종합 점수
- 운영 모니터링용 가중치:
  - 정답성 35%
  - 근거정합성 30%
  - 재질문 적절성 15%
  - 이관 정확도 20%
- `overall_score = 0.35*C + 0.30*G + 0.15*Q + 0.20*H`

## 리포팅 규칙
- 주간 리포트에는 평균뿐 아니라 p50/p90, 실패 Top 5 intent, 주요 반례를 함께 기록.
- 배포 게이트 권장안:
  - `overall_score >= 0.87`
  - `grounding >= 0.90`
  - `handoff_accuracy >= 0.90`
