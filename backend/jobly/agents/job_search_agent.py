"""Job search agent for discovering job opportunities."""

from typing import Any, Dict
from .base import BaseAgent


class JobSearchAgent(BaseAgent):
    """Agent responsible for searching and scraping job postings."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="JobSearchAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for job postings based on criteria.

        Args:
            input_data: Search criteria (keywords, location, etc.)

        Returns:
            List of job postings
        """
        criteria = input_data if isinstance(input_data, dict) else {}
        keywords_raw = criteria.get("keywords") or criteria.get("query") or ""
        location_filter = str(criteria.get("location") or "remote").strip().lower()
        limit = int(criteria.get("limit") or self.config.get("default_limit", 50))

        if isinstance(keywords_raw, str):
            keywords = [k.strip().lower() for k in keywords_raw.replace(",", " ").split() if k.strip()]
        else:
            keywords = [str(k).strip().lower() for k in keywords_raw or [] if str(k).strip()]

        seed_jobs = []
        if isinstance(criteria.get("jobs"), list):
            seed_jobs.extend(criteria["jobs"])
        if isinstance(self.config.get("seed_jobs"), list):
            seed_jobs.extend(self.config["seed_jobs"])

        def _normalize(value: Any) -> str:
            return str(value or "").strip().lower()

        def _matches(job: Dict[str, Any]) -> bool:
            title = _normalize(job.get("title"))
            description = _normalize(job.get("description"))
            company = _normalize(job.get("company"))
            combined = " ".join((title, description, company))

            location = _normalize(job.get("location"))
            location_ok = (
                not location_filter
                or location_filter == "any"
                or "remote" in location_filter
                or "remote" in location
                or location_filter in location
            )

            keyword_ok = not keywords or any(k in combined for k in keywords)
            return keyword_ok and location_ok

        filtered = []
        seen = set()
        for job in seed_jobs:
            job_id = _normalize(job.get("id")) if isinstance(job, dict) else ""
            job_url = _normalize(job.get("url")) if isinstance(job, dict) else ""
            dedup_key = job_url or job_id
            if dedup_key and dedup_key in seen:
                continue
            if isinstance(job, dict) and _matches(job):
                if dedup_key:
                    seen.add(dedup_key)
                filtered.append(job)
            if len(filtered) >= limit:
                break

        return {"status": "success", "jobs": filtered[:limit]}
