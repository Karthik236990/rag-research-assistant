"""
Thin wrapper around ChromaDB for persistent local vector storage.
"""
from __future__ import annotations
import chromadb

import config
from src.utils import get_logger

logger = get_logger(__name__)


class VectorStore:
    def __init__(self, persist_dir=None, collection_name=None):
        persist_dir = str(persist_dir or config.VECTOR_DB_DIR)
        collection_name = collection_name or config.COLLECTION_NAME

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def already_ingested_sources(self) -> set[str]:
        """Return the set of source file names already present in the store."""
        try:
            existing = self.collection.get(include=["metadatas"])
        except Exception:
            return set()
        sources = set()
        for meta in existing.get("metadatas", []) or []:
            if meta and "source" in meta:
                sources.add(meta["source"])
        return sources

    def add(self, ids: list[str], embeddings, documents: list[str], metadatas: list[dict]):
        # Chroma metadata values must be str/int/float/bool, never None.
        clean_metas = [
            {k: (v if v is not None else "") for k, v in m.items()} for m in metadatas
        ]
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings,
            documents=documents,
            metadatas=clean_metas,
        )

    def query(self, query_embedding, top_k: int):
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding],
            n_results=top_k,
        )
        # Flatten Chroma's batched response format (single query -> single batch).
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        out = []
        for doc, meta, dist in zip(docs, metas, dists):
            out.append({"text": doc, "metadata": meta, "distance": dist})
        return out

    def count(self) -> int:
        return self.collection.count()
