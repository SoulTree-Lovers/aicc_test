from __future__ import annotations

from dataclasses import dataclass


DEFAULT_MIN_TOKENS = 500
DEFAULT_MAX_TOKENS = 800
DEFAULT_OVERLAP = 100


@dataclass(frozen=True)
class ChunkingPolicy:
    min_tokens: int = DEFAULT_MIN_TOKENS
    max_tokens: int = DEFAULT_MAX_TOKENS
    overlap_tokens: int = DEFAULT_OVERLAP

    def __post_init__(self) -> None:
        if self.min_tokens <= 0 or self.max_tokens <= 0:
            raise ValueError("Token sizes must be positive")
        if self.min_tokens > self.max_tokens:
            raise ValueError("min_tokens cannot be greater than max_tokens")
        if self.overlap_tokens < 0:
            raise ValueError("overlap_tokens cannot be negative")
        if self.overlap_tokens >= self.max_tokens:
            raise ValueError("overlap_tokens must be smaller than max_tokens")


def chunk_text_by_tokens(
    text: str,
    policy: ChunkingPolicy | None = None,
) -> list[str]:
    """Chunk text with token-count bounds and overlap.

    Uses whitespace tokenization as a model-agnostic approximation.
    """

    policy = policy or ChunkingPolicy()
    tokens = text.split()
    if not tokens:
        return []

    chunks: list[str] = []
    start = 0
    step = policy.max_tokens - policy.overlap_tokens

    while start < len(tokens):
        end = min(start + policy.max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        if len(chunk_tokens) < policy.min_tokens and chunks:
            chunks[-1] = f"{chunks[-1]} {' '.join(chunk_tokens)}".strip()
            break

        chunks.append(" ".join(chunk_tokens))
        if end >= len(tokens):
            break
        start += step

    return chunks
