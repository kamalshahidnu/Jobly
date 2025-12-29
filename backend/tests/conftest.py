"""Pytest configuration and fixtures."""

import pytest
from jobly.memory.sqlite_store import SQLiteStore
from jobly.models.database import Base, get_engine


@pytest.fixture
def test_db():
    """Create test database.

    Yields:
        Database engine
    """
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_store():
    """Create test database store.

    Yields:
        SQLiteStore instance
    """
    store = SQLiteStore(":memory:")
    store.connect()
    yield store
    store.disconnect()


@pytest.fixture
def sample_profile():
    """Sample user profile data.

    Returns:
        Profile dictionary
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "location": "San Francisco, CA",
        "skills": ["Python", "JavaScript", "React"],
        "experience_years": 5
    }


@pytest.fixture
def sample_job():
    """Sample job posting data.

    Returns:
        Job dictionary
    """
    return {
        "title": "Software Engineer",
        "company": "Test Corp",
        "location": "Remote",
        "description": "Great opportunity",
        "requirements": ["Python", "API development"],
        "url": "https://example.com/job",
        "source": "linkedin",
        "job_type": "full_time"
    }


@pytest.fixture
def sample_contact():
    """Sample contact data.

    Returns:
        Contact dictionary
    """
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "company": "Test Corp",
        "position": "Engineering Manager"
    }
