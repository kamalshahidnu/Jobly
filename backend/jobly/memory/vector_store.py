"""Vector store for semantic search and embeddings."""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

# Try to import sentence-transformers, fall back to basic implementation
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class VectorStore:
    """Vector database for semantic search with embeddings."""

    def __init__(
        self,
        dimension: int = 384,
        model_name: str = "all-MiniLM-L6-v2",
        store_path: Optional[str] = None,
    ):
        """Initialize vector store.

        Args:
            dimension: Dimension of embedding vectors
            model_name: Name of sentence-transformers model
            store_path: Path to persist the vector store
        """
        self.dimension = dimension
        self.model_name = model_name
        self.store_path = store_path or os.path.expanduser("~/.jobly/vector_store.pkl")
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        self.ids: List[str] = []
        self.model = None

        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.dimension = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                print(f"Error loading embedding model: {e}")

        # Load existing store
        self._load_store()

    def _load_store(self) -> None:
        """Load vector store from disk."""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "rb") as f:
                    data = pickle.load(f)
                    self.vectors = data.get("vectors", [])
                    self.metadata = data.get("metadata", [])
                    self.ids = data.get("ids", [])
            except Exception as e:
                print(f"Error loading vector store: {e}")

    def _save_store(self) -> None:
        """Save vector store to disk."""
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, "wb") as f:
                pickle.dump({
                    "vectors": self.vectors,
                    "metadata": self.metadata,
                    "ids": self.ids,
                }, f)
        except Exception as e:
            print(f"Error saving vector store: {e}")

    def add(self, vector: List[float], metadata: Dict[str, Any], doc_id: str) -> None:
        """Add vector to store.

        Args:
            vector: Embedding vector
            metadata: Associated metadata
            doc_id: Document ID
        """
        # Check if document exists
        if doc_id in self.ids:
            idx = self.ids.index(doc_id)
            self.vectors[idx] = np.array(vector)
            self.metadata[idx] = metadata
        else:
            self.vectors.append(np.array(vector))
            self.metadata.append(metadata)
            self.ids.append(doc_id)

        self._save_store()

    def add_text(self, text: str, metadata: Dict[str, Any], doc_id: str) -> bool:
        """Add text document by generating embedding.

        Args:
            text: Text to embed
            metadata: Associated metadata
            doc_id: Document ID

        Returns:
            Success status
        """
        if not self.model:
            print("Embedding model not available")
            return False

        try:
            vector = self.model.encode(text, convert_to_numpy=True)
            self.add(vector.tolist(), metadata, doc_id)
            return True
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return False

    def add_texts_batch(self, documents: List[Dict[str, Any]]) -> int:
        """Add multiple text documents in batch.

        Args:
            documents: List of dicts with 'text', 'metadata', 'id'

        Returns:
            Number of documents added
        """
        if not self.model:
            return 0

        texts = [doc["text"] for doc in documents]
        try:
            vectors = self.model.encode(texts, convert_to_numpy=True)
            for i, doc in enumerate(documents):
                self.add(vectors[i].tolist(), doc["metadata"], doc["id"])
            return len(documents)
        except Exception as e:
            print(f"Error in batch embedding: {e}")
            return 0

    def search(self, query_vector: List[float], top_k: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            min_score: Minimum similarity score

        Returns:
            List of similar documents with metadata
        """
        if not self.vectors:
            return []

        query = np.array(query_vector)
        similarities = [self._cosine_similarity(query, vec) for vec in self.vectors]
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= min_score:
                results.append({
                    "id": self.ids[idx],
                    "metadata": self.metadata[idx],
                    "similarity": score
                })

        return results

    def search_text(self, query: str, top_k: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """Search using text query.

        Args:
            query: Text query
            top_k: Number of results
            min_score: Minimum similarity score

        Returns:
            List of similar documents
        """
        if not self.model:
            print("Embedding model not available")
            return []

        try:
            query_vector = self.model.encode(query, convert_to_numpy=True)
            return self.search(query_vector.tolist(), top_k, min_score)
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity score
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def delete(self, doc_id: str) -> bool:
        """Delete document by ID.

        Args:
            doc_id: Document ID to delete

        Returns:
            Success status
        """
        if doc_id in self.ids:
            idx = self.ids.index(doc_id)
            del self.vectors[idx]
            del self.metadata[idx]
            del self.ids[idx]
            self._save_store()
            return True
        return False

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document metadata
        """
        if doc_id in self.ids:
            idx = self.ids.index(doc_id)
            return self.metadata[idx]
        return None

    def clear(self) -> None:
        """Clear all documents from store."""
        self.vectors = []
        self.metadata = []
        self.ids = []
        self._save_store()

    def size(self) -> int:
        """Get number of documents in store.

        Returns:
            Document count
        """
        return len(self.ids)


# Helper functions for job search
def add_job_to_vector_store(vector_store: VectorStore, job: Dict[str, Any]) -> bool:
    """Add a job to the vector store.

    Args:
        vector_store: VectorStore instance
        job: Job data

    Returns:
        Success status
    """
    job_id = job.get("job_id") or job.get("id")
    if not job_id:
        return False

    # Create searchable text
    text_parts = [
        job.get("title", ""),
        job.get("company", ""),
        job.get("description", ""),
        " ".join(job.get("requirements", [])),
        " ".join(job.get("skills", [])),
    ]
    text = " ".join(filter(None, text_parts))

    metadata = {
        "job_id": job_id,
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "source": job.get("source"),
        "url": job.get("url"),
    }

    return vector_store.add_text(text, metadata, str(job_id))


def search_jobs_semantic(
    vector_store: VectorStore,
    query: str,
    top_k: int = 20,
    min_score: float = 0.3,
) -> List[Dict[str, Any]]:
    """Search for jobs using semantic search.

    Args:
        vector_store: VectorStore instance
        query: Search query
        top_k: Number of results
        min_score: Minimum similarity score

    Returns:
        List of matching jobs
    """
    results = vector_store.search_text(query, top_k, min_score)
    return [r["metadata"] for r in results]
