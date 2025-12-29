"""LinkedIn client for profile and job scraping."""

from __future__ import annotations

from typing import List, Dict, Any


class LinkedInClient:
    """Client for LinkedIn operations."""

    def __init__(self, credentials: Dict[str, str] = None):
        """Initialize LinkedIn client.

        Args:
            credentials: LinkedIn credentials
        """
        self.credentials = credentials

    def search_jobs(self, keywords: str, location: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs on LinkedIn.

        Args:
            keywords: Search keywords
            location: Job location
            limit: Maximum results

        Returns:
            List of job postings
        """
        # Note: LinkedIn blocks unauthenticated scraping and their TOS prohibits automated scraping.
        # Phase 1 keeps a "pluggable" interface; callers can provide seed jobs for demos/tests.
        seed = []
        if isinstance(self.credentials, dict):
            seed = self.credentials.get("seed_jobs") or []
        results: List[Dict[str, Any]] = []
        for job in seed:
            if not isinstance(job, dict):
                continue
            results.append(job)
            if len(results) >= limit:
                break
        return results

    def get_profile(self, profile_url: str) -> Dict[str, Any]:
        """Get LinkedIn profile information.

        Args:
            profile_url: LinkedIn profile URL

        Returns:
            Profile data
        """
        # Phase 1: return minimal structure; real scraping requires OAuth or approved API access.
        if not profile_url:
            return {}
        return {"url": profile_url}

    def find_contacts(self, company: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Find contacts at a company.

        Args:
            company: Company name
            keywords: Keywords for role filtering

        Returns:
            List of contacts
        """
        # Phase 1: optional seeded contacts for demo flows.
        seed = []
        if isinstance(self.credentials, dict):
            seed = self.credentials.get("seed_contacts") or []
        results: List[Dict[str, Any]] = []
        company_lc = (company or "").strip().lower()
        keywords_lc = {str(k).strip().lower() for k in (keywords or []) if str(k).strip()}

        for contact in seed:
            if not isinstance(contact, dict):
                continue
            if company_lc and str(contact.get("company", "")).strip().lower() != company_lc:
                continue
            if keywords_lc:
                blob = " ".join(
                    [
                        str(contact.get("position", "")),
                        str(contact.get("title", "")),
                        str(contact.get("headline", "")),
                    ]
                ).lower()
                if not any(k in blob for k in keywords_lc):
                    continue
            results.append(contact)
        return results
