"""Tests for job service."""

import pytest
from jobly.services.job_service import JobService


class TestJobService:
    """Test cases for JobService."""

    @pytest.fixture
    def service(self, db_store):
        """Create JobService instance.

        Args:
            db_store: Test database store

        Returns:
            JobService instance
        """
        return JobService(db_store)

    def test_service_initialization(self, service, db_store):
        """Test service initialization."""
        assert service.store == db_store

    def test_create_job(self, service, sample_job):
        """Test creating a job."""
        job = service.create_job(sample_job)
        assert job.title == sample_job["title"]
        assert job.company == sample_job["company"]

    def test_list_jobs_returns_empty_list(self, service):
        """Test listing jobs returns empty list when no jobs."""
        jobs = service.list_jobs()
        assert jobs == []
