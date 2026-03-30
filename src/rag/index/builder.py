from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rag.schema import DocumentMetadata


@dataclass
class IndexedChunk:
    chunk_id: str
    text: str
    embedding: list[float]
    metadata: dict[str, str]


class EmbeddingModel:
    """Protocol-like base class for embedding providers."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class VectorIndex:
    """Protocol-like base class for vector index backends."""

    def upsert(self, items: list[IndexedChunk]) -> None:
        raise NotImplementedError


class InMemoryVectorIndex(VectorIndex):
    def __init__(self) -> None:
        self.items: dict[str, IndexedChunk] = {}

    def upsert(self, items: list[IndexedChunk]) -> None:
        for item in items:
            self.items[item.chunk_id] = item


class SimpleHashEmbeddingModel(EmbeddingModel):
    """Dependency-free embedding fallback for local validation."""

    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vec = [0.0] * self.dimensions
            for token in text.split():
                vec[hash(token) % self.dimensions] += 1.0
            norm = sum(x * x for x in vec) ** 0.5 or 1.0
            vectors.append([x / norm for x in vec])
        return vectors


def build_and_index(
    *,
    chunks: Iterable[str],
    metadata: dict[str, str],
    embedding_model: EmbeddingModel,
    vector_index: VectorIndex,
    source_id: str,
) -> list[IndexedChunk]:
    """Generate embeddings and load chunks into vector index with enforced metadata."""

    validated_metadata = DocumentMetadata.from_dict(metadata).to_dict()
    chunk_list = [chunk for chunk in chunks if chunk.strip()]
    embeddings = embedding_model.encode(chunk_list)

    indexed_items = [
        IndexedChunk(
            chunk_id=f"{source_id}:{i}",
            text=chunk,
            embedding=embeddings[i],
            metadata=validated_metadata,
        )
        for i, chunk in enumerate(chunk_list)
    ]

    vector_index.upsert(indexed_items)
    return indexed_items
