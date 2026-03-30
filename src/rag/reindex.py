from __future__ import annotations

from pathlib import Path

from rag.index import InMemoryVectorIndex, SimpleHashEmbeddingModel, build_and_index
from rag.ingest import ingest_documents
from rag.preprocess import ChunkingPolicy, apply_pii_masking, chunk_text_by_tokens


def reindex_knowledge_base(input_dir: str) -> int:
    docs = ingest_documents(input_dir)
    embedding_model = SimpleHashEmbeddingModel()
    vector_index = InMemoryVectorIndex()

    total_chunks = 0
    for doc in docs:
        masking = apply_pii_masking(doc.content)
        chunks = chunk_text_by_tokens(masking.text, ChunkingPolicy())
        if not chunks:
            continue

        metadata = {
            "category": _category_from_path(doc.source_path),
            "effective_date": "2026-01-01",
            "policy_version": "v1",
            "source_url": f"file://{Path(doc.source_path).resolve()}",
            "last_verified_at": "2026-03-30T00:00:00Z",
        }
        indexed = build_and_index(
            chunks=chunks,
            metadata=metadata,
            embedding_model=embedding_model,
            vector_index=vector_index,
            source_id=Path(doc.source_path).stem,
        )
        total_chunks += len(indexed)

    return total_chunks


def _category_from_path(path: str) -> str:
    lowered = path.lower()
    if "faq" in lowered:
        return "faq"
    if "매뉴얼" in lowered or "manual" in lowered:
        return "manual"
    if "공지" in lowered or "notice" in lowered:
        return "notice"
    return "general"
