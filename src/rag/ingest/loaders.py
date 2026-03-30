from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".html", ".htm", ".csv"}


@dataclass
class RawDocument:
    source_path: str
    content: str
    content_type: str


def ingest_documents(input_dir: str) -> list[RawDocument]:
    """Load FAQ/업무매뉴얼/공지 documents from PDF/HTML/CSV files."""

    base = Path(input_dir)
    if not base.exists() or not base.is_dir():
        raise ValueError(f"input_dir must be an existing directory: {input_dir}")

    docs: list[RawDocument] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            content = _extract_pdf_text(path)
            content_type = "pdf"
        elif suffix in {".html", ".htm"}:
            content = _extract_html_text(path)
            content_type = "html"
        else:
            content = _extract_csv_text(path)
            content_type = "csv"

        docs.append(
            RawDocument(source_path=str(path), content=content, content_type=content_type)
        )

    return docs


def _extract_pdf_text(path: Path) -> str:
    """Best-effort PDF extraction.

    Tries pypdf if available; otherwise raises an actionable error.
    """

    try:
        from pypdf import PdfReader  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "pypdf is required for PDF ingestion. Install with: pip install pypdf"
        ) from exc

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def _extract_html_text(path: Path) -> str:
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "beautifulsoup4 is required for HTML ingestion. Install with: pip install beautifulsoup4"
        ) from exc

    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def _extract_csv_text(path: Path) -> str:
    rows: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            rows.append(" | ".join(cell.strip() for cell in row))
    return "\n".join(rows)
