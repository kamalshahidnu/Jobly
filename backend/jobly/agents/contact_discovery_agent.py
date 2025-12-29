"""Contact discovery agent for finding hiring managers and recruiters."""

import re
from typing import Any, Dict, List, Optional, Tuple
from .base import BaseAgent


class ContactDiscoveryAgent(BaseAgent):
    """Agent responsible for discovering contact information."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="ContactDiscoveryAgent", config=config)

    def _infer_department(self, role: str) -> str:
        role_lower = role.lower()
        departments: Dict[str, Tuple[str, ...]] = {
            "Engineering": (
                "engineer",
                "developer",
                "software",
                "backend",
                "frontend",
                "full stack",
                "devops",
                "sre",
            ),
            "Product": ("product", "pm"),
            "Design": ("design", "ux", "ui", "research"),
            "Data": ("data", "analytics", "ml", "ai", "scientist", "analysis"),
            "Marketing": ("marketing", "growth", "brand", "content"),
            "Sales": ("sales", "account", "customer", "success", "bd"),
            "People": ("recruit", "talent", "hr", "people"),
        }

        for department, keywords in departments.items():
            if any(keyword in role_lower for keyword in keywords):
                return department
        return "General"

    def _target_titles(self, department: str) -> List[Tuple[str, str]]:
        dept_targets: Dict[str, List[Tuple[str, str]]] = {
            "Engineering": [
                ("Engineering Manager", "high"),
                ("Director of Engineering", "medium"),
                ("Technical Recruiter", "medium"),
            ],
            "Product": [
                ("Product Manager", "high"),
                ("Director of Product", "medium"),
                ("Technical Recruiter", "medium"),
            ],
            "Design": [
                ("Design Lead", "high"),
                ("Director of Design", "medium"),
                ("Recruiter", "medium"),
            ],
            "Data": [
                ("Head of Data", "high"),
                ("Data Engineering Manager", "medium"),
                ("Technical Recruiter", "medium"),
            ],
            "Marketing": [
                ("Marketing Manager", "high"),
                ("Head of Marketing", "medium"),
                ("Recruiter", "medium"),
            ],
            "Sales": [
                ("Sales Manager", "high"),
                ("Head of Sales", "medium"),
                ("Recruiter", "medium"),
            ],
            "People": [
                ("Senior Recruiter", "high"),
                ("Talent Acquisition Lead", "medium"),
                ("HR Manager", "medium"),
            ],
        }

        base_targets = [
            ("Hiring Manager", "high"),
            ("Recruiter", "medium"),
            ("Talent Acquisition", "medium"),
        ]

        combined = dept_targets.get(department, []) + base_targets
        seen = set()
        unique_targets: List[Tuple[str, str]] = []
        for title, priority in combined:
            key = title.lower()
            if key in seen:
                continue
            seen.add(key)
            unique_targets.append((title, priority))
        return unique_targets

    def _guess_domain(self, company: str, provided: Optional[str]) -> Optional[str]:
        if provided:
            return (
                provided.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
                .strip()
            )

        slug = re.sub(r"[^a-z0-9]", "", company.lower())
        if not slug:
            return None
        return f"{slug}.com"

    def _build_search_keywords(
        self,
        company: str,
        role: str,
        title: str,
        department: str,
        location: Optional[str],
        extra_keywords: Optional[List[str]],
    ) -> List[str]:
        keywords = [
            company,
            title,
            department,
            role,
            location or "",
            "hiring",
        ]
        if extra_keywords:
            keywords.extend(extra_keywords)

        seen = set()
        deduped: List[str] = []
        for keyword in keywords:
            cleaned = keyword.strip()
            if not cleaned:
                continue
            lower = cleaned.lower()
            if lower in seen:
                continue
            seen.add(lower)
            deduped.append(cleaned)
        return deduped

    def _email_for_title(self, title: str, domain: Optional[str]) -> Optional[str]:
        if not domain:
            return None

        lowered = title.lower()
        if "recruit" in lowered or "talent" in lowered:
            return f"recruiting@{domain}"
        if "hr" in lowered or "people" in lowered:
            return f"hr@{domain}"
        if "manager" in lowered or "director" in lowered or "head" in lowered:
            return f"hiring@{domain}"
        return f"careers@{domain}"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Discover hiring managers and recruiters.

        Args:
            input_data: Company and job information

        Returns:
            List of contacts with emails
        """
        company = str(
            input_data.get("company") or input_data.get("company_name") or ""
        ).strip()
        role = str(input_data.get("role") or input_data.get("job_title") or "").strip()

        if not company:
            return {"status": "error", "error": "company_required"}

        department = self._infer_department(role)
        domain = self._guess_domain(company, input_data.get("company_domain"))
        location = input_data.get("location")
        extra_keywords = input_data.get("keywords")

        existing_titles = {
            str(contact.get("position") or contact.get("title") or "")
            .lower()
            .strip()
            for contact in input_data.get("existing_contacts", [])
            if isinstance(contact, dict)
        }

        contacts = []
        for title, priority in self._target_titles(department):
            if title.lower() in existing_titles:
                continue

            search_keywords = self._build_search_keywords(
                company, role, title, department, location, extra_keywords
            )
            contacts.append(
                {
                    "name": f"Likely {title}",
                    "email": self._email_for_title(title, domain),
                    "company": company,
                    "position": title,
                    "department": department,
                    "priority": priority,
                    "search_keywords": search_keywords,
                    "search_hint": f"LinkedIn: {' '.join(search_keywords)}",
                }
            )

        return {"status": "success", "contacts": contacts}
