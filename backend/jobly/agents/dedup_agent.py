"""Deduplication agent for removing duplicate job postings."""

from typing import Any, Dict, List
from .base import BaseAgent


class DedupAgent(BaseAgent):
    """Agent responsible for deduplicating job postings."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="DedupAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate job postings.

        Args:
            input_data: List of job postings

        Returns:
            Deduplicated list of jobs
        """
        jobs = input_data.get("jobs") if isinstance(input_data, dict) else input_data
        jobs = jobs or []

        def _get_value(job: Any, key: str) -> Any:
            return job.get(key) if isinstance(job, dict) else getattr(job, key, None)

        def _normalize(value: Any) -> str:
            return str(value).strip().lower()

        seen = set()
        unique_jobs: List[Any] = []

        for job in jobs:
            url = _get_value(job, "url")
            job_id = _get_value(job, "id")
            title = _get_value(job, "title")
            company = _get_value(job, "company")
            location = _get_value(job, "location")

            if url:
                key = f"url:{_normalize(url)}"
            elif job_id:
                key = f"id:{_normalize(job_id)}"
            else:
                key_parts = (
                    _normalize(title) if title else "",
                    _normalize(company) if company else "",
                    _normalize(location) if location else "",
                )
                key = f"composite:{'|'.join(key_parts)}"

            if key in seen:
                continue

            seen.add(key)
            unique_jobs.append(job)

        return {"status": "success", "unique_jobs": unique_jobs}
