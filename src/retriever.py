"""
Retriever: embeds a query and fetches the top-K most relevant chunks
from the vector store.
"""
import config
from src.embeddings import get_embedder
from src.vectorstore import VectorStore
from src.utils import get_logger

logger = get_logger(__name__)


class Retriever:
    def __init__(self, vectorstore: VectorStore = None, embedder=None):
        self.vectorstore = vectorstore or VectorStore()
        self.embedder = embedder or get_embedder()

    def retrieve(self, query: str, top_k: int = None) -> list[dict]:
        top_k = top_k or config.TOP_K
        if self.vectorstore.count() == 0:
            logger.warning("Vector store is empty. Run `python main.py ingest` first.")
            return []

        query_embedding = self.embedder.embed_query(query)
        results = self.vectorstore.query(query_embedding, top_k=top_k)
        return results
