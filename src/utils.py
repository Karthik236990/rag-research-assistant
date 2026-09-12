"""Small shared helpers: logging setup and source citation formatting."""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def format_sources(chunks: list) -> str:
    """
    Build a human-readable numbered "Sources" section from a list of
    retrieved chunk dicts (each with 'metadata' containing 'source' and
    optionally 'page').
    """
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        page = meta.get("page")
        if page is not None:
            lines.append(f"[{i}] {source} (page {page})")
        else:
            lines.append(f"[{i}] {source}")
    return "\n".join(lines)


def truncate(text: str, max_len: int = 100) -> str:
    return text if len(text) <= max_len else text[: max_len - 3] + "..."
