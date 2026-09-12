"""
Embedding backend for the RAG pipeline.

Primary: sentence-transformers (local, offline after first model download).
Fallback: scikit-learn TF-IDF vectors if sentence-transformers isn't
installed or fails to load (e.g. no internet on first run). This keeps the
whole project usable in fully offline / constrained environments.
"""
from __future__ import annotations
import numpy as np

import config
from src.utils import get_logger

logger = get_logger(__name__)


class BaseEmbedder:
    def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        from sentence_transformers import SentenceTransformer  # local import
        logger.info("Loading sentence-transformers model '%s'...", model_name)
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        return np.array(self.model.encode(texts, show_progress_bar=False))


class TfidfEmbedder(BaseEmbedder):
    """
    Offline fallback. Fits a TF-IDF vectorizer over the corpus at index time.
    Note: unlike a real embedding model, this must be fit once on the full
    set of chunks before it can embed queries meaningfully, so the
    vectorstore persists the fitted vectorizer alongside the DB.
    """
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(max_features=4096)
        self._fitted = False

    def fit(self, texts: list[str]):
        self.vectorizer.fit(texts)
        self._fitted = True

    def embed(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            self.fit(texts)
        return self.vectorizer.transform(texts).toarray()


def get_embedder() -> BaseEmbedder:
    """Try sentence-transformers first, fall back to TF-IDF on any failure."""
    try:
        return SentenceTransformerEmbedder()
    except Exception as e:
        logger.warning(
            "sentence-transformers unavailable (%s). Falling back to TF-IDF embedder. "
            "Install sentence-transformers for better retrieval quality.",
            e,
        )
        return TfidfEmbedder()
