"""Chatbot orchestration pipeline for simple customer support Q&A.

Pipeline:
    query_normalize -> intent_classify -> retrieve -> rerank
    -> answer_generate -> safety_check
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class Intent(str, Enum):
    """Supported intent taxonomy for simple inquiries."""

    FEE = "요금"
    OUTAGE = "장애"
    CONTRACT = "계약"
    BILLING = "납부"
    OTHER = "기타"


@dataclass(frozen=True)
class CandidateDocument:
    """Retrieved candidate document."""

    doc_id: str
    text: str
    retrieval_score: float


@dataclass(frozen=True)
class RankedDocument:
    """Reranked candidate document."""

    doc_id: str
    text: str
    retrieval_score: float
    rerank_score: float


# Retrieval/rerank policy (documented + codified)
RETRIEVE_TOP_K = 8
RERANK_TOP_N = 3
CONFIDENCE_THRESHOLD = 0.65

RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "snippet": {"type": "string"},
                },
                "required": ["doc_id", "snippet"],
                "additionalProperties": False,
            },
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "handoff_required": {"type": "boolean"},
        "next_question": {"type": ["string", "null"]},
    },
    "required": [
        "answer",
        "citations",
        "confidence",
        "handoff_required",
        "next_question",
    ],
    "additionalProperties": False,
}


class ChatbotOrchestrator:
    """End-to-end orchestrator with deterministic fallback and handoff policy."""

    def run(self, query: str) -> dict[str, Any]:
        normalized = self.query_normalize(query)
        intent = self.intent_classify(normalized)

        candidates = self.retrieve(normalized, intent, k=RETRIEVE_TOP_K)
        ranked = self.rerank(normalized, candidates, top_n=RERANK_TOP_N)

        response = self.answer_generate(normalized, intent, ranked)
        response = self.safety_check(response)
        return response

    def query_normalize(self, query: str) -> str:
        return " ".join(query.strip().split())

    def intent_classify(self, normalized_query: str) -> Intent:
        q = normalized_query
        if any(token in q for token in ("요금", "가격", "플랜")):
            return Intent.FEE
        if any(token in q for token in ("장애", "끊김", "안됨")):
            return Intent.OUTAGE
        if any(token in q for token in ("계약", "약정", "해지")):
            return Intent.CONTRACT
        if any(token in q for token in ("납부", "결제", "청구")):
            return Intent.BILLING
        return Intent.OTHER

    def retrieve(self, normalized_query: str, intent: Intent, k: int = RETRIEVE_TOP_K) -> list[CandidateDocument]:
        """Retrieve top-k candidates.

        NOTE: Replace this stub with vector/BM25 retrieval against your knowledge base.
        """
        del normalized_query, intent
        kb = [
            CandidateDocument("DOC-101", "요금제 변경은 앱 설정 > 요금제에서 가능합니다.", 0.91),
            CandidateDocument("DOC-202", "납부일은 매월 25일이며 카드 변경은 마이페이지에서 가능합니다.", 0.86),
            CandidateDocument("DOC-303", "장애 신고는 24시간 고객센터에서 접수합니다.", 0.82),
            CandidateDocument("DOC-404", "약정 해지 시 위약금이 발생할 수 있습니다.", 0.80),
        ]
        return sorted(kb, key=lambda d: d.retrieval_score, reverse=True)[:k]

    def rerank(
        self,
        normalized_query: str,
        candidates: Iterable[CandidateDocument],
        top_n: int = RERANK_TOP_N,
    ) -> list[RankedDocument]:
        """Rerank candidates and keep top-n."""
        tokens = set(normalized_query.split())
        ranked: list[RankedDocument] = []
        for doc in candidates:
            overlap = len(tokens.intersection(doc.text.split()))
            rerank_score = (doc.retrieval_score * 0.7) + (overlap * 0.1)
            ranked.append(
                RankedDocument(
                    doc_id=doc.doc_id,
                    text=doc.text,
                    retrieval_score=doc.retrieval_score,
                    rerank_score=rerank_score,
                )
            )
        return sorted(ranked, key=lambda d: d.rerank_score, reverse=True)[:top_n]

    def answer_generate(
        self,
        normalized_query: str,
        intent: Intent,
        ranked_docs: list[RankedDocument],
    ) -> dict[str, Any]:
        """Generate answer with mandatory internal grounding by doc_id and snippet."""
        del normalized_query
        citations = [
            {"doc_id": d.doc_id, "snippet": self._core_sentence(d.text)} for d in ranked_docs
        ]

        if not citations:
            return self._make_handoff_response(
                answer="확인 가능한 근거 문서를 찾지 못했습니다.",
                confidence=0.0,
                reason="additional_info",
            )

        # Internal grounding enforcement:
        # answer must be synthesized from selected citations (doc_id + snippet).
        answer = self._build_grounded_answer(intent=intent, citations=citations)
        confidence = min(0.99, 0.5 + (len(citations) * 0.15))

        if confidence < CONFIDENCE_THRESHOLD:
            return self._make_handoff_response(
                answer=answer,
                confidence=confidence,
                reason="additional_info",
            )

        return {
            "answer": answer,
            "citations": citations,
            "confidence": confidence,
            "handoff_required": False,
            "next_question": None,
        }

    def safety_check(self, response: dict[str, Any]) -> dict[str, Any]:
        """Basic safety layer that removes sensitive strings and ensures schema keys."""
        answer = response.get("answer", "")
        response["answer"] = answer.replace("주민등록번호", "[민감정보]")

        for key in ("citations", "confidence", "handoff_required", "next_question"):
            response.setdefault(key, [] if key == "citations" else None)

        if response["confidence"] is None:
            response["confidence"] = 0.0
        if response["handoff_required"] is None:
            response["handoff_required"] = True

        return response

    def _core_sentence(self, text: str) -> str:
        return text.split(".")[0].strip() + "."

    def _build_grounded_answer(self, intent: Intent, citations: list[dict[str, str]]) -> str:
        head = f"[{intent.value}] 문의에 대해 확인된 내용입니다."
        bullet = " ".join(f"({c['doc_id']}) {c['snippet']}" for c in citations)
        return f"{head} {bullet}".strip()

    def _make_handoff_response(self, answer: str, confidence: float, reason: str) -> dict[str, Any]:
        if reason == "additional_info":
            next_question = "사용 중인 상품명/오류 발생 시각을 알려주실 수 있을까요?"
            handoff_required = False
        else:
            next_question = "상담원 연결을 진행할까요?"
            handoff_required = True

        return {
            "answer": answer,
            "citations": [],
            "confidence": confidence,
            "handoff_required": handoff_required,
            "next_question": next_question,
        }
