"""Job ranker agent for scoring and ranking job opportunities."""

from typing import Any, Dict
from .base import BaseAgent


class JobRankerAgent(BaseAgent):
    """Agent responsible for ranking jobs based on user profile fit."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="JobRankerAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rank jobs based on profile match.

        Args:
            input_data: User profile and list of jobs

        Returns:
            Ranked list of jobs with scores
        """
        profile = input_data.get("profile") if isinstance(input_data, dict) else {}
        jobs = input_data.get("jobs") if isinstance(input_data, dict) else input_data
        jobs = jobs or []

        def _get_value(item: Any, key: str, default: Any = None) -> Any:
            if isinstance(item, dict):
                return item.get(key, default)
            return getattr(item, key, default)

        def _normalize_set(values: Any) -> set[str]:
            if not values:
                return set()
            return {str(value).strip().lower() for value in values if value}

        preferred_types = {
            str(t).lower() for t in self.config.get("preferred_job_types", []) or []
        }
        profile_skills = _normalize_set(_get_value(profile, "skills", []))
        profile_location = str(_get_value(profile, "location", "") or "").lower()
        profile_experience = _get_value(profile, "experience_years", 0) or 0

        ranked_jobs = []

        for job in jobs:
            requirements = _normalize_set(_get_value(job, "requirements", []))
            matched_skills = profile_skills.intersection(requirements)
            missing_skills = requirements - profile_skills

            skill_score = (len(matched_skills) / max(len(requirements), 1)) * 70

            job_experience = _get_value(job, "experience_years")
            if isinstance(job_experience, (int, float)) and job_experience > 0:
                experience_ratio = max(0.0, min(1.0, profile_experience / job_experience))
                experience_score = experience_ratio * 15
            else:
                experience_score = 7.5 if profile_experience else 0.0

            location = str(_get_value(job, "location", "") or "").lower()
            if not profile_location or not location:
                location_score = 5.0
            elif "remote" in location or "remote" in profile_location:
                location_score = 10.0
            elif profile_location == location:
                location_score = 10.0
            else:
                location_score = 0.0

            job_type = str(_get_value(job, "job_type", "") or "").lower()
            if preferred_types:
                job_type_score = 5.0 if job_type in preferred_types else 0.0
            else:
                job_type_score = 2.5 if job_type else 0.0

            score = min(skill_score + experience_score + location_score + job_type_score, 100.0)

            job_payload = job.copy() if isinstance(job, dict) else {"job": job}
            job_payload.update(
                {
                    "score": round(score, 2),
                    "matched_skills": sorted(matched_skills),
                    "missing_skills": sorted(missing_skills),
                }
            )
            ranked_jobs.append(job_payload)

        ranked_jobs.sort(key=lambda j: j.get("score", 0), reverse=True)

        return {"status": "success", "ranked_jobs": ranked_jobs}
