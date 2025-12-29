"""Profile agent for parsing and managing user profiles."""

import re
from typing import Any, Dict, Iterable, List
from ..utils.validators import sanitize_string, validate_email, validate_phone
from .base import BaseAgent


class ProfileAgent(BaseAgent):
    """Agent responsible for parsing resumes and building user profiles."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="ProfileAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resume and build user profile.

        Args:
            input_data: Contains resume file path or text

        Returns:
            Structured user profile data
        """
        source = input_data or {}
        profile: Dict[str, Any] = {}
        base_profile = source.get("profile") if isinstance(source, dict) else {}
        if isinstance(base_profile, dict):
            profile.update(base_profile)

        resume_text = ""
        if isinstance(source, dict):
            resume_text = str(
                source.get("resume_text")
                or source.get("text")
                or profile.get("resume_text")
                or ""
            )

            path = source.get("resume_path") or source.get("file_path")
            if not resume_text and path:
                try:
                    with open(path, "r", encoding="utf-8") as handle:
                        resume_text = handle.read()
                except OSError:
                    resume_text = ""

        def _extract_email(text: str) -> str | None:
            match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
            if match:
                candidate = match.group(0)
                if validate_email(candidate):
                    return candidate
            return None

        def _extract_phone(text: str) -> str | None:
            match = re.search(r"\+?\d[\d\-\s\(\)]{8,}\d", text)
            if not match:
                return None
            cleaned = re.sub(r"[^\d+]", "", match.group(0))
            return cleaned if validate_phone(cleaned) else None

        def _extract_location(text: str) -> str | None:
            match = re.search(r"location\s*[:\-]\s*(.+)", text, re.IGNORECASE)
            if match:
                return sanitize_string(match.group(1).splitlines()[0])
            return None

        def _extract_skills(text: str) -> List[str]:
            match = re.search(r"skills?\s*[:\-]\s*(.+)", text, re.IGNORECASE)
            if not match:
                return []
            raw = match.group(1)
            candidates = re.split(r"[,\n;•]|and", raw)
            skills: List[str] = []
            for skill in candidates:
                cleaned = sanitize_string(skill)
                if cleaned:
                    skills.append(cleaned)
            return skills

        def _extract_experience(text: str) -> int | None:
            matches = re.findall(r"(\d+)\s*\+?\s*years", text, re.IGNORECASE)
            if not matches:
                return None
            return max(int(years) for years in matches)

        def _first_nonempty_line(text: str) -> str | None:
            for line in text.splitlines():
                cleaned = sanitize_string(line)
                if cleaned:
                    return cleaned
            return None

        def _merge_list(existing: Iterable[Any] | None, new_items: Iterable[Any]) -> List[Any]:
            seen = set()
            merged: List[Any] = []
            for item in (existing or []):
                if item is None:
                    continue
                key = str(item).strip()
                if key and key.lower() not in seen:
                    merged.append(item)
                    seen.add(key.lower())
            for item in new_items:
                key = str(item).strip()
                if key and key.lower() not in seen:
                    merged.append(item if not isinstance(item, str) else sanitize_string(item))
                    seen.add(key.lower())
            return merged

        if resume_text:
            profile["resume_text"] = resume_text

        if not profile.get("email") and resume_text:
            email = _extract_email(resume_text)
            if email:
                profile["email"] = email

        if not profile.get("phone") and resume_text:
            phone = _extract_phone(resume_text)
            if phone:
                profile["phone"] = phone

        if not profile.get("location") and resume_text:
            location = _extract_location(resume_text)
            if location:
                profile["location"] = location

        skills = profile.get("skills", [])
        if not skills and resume_text:
            skills = _extract_skills(resume_text)
        profile["skills"] = _merge_list(skills, [])

        if profile.get("experience_years") is None and resume_text:
            years = _extract_experience(resume_text)
            if years is not None:
                profile["experience_years"] = years

        if not profile.get("name") and resume_text:
            name_candidate = _first_nonempty_line(resume_text)
            if name_candidate and "@" not in name_candidate.lower() and "skills" not in name_candidate.lower():
                profile["name"] = name_candidate

        self.state["profile"] = profile

        return {"status": "success", "profile": profile}
