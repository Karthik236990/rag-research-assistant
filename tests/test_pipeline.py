"""
Unit tests for chunking and citation-formatting logic.
These test pure logic only (no API calls / no model downloads) so they
run fast and fully offline.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingest import _split_into_chunks
from src.utils import format_sources, truncate


def test_split_into_chunks_basic():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = _split_into_chunks(text, chunk_size=1000, overlap=0)
    assert len(chunks) == 1  # fits in one chunk
    assert "Paragraph one." in chunks[0]


def test_split_into_chunks_respects_size():
    text = "\n\n".join([f"This is paragraph number {i}." for i in range(50)])
    chunks = _split_into_chunks(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    for c in chunks:
        # allow a little slack for overlap prefix
        assert len(c) <= 100 + 15


def test_split_into_chunks_empty():
    assert _split_into_chunks("", chunk_size=500, overlap=50) == []


def test_split_into_chunks_hard_split_long_paragraph():
    long_para = "word " * 500  # ~2500 chars, no paragraph breaks
    chunks = _split_into_chunks(long_para, chunk_size=200, overlap=20)
    assert len(chunks) > 1


def test_format_sources():
    chunks = [
        {"metadata": {"source": "report.pdf", "page": 3}},
        {"metadata": {"source": "notes.txt", "page": None}},
    ]
    result = format_sources(chunks)
    assert "[1] report.pdf (page 3)" in result
    assert "[2] notes.txt" in result
    assert "page None" not in result


def test_format_sources_empty():
    assert format_sources([]) == ""


def test_truncate():
    assert truncate("short") == "short"
    long_text = "a" * 200
    out = truncate(long_text, max_len=50)
    assert len(out) == 50
    assert out.endswith("...")
