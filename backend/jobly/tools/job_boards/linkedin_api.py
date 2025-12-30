"""LinkedIn API client for job search and profile access."""

import os
from typing import List, Dict, Any, Optional
import requests
from ...config.settings import settings
from ...utils.rate_limiter import RateLimiter


class LinkedInAPIClient:
    """Client for LinkedIn API integration.

    Note: LinkedIn's official API requires partnership for job posting access.
    This client provides:
    1. Integration with LinkedIn's official APIs (where available)
    2. Fallback to manual job seeding for development/testing
    3. Guidance for setting up proper LinkedIn integration

    For production use, you'll need:
    - LinkedIn Partner API access OR
    - LinkedIn Talent Solutions subscription OR
    - Manual job data collection via authorized means
    """

    BASE_URL = "https://api.linkedin.com/v2"
    AUTH_URL = "https://www.linkedin.com/oauth/v2"

    def __init__(
        self,
        access_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """Initialize LinkedIn API client.

        Args:
            access_token: LinkedIn OAuth access token
            client_id: LinkedIn app client ID
            client_secret: LinkedIn app client secret
        """
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")

        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
            })

        self.rate_limiter = RateLimiter(10, 60.0)

    def is_authenticated(self) -> bool:
        """Check if client is authenticated with LinkedIn API.

        Returns:
            True if authenticated
        """
        return bool(self.access_token)

    def get_authorization_url(self, redirect_uri: str, scope: List[str]) -> str:
        """Generate OAuth authorization URL.

        Args:
            redirect_uri: OAuth redirect URI
            scope: List of permission scopes

        Returns:
            Authorization URL
        """
        if not self.client_id:
            raise ValueError("LinkedIn client_id not configured")

        from urllib.parse import urlencode

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scope),
        }

        return f"{self.AUTH_URL}/authorization?{urlencode(params)}"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[str]:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code
            redirect_uri: OAuth redirect URI

        Returns:
            Access token
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("LinkedIn client_id and client_secret required")

        try:
            response = requests.post(
                f"{self.AUTH_URL}/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            return self.access_token

        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None

    def get_profile(self, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get the authenticated user's LinkedIn profile.

        Args:
            fields: Fields to retrieve

        Returns:
            Profile data
        """
        if not self.is_authenticated():
            print("Not authenticated with LinkedIn API")
            return None

        try:
            self.rate_limiter.wait_if_needed()

            default_fields = ["id", "firstName", "lastName", "headline", "profilePicture"]
            fields = fields or default_fields

            url = f"{self.BASE_URL}/me?projection=({','.join(fields)})"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None

    def search_jobs(
        self,
        keywords: str,
        location: str = "",
        limit: int = 50,
        seed_jobs: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for jobs on LinkedIn.

        Note: LinkedIn's Job Search API is not publicly available.
        This method provides:
        1. Integration point for partner API if available
        2. Fallback to seed data for development/testing
        3. Guidance for manual data collection

        Args:
            keywords: Search keywords
            location: Job location
            limit: Maximum results
            seed_jobs: Seed jobs for development/testing

        Returns:
            List of job postings
        """
        # If you have LinkedIn Partner API access, implement here
        if self.is_authenticated() and self._has_job_search_access():
            try:
                return self._search_jobs_via_api(keywords, location, limit)
            except Exception as e:
                print(f"API search failed: {e}")

        # Fallback: Use seed jobs for development
        if seed_jobs:
            filtered_jobs = []
            keywords_lower = keywords.lower()
            location_lower = location.lower()

            for job in seed_jobs:
                if len(filtered_jobs) >= limit:
                    break

                # Simple keyword matching
                title = job.get("title", "").lower()
                description = job.get("description", "").lower()
                job_location = job.get("location", "").lower()

                if keywords_lower in title or keywords_lower in description:
                    if not location or location_lower in job_location:
                        filtered_jobs.append(job)

            return filtered_jobs

        # No data available
        print(
            "LinkedIn job search not available. Options:\n"
            "1. Apply for LinkedIn Partner Program: https://business.linkedin.com/talent-solutions\n"
            "2. Use LinkedIn Recruiter with API access\n"
            "3. Manually collect job data via authorized means\n"
            "4. Provide seed jobs for development/testing"
        )
        return []

    def _has_job_search_access(self) -> bool:
        """Check if the current token has job search permissions.

        Returns:
            True if job search is available
        """
        # Implement token scope validation here
        # For now, return False as job search API is not publicly available
        return False

    def _search_jobs_via_api(
        self, keywords: str, location: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Search jobs using LinkedIn Partner API.

        Args:
            keywords: Search keywords
            location: Job location
            limit: Maximum results

        Returns:
            List of job postings
        """
        # This is a placeholder for Partner API integration
        # Implement actual API calls if you have access
        raise NotImplementedError("LinkedIn Partner API integration required")

    def get_company_info(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get company information from LinkedIn.

        Args:
            company_id: LinkedIn company ID

        Returns:
            Company data
        """
        if not self.is_authenticated():
            return None

        try:
            self.rate_limiter.wait_if_needed()

            url = f"{self.BASE_URL}/organizations/{company_id}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"Error fetching company info: {e}")
            return None


# Utility function for creating LinkedIn job URLs
def create_linkedin_job_url(job_id: str) -> str:
    """Create a LinkedIn job URL from job ID.

    Args:
        job_id: LinkedIn job posting ID

    Returns:
        Full job URL
    """
    return f"https://www.linkedin.com/jobs/view/{job_id}"


def create_linkedin_search_url(keywords: str, location: str = "") -> str:
    """Create a LinkedIn job search URL.

    Args:
        keywords: Search keywords
        location: Job location

    Returns:
        Search URL
    """
    from urllib.parse import urlencode

    params = {"keywords": keywords}
    if location:
        params["location"] = location

    return f"https://www.linkedin.com/jobs/search?{urlencode(params)}"


# Development helper: Load seed jobs from file
def load_seed_jobs(seed_file: str) -> List[Dict[str, Any]]:
    """Load seed jobs from JSON file for development.

    Args:
        seed_file: Path to JSON file with seed jobs

    Returns:
        List of seed jobs
    """
    import json

    try:
        with open(seed_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading seed jobs: {e}")
        return []
