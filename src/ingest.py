"""
Load documents (PDF / TXT / MD) from a folder and split them into
overlapping text chunks, preserving source file name and page number
(for PDFs) as metadata so answers can be cited later.
"""
from pathlib import Path
from dataclasses import dataclass, field

from pypdf import PdfReader

import config
from src.utils import get_logger

logger = get_logger(__name__)


@dataclass
class Chunk:
    text: str
    source: str
    page: int | None = None
    chunk_id: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        self.metadata = {"source": self.source, "page": self.page}


def _read_pdf(path: Path) -> list[tuple[str, int]]:
    """Returns list of (page_text, page_number) tuples, 1-indexed pages."""
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((text, i))
    return pages


def _read_text(path: Path) -> list[tuple[str, int | None]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [(text, None)]


def _split_into_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Simple sliding-window character-based splitter with paragraph awareness."""
    text = text.strip()
    if not text:
        return []

    # Prefer splitting on paragraph boundaries when possible.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 1 <= chunk_size:
            current = f"{current}\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            if len(para) > chunk_size:
                # Paragraph itself too long: hard-split with overlap.
                start = 0
                while start < len(para):
                    end = start + chunk_size
                    chunks.append(para[start:end])
                    start = end - overlap
            else:
                current = para

    if current:
        chunks.append(current)

    # Apply overlap between adjacent chunks for better context continuity.
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append((prev_tail + " " + chunks[i]).strip())
        return overlapped

    return chunks


def load_and_chunk_file(path: Path) -> list[Chunk]:
    """Load a single file and return a list of Chunk objects."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        pages = _read_pdf(path)
    elif ext in (".txt", ".md"):
        pages = _read_text(path)
    else:
        logger.warning("Skipping unsupported file type: %s", path.name)
        return []

    chunks: list[Chunk] = []
    for page_text, page_num in pages:
        pieces = _split_into_chunks(page_text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        for idx, piece in enumerate(pieces):
            chunk_id = f"{path.name}::p{page_num or 0}::c{idx}"
            chunks.append(Chunk(text=piece, source=path.name, page=page_num, chunk_id=chunk_id))

    logger.info("Loaded %d chunks from %s", len(chunks), path.name)
    return chunks


def load_all_documents(documents_dir: Path = None) -> list[Chunk]:
    """Load and chunk every supported file in the documents directory."""
    documents_dir = documents_dir or config.DOCUMENTS_DIR
    documents_dir.mkdir(parents=True, exist_ok=True)

    all_chunks: list[Chunk] = []
    files = [
        f for f in sorted(documents_dir.iterdir())
        if f.is_file() and f.suffix.lower() in config.SUPPORTED_EXTENSIONS
    ]

    if not files:
        logger.warning(
            "No supported documents found in %s. Add .pdf/.txt/.md files and re-run.",
            documents_dir,
        )
        return []

    for f in files:
        all_chunks.extend(load_and_chunk_file(f))

    return all_chunks
