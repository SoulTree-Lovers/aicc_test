from __future__ import annotations

import re
from dataclasses import dataclass


PHONE_PATTERN = re.compile(r"\b(?:01[016789]-?\d{3,4}-?\d{4}|0\d{1,2}-?\d{3,4}-?\d{4})\b")
RRN_PATTERN = re.compile(r"\b\d{6}-?[1-4]\d{6}\b")
ACCOUNT_PATTERN = re.compile(r"\b\d{2,6}-\d{2,6}-\d{2,6}\b|\b\d{10,14}\b")


@dataclass(frozen=True)
class MaskingResult:
    text: str
    stats: dict[str, int]


def apply_pii_masking(text: str) -> MaskingResult:
    """Mask phone numbers, resident registration numbers, and account numbers."""

    masked, phone_count = PHONE_PATTERN.subn("[MASKED_PHONE]", text)
    masked, rrn_count = RRN_PATTERN.subn("[MASKED_RRN]", masked)
    masked, account_count = ACCOUNT_PATTERN.subn("[MASKED_ACCOUNT]", masked)

    return MaskingResult(
        text=masked,
        stats={
            "phone": phone_count,
            "resident_registration": rrn_count,
            "account": account_count,
        },
    )
