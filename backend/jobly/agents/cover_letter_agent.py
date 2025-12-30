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

        # Try LLM-based generation first
        if self.llm and self.llm.is_available():
            try:
                cover_letter = await self._generate_with_llm(profile, job, company_info)
                return {"status": "success", "cover_letter": cover_letter}
            except Exception as e:
                # Fall back to template-based generation
                print(f"LLM generation failed: {e}. Falling back to template.")

        # Fallback: template-based generation
        cover_letter = self._generate_template_based(profile, job, company_info)
        return {"status": "success", "cover_letter": cover_letter}

    async def _generate_with_llm(
        self, profile: Dict[str, Any], job: Dict[str, Any], company_info: str
    ) -> str:
        """Generate cover letter using LLM.

        Args:
            profile: User profile data
            job: Job posting details
            company_info: Additional company information

        Returns:
            Generated cover letter
        """
        system_prompt = """You are an expert career counselor and professional cover letter writer.
Generate compelling, personalized cover letters that:
- Highlight relevant experience and skills
- Show genuine interest in the company and role
- Maintain a professional yet personable tone
- Are concise (3-4 paragraphs)
- Avoid clichés and generic statements"""

        user_prompt = f"""Generate a cover letter for this job application:

JOB DETAILS:
- Title: {job.get('title', 'N/A')}
- Company: {job.get('company', 'N/A')}
- Location: {job.get('location', 'N/A')}
- Description: {job.get('description', 'N/A')}
- Requirements: {', '.join(job.get('requirements', [])) or 'N/A'}

CANDIDATE PROFILE:
- Name: {profile.get('name', 'Candidate')}
- Email: {profile.get('email', '')}
- Skills: {', '.join(profile.get('skills', [])) or 'N/A'}
- Experience: {profile.get('experience_years', 'N/A')} years
- Location: {profile.get('location', 'N/A')}

COMPANY RESEARCH:
{company_info or 'No additional information available'}

Generate a personalized, professional cover letter that demonstrates why this candidate is a strong fit for the role."""

        return await self.llm.acomplete(user_prompt, system=system_prompt, temperature=0.7)

    def _generate_template_based(
        self, profile: Dict[str, Any], job: Dict[str, Any], company_info: str
    ) -> str:
        """Generate cover letter using template (fallback method).

        Args:
            profile: User profile data
            job: Job posting details
            company_info: Additional company information

        Returns:
            Generated cover letter
        """
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
            f"With {experience_years}+ years of experience"
            if experience_years
            else "With a strong background"
        )

        company_hook = (
            f" After researching {company}, {company_info.strip()}" if company_info.strip() else ""
        )
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

        return "\n\n".join([paragraph for paragraph in paragraphs if paragraph])
