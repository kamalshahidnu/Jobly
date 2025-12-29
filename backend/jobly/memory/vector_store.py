"""Vector store for semantic search and embeddings."""

from typing import List, Dict, Any, Optional
import numpy as np


class VectorStore:
    """Vector database for semantic search."""

    def __init__(self, dimension: int = 768):
        """Initialize vector store.

        Args:
            dimension: Dimension of embedding vectors
        """
        self.dimension = dimension
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        self.ids: List[str] = []

    def add(self, vector: List[float], metadata: Dict[str, Any], doc_id: str) -> None:
        """Add vector to store.

        Args:
            vector: Embedding vector
            metadata: Associated metadata
            doc_id: Document ID
        """
        self.vectors.append(np.array(vector))
        self.metadata.append(metadata)
        self.ids.append(doc_id)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding
            top_k: Number of results to return

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
            results.append({
                "id": self.ids[idx],
                "metadata": self.metadata[idx],
                "similarity": similarities[idx]
            })

        return results

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
            return True
        return False
