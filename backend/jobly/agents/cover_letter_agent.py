"""Cover letter agent for generating personalized cover letters."""

from typing import Any, Dict
from .base import BaseAgent


class CoverLetterAgent(BaseAgent):
    """Agent responsible for generating cover letters."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="CoverLetterAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cover letter for job application.

        Args:
            input_data: User profile and job details

        Returns:
            Generated cover letter
        """
        profile = input_data.get("profile", {}) or {}
        job = input_data.get("job", {}) or {}
        company_info = input_data.get("company_info", "") or ""

        applicant_name = profile.get("name") or "Candidate"
        job_title = job.get("title") or "the role"
        company = job.get("company") or "your team"
        location = job.get("location") or ""

        profile_skills = profile.get("skills") or []
        job_requirements = job.get("requirements") or []
        matched_skills = [skill for skill in profile_skills if skill in job_requirements]
        highlighted_skills = matched_skills[:3] or profile_skills[:3]
        skills_line = ", ".join(highlighted_skills)

        experience_years = profile.get("experience_years")
        experience_line = (
            f"With {experience_years}+ years of experience" if experience_years else "With a strong background"
        )

        company_hook = f" After researching {company}, {company_info.strip()}" if company_info.strip() else ""
        location_note = f" in {location}" if location else ""

        paragraphs = [
            f"Dear {company} Hiring Team,",
            (
                f"I am excited to apply for {job_title}{location_note}. "
                f"{experience_line}, I have developed expertise in {skills_line or 'key areas aligned to this role'}."
            ),
            (
                f"In my recent work, I have consistently delivered impact through collaboration, ownership, "
                f"and measurable outcomes. I am confident these strengths translate well to {company}'s needs."
                f"{company_hook}"
            ),
            (
                "I would welcome the opportunity to discuss how my background can support your goals. "
                "Thank you for your consideration."
            ),
            f"Sincerely,\n{applicant_name}",
        ]

        cover_letter = "\n\n".join([paragraph for paragraph in paragraphs if paragraph])
        return {"status": "success", "cover_letter": cover_letter}
