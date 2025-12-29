"""Resume tailor agent for customizing resumes for specific jobs."""

from typing import Any, Dict
from .base import BaseAgent


class ResumeTailorAgent(BaseAgent):
    """Agent responsible for tailoring resumes to specific job postings."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="ResumeTailorAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tailor resume for specific job.

        Args:
            input_data: User profile and target job

        Returns:
            Tailored resume content
        """
        profile = input_data.get("profile") if isinstance(input_data, dict) else {}
        job = input_data.get("job") if isinstance(input_data, dict) else {}
        base_resume = (input_data.get("resume") or "").strip() if isinstance(input_data, dict) else ""

        def _clean_list(values: Any) -> list[str]:
            if not values:
                return []
            cleaned = []
            for value in values:
                if value is None:
                    continue
                text = str(value).strip()
                if text:
                    cleaned.append(text)
            return cleaned

        def _extract_keywords(job_data: Dict[str, Any]) -> set[str]:
            keywords = {kw.lower() for kw in _clean_list(job_data.get("requirements"))}
            keywords.update({kw.lower() for kw in _clean_list(job_data.get("skills"))})
            if not keywords:
                description = str(job_data.get("description", "") or "")
                for token in description.replace("/", " ").replace(",", " ").split():
                    token = token.strip().lower()
                    if len(token) > 3:
                        keywords.add(token)
            return {kw for kw in keywords if kw}

        def _prioritize_skills(skills: list[str], keywords: set[str]) -> list[str]:
            seen = set()
            prioritized = []
            for skill in skills:
                key = skill.lower()
                if key in seen:
                    continue
                if key in keywords:
                    prioritized.append(skill)
                    seen.add(key)
            for skill in skills:
                key = skill.lower()
                if key not in seen:
                    prioritized.append(skill)
                    seen.add(key)
            return prioritized

        def _extract_bullets(entry: Any) -> list[str]:
            if isinstance(entry, list):
                return [str(item).strip() for item in entry if str(item).strip()]
            if isinstance(entry, str):
                return [seg.strip() for seg in entry.replace("\n", " ").split(".") if seg.strip()]
            return []

        def _filter_bullets(bullets: list[str], keywords: set[str]) -> list[str]:
            if not keywords:
                return bullets[:3]
            ranked = []
            for bullet in bullets:
                score = sum(1 for kw in keywords if kw in bullet.lower())
                ranked.append((score, bullet))
            ranked.sort(key=lambda item: item[0], reverse=True)
            filtered = [bullet for score, bullet in ranked if bullet]
            return filtered[:3] if filtered else bullets[:3]

        job_title = str(job.get("title", "")).strip() or "the target role"
        company = str(job.get("company", "")).strip()
        company_phrase = f" at {company}" if company else ""
        profile_skills = _clean_list(profile.get("skills"))
        job_keywords = _extract_keywords(job)
        prioritized_skills = _prioritize_skills(profile_skills, job_keywords)
        matched_skills = [skill for skill in prioritized_skills if skill.lower() in job_keywords]

        name = str(profile.get("name", "")).strip()
        location = str(profile.get("location", "")).strip()
        experience_years = profile.get("experience_years")
        experience_note = f"{experience_years}+ years" if experience_years else "Proven"
        summary_line = (
            f"{experience_note} experience tailoring to {job_title}{company_phrase}. "
            f"Strengths: {', '.join(matched_skills[:5] or prioritized_skills[:5]) or 'relevant expertise'}."
        )

        sections = []

        header_parts = [name] if name else []
        contact_bits = [bit for bit in [location, profile.get("email"), profile.get("phone")] if bit]
        if contact_bits:
            header_parts.append(" | ".join(contact_bits))
        if header_parts:
            sections.append("\n".join(header_parts))

        sections.append("SUMMARY\n" + summary_line)

        if prioritized_skills:
            sections.append("CORE SKILLS\n" + ", ".join(prioritized_skills))

        work_history = profile.get("work_history") or []
        experience_lines = []
        for role in work_history:
            title = str(role.get("title", "")).strip() or "Experience"
            company_name = str(role.get("company", "")).strip()
            duration = str(role.get("duration", "")).strip()
            header = " | ".join(part for part in [title, company_name, duration] if part)
            if header:
                experience_lines.append(header)
            bullets = _filter_bullets(_extract_bullets(role.get("description")), job_keywords)
            for bullet in bullets:
                experience_lines.append(f"- {bullet}")
        if experience_lines:
            sections.append("EXPERIENCE\n" + "\n".join(experience_lines))

        education_entries = profile.get("education") or []
        education_lines = []
        for edu in education_entries:
            school = str(edu.get("school", "")).strip()
            degree = str(edu.get("degree", "")).strip()
            field = str(edu.get("field", "")).strip()
            year = str(edu.get("year", "")).strip()
            line = ", ".join(part for part in [degree, field] if part)
            education_lines.append(" | ".join(part for part in [school, line, year] if part))
        if education_lines:
            sections.append("EDUCATION\n" + "\n".join(education_lines))

        tailored_resume = "\n\n".join(section for section in sections if section)
        if base_resume and len(base_resume) > len(tailored_resume):
            if tailored_resume:
                tailored_resume = f"{tailored_resume}\n\nORIGINAL RESUME\n{base_resume}"
            else:
                tailored_resume = base_resume

        return {"status": "success", "tailored_resume": tailored_resume}
