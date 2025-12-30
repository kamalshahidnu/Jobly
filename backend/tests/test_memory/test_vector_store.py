"""Tests for VectorStore."""

import pytest
from jobly.memory.vector_store import VectorStore, add_job_to_vector_store, search_jobs_semantic


def test_vector_store_initialization():
    """Test vector store initialization."""
    store = VectorStore(store_path="/tmp/test_vector_store.pkl")

    assert store.size() == 0
    assert store.vectors is not None


def test_add_and_get_document():
    """Test adding and retrieving documents."""
    store = VectorStore(store_path="/tmp/test_vector_store_2.pkl")

    # Clear any existing data
    store.clear()

    # Add a document with direct vector
    vector = [0.1] * store.dimension if store.model else [0.1] * 384
    metadata = {"title": "Test Document", "type": "test"}

    store.add(vector, metadata, "doc1")

    assert store.size() == 1

    # Get document
    doc = store.get("doc1")
    assert doc is not None
    assert doc["title"] == "Test Document"


def test_delete_document():
    """Test deleting documents."""
    store = VectorStore(store_path="/tmp/test_vector_store_3.pkl")
    store.clear()

    vector = [0.1] * (store.dimension if store.model else 384)
    store.add(vector, {"title": "Doc to delete"}, "doc1")

    assert store.size() == 1

    success = store.delete("doc1")
    assert success is True
    assert store.size() == 0


def test_clear_store():
    """Test clearing the store."""
    store = VectorStore(store_path="/tmp/test_vector_store_4.pkl")

    vector = [0.1] * (store.dimension if store.model else 384)
    store.add(vector, {"title": "Doc 1"}, "doc1")
    store.add(vector, {"title": "Doc 2"}, "doc2")

    assert store.size() == 2

    store.clear()
    assert store.size() == 0


def test_add_job_to_vector_store():
    """Test adding a job to vector store."""
    store = VectorStore(store_path="/tmp/test_vector_store_5.pkl")
    store.clear()

    job = {
        "job_id": "job123",
        "title": "Software Engineer",
        "company": "TechCorp",
        "description": "Build scalable systems",
        "requirements": ["Python", "SQL"],
        "skills": ["FastAPI", "PostgreSQL"]
    }

    # This will only work if sentence-transformers is installed
    # Otherwise it will return False
    if store.model:
        success = add_job_to_vector_store(store, job)
        assert success is True
        assert store.size() == 1

        # Verify job was added
        doc = store.get("job123")
        assert doc is not None
        assert doc["title"] == "Software Engineer"


def test_search_with_empty_store():
    """Test search with empty store."""
    store = VectorStore(store_path="/tmp/test_vector_store_6.pkl")
    store.clear()

    vector = [0.1] * (store.dimension if store.model else 384)
    results = store.search(vector, top_k=5)

    assert results == []


def test_add_duplicate_document():
    """Test that adding duplicate ID updates the document."""
    store = VectorStore(store_path="/tmp/test_vector_store_7.pkl")
    store.clear()

    vector1 = [0.1] * (store.dimension if store.model else 384)
    vector2 = [0.2] * (store.dimension if store.model else 384)

    store.add(vector1, {"title": "Original"}, "doc1")
    assert store.size() == 1

    store.add(vector2, {"title": "Updated"}, "doc1")
    assert store.size() == 1  # Should still be 1

    doc = store.get("doc1")
    assert doc["title"] == "Updated"
