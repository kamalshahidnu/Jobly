"""Job service for job-related operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..models.schemas import JobPosting
from ..memory.sqlite_store import SQLiteStore


class JobService:
    """Service layer for job operations."""

    def __init__(self, store: SQLiteStore):
        """Initialize job service.

        Args:
            store: Database store instance
        """
        self.store = store

    def create_job(self, job_data: Dict[str, Any]) -> JobPosting:
        """Create a new job posting.

        Args:
            job_data: Job data

        Returns:
            Created job posting
        """
        payload = dict(job_data or {})
        payload.setdefault("id", str(uuid4()))

        job = JobPosting(**payload)
        row = {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "requirements": self.store.dumps(job.requirements),
            "url": job.url,
            "source": job.source,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "salary_range": job.salary_range,
            "job_type": job.job_type,
            "created_at": job.created_at.isoformat(),
        }
        self.store.insert("jobs", row)
        return job

    def get_job(self, job_id: str) -> Optional[JobPosting]:
        """Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job posting or None
        """
        row = self.store.fetch_one("SELECT * FROM jobs WHERE id = ?", (job_id,))
        if not row:
            return None
        row["requirements"] = self.store.loads(row.get("requirements"), [])
        posted = row.get("posted_date")
        if posted:
            try:
                row["posted_date"] = datetime.fromisoformat(posted)
            except ValueError:
                row["posted_date"] = None
        created = row.get("created_at")
        if created:
            try:
                row["created_at"] = datetime.fromisoformat(created)
            except ValueError:
                row["created_at"] = datetime.utcnow()
        return JobPosting(**row)

    def list_jobs(self, filters: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[JobPosting]:
        """List jobs with optional filters.

        Args:
            filters: Optional filter criteria
            limit: Maximum number of results

        Returns:
            List of job postings
        """
        filters = filters or {}
        where: List[str] = []
        params: List[Any] = []

        if company := filters.get("company"):
            where.append("LOWER(company) = LOWER(?)")
            params.append(company)
        if job_type := filters.get("job_type"):
            where.append("LOWER(job_type) = LOWER(?)")
            params.append(job_type)
        if source := filters.get("source"):
            where.append("LOWER(source) = LOWER(?)")
            params.append(source)

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        rows = self.store.fetch_all(
            f"SELECT * FROM jobs {where_sql} ORDER BY created_at DESC LIMIT ?",
            tuple(params + [limit]),
        )
        jobs: List[JobPosting] = []
        for row in rows:
            row["requirements"] = self.store.loads(row.get("requirements"), [])
            posted = row.get("posted_date")
            if posted:
                try:
                    row["posted_date"] = datetime.fromisoformat(posted)
                except ValueError:
                    row["posted_date"] = None
            created = row.get("created_at")
            if created:
                try:
                    row["created_at"] = datetime.fromisoformat(created)
                except ValueError:
                    row["created_at"] = datetime.utcnow()
            jobs.append(JobPosting(**row))
        return jobs

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[JobPosting]:
        """Update job posting.

        Args:
            job_id: Job ID
            updates: Fields to update

        Returns:
            Updated job posting or None
        """
        existing = self.get_job(job_id)
        if not existing:
            return None
        patch = dict(updates or {})
        merged = existing.model_copy(update=patch)

        update_row: Dict[str, Any] = {}
        for key in (
            "title",
            "company",
            "location",
            "description",
            "url",
            "source",
            "salary_range",
            "job_type",
        ):
            if key in patch:
                update_row[key] = getattr(merged, key)
        if "requirements" in patch:
            update_row["requirements"] = self.store.dumps(merged.requirements)
        if "posted_date" in patch:
            update_row["posted_date"] = merged.posted_date.isoformat() if merged.posted_date else None

        if update_row:
            self.store.update("jobs", job_id, update_row)
        return self.get_job(job_id)

    def delete_job(self, job_id: str) -> bool:
        """Delete job posting.

        Args:
            job_id: Job ID

        Returns:
            Success status
        """
        return self.store.delete("jobs", job_id) > 0

    def search_jobs(self, query: str, limit: int = 50) -> List[JobPosting]:
        """Search jobs by query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching jobs
        """
        q = (query or "").strip()
        if not q:
            return self.list_jobs(limit=limit)
        like = f"%{q.lower()}%"
        rows = self.store.fetch_all(
            """
            SELECT * FROM jobs
            WHERE LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(description) LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (like, like, like, limit),
        )
        jobs: List[JobPosting] = []
        for row in rows:
            row["requirements"] = self.store.loads(row.get("requirements"), [])
            posted = row.get("posted_date")
            if posted:
                try:
                    row["posted_date"] = datetime.fromisoformat(posted)
                except ValueError:
                    row["posted_date"] = None
            created = row.get("created_at")
            if created:
                try:
                    row["created_at"] = datetime.fromisoformat(created)
                except ValueError:
                    row["created_at"] = datetime.utcnow()
            jobs.append(JobPosting(**row))
        return jobs
