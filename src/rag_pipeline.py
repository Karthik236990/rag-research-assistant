"""
Orchestrates the full pipeline: ingest -> embed -> store, and
retrieve -> generate -> cite.
"""
from __future__ import annotations
import uuid

import config
from src.ingest import load_all_documents
from src.embeddings import get_embedder, TfidfEmbedder
from src.vectorstore import VectorStore
from src.retriever import Retriever
from src.llm import GeminiAnswerer
from src.utils import get_logger, format_sources

logger = get_logger(__name__)


def ingest_documents(force: bool = False):
    """Load, embed, and store all documents in data/documents/."""
    store = VectorStore()
    already = store.already_ingested_sources() if not force else set()

    chunks = load_all_documents()
    if not chunks:
        return 0

    new_chunks = [c for c in chunks if c.source not in already]
    if not new_chunks:
        logger.info("All documents already ingested. Use --force to re-ingest.")
        return 0

    embedder = get_embedder()
    texts = [c.text for c in new_chunks]

    # TF-IDF must be fit on the whole corpus before producing usable vectors.
    if isinstance(embedder, TfidfEmbedder):
        embedder.fit(texts)

    embeddings = embedder.embed(texts)
    ids = [c.chunk_id or str(uuid.uuid4()) for c in new_chunks]
    metadatas = [c.metadata for c in new_chunks]

    store.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    logger.info("Ingested %d new chunks from %d source file(s).",
                len(new_chunks), len({c.source for c in new_chunks}))
    return len(new_chunks)


def ask_question(question: str, top_k: int = None) -> dict:
    """Run retrieval + generation for a single question. Returns dict with
    'answer' and 'sources' (formatted string) and raw 'passages'."""
    retriever = Retriever()
    passages = retriever.retrieve(question, top_k=top_k)

    answerer = GeminiAnswerer()
    answer = answerer.answer(question, passages)
    sources = format_sources(passages) if passages else ""

    return {"answer": answer, "sources": sources, "passages": passages}
