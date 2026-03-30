from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


REQUIRED_METADATA_FIELDS = (
    "category",
    "effective_date",
    "policy_version",
    "source_url",
    "last_verified_at",
)


@dataclass(frozen=True)
class DocumentMetadata:
    """Normalized metadata schema for all indexed documents."""

    category: str
    effective_date: str
    policy_version: str
    source_url: str
    last_verified_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        missing = [field for field in REQUIRED_METADATA_FIELDS if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required metadata field(s): {', '.join(missing)}")

        _validate_iso_date(data["effective_date"], "effective_date")
        _validate_iso_datetime(data["last_verified_at"], "last_verified_at")

        return cls(
            category=str(data["category"]),
            effective_date=str(data["effective_date"]),
            policy_version=str(data["policy_version"]),
            source_url=str(data["source_url"]),
            last_verified_at=str(data["last_verified_at"]),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "effective_date": self.effective_date,
            "policy_version": self.policy_version,
            "source_url": self.source_url,
            "last_verified_at": self.last_verified_at,
        }


def _validate_iso_date(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be YYYY-MM-DD, got: {value}") from exc


def _validate_iso_datetime(value: str, field_name: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be ISO-8601 datetime, got: {value}"
        ) from exc
