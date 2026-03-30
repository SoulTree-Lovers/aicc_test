"""Chatbot guardrails for policy-aligned response checks."""

from __future__ import annotations

import re
from typing import Dict, List


FORBIDDEN_PATTERNS: Dict[str, List[re.Pattern[str]]] = {
    "assertive_falsehood": [
        re.compile(r"\b(무조건|100%|절대|반드시)\b"),
        re.compile(r"\b(사실입니다|확실합니다)\b"),
    ],
    "pii_redisclosure": [
        re.compile(r"\b\d{6}-\d{7}\b"),  # 주민등록번호 형식
        re.compile(r"\b\d{2,3}-\d{3,4}-\d{4}\b"),  # 전화번호 형식
        re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),  # 이메일 형식
        re.compile(r"\b\d{12,19}\b"),  # 카드번호 추정 패턴
    ],
}


def detect_forbidden_patterns(text: str) -> Dict[str, List[str]]:
    """Detect disallowed content patterns in a candidate response."""
    findings: Dict[str, List[str]] = {}
    for category, patterns in FORBIDDEN_PATTERNS.items():
        matches: List[str] = []
        for pattern in patterns:
            for match in pattern.findall(text):
                if isinstance(match, tuple):
                    matches.append("".join(match))
                else:
                    matches.append(match)
        if matches:
            findings[category] = sorted(set(matches))
    return findings


def build_source_summary(sources: List[str], max_items: int = 3) -> str:
    """Build a minimal source summary while suppressing internal details."""
    if not sources:
        return "근거 출처 요약: 제공된 외부 근거 없음"

    redacted = []
    for src in sources[:max_items]:
        cleaned = re.sub(r"(token|internal|prompt|secret)=[^&\s]+", r"\1=***", src, flags=re.I)
        redacted.append(cleaned)
    if len(sources) > max_items:
        redacted.append("외 N건")

    return "근거 출처 요약: " + ", ".join(redacted)


def build_failure_response(missing_info_hint: str = "○○") -> str:
    """Return policy failure response template with missing info hint."""
    return f"확인 가능한 정보가 부족합니다. {missing_info_hint} 정보를 알려주시면 정확히 안내드리겠습니다."
