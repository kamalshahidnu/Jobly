"""Indeed job board scraper."""

import time
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode, quote_plus
import requests
from bs4 import BeautifulSoup
from ...utils.rate_limiter import RateLimiter


class IndeedScraper:
    """Scraper for Indeed job board."""

    BASE_URL = "https://www.indeed.com"

    def __init__(self, rate_limit_calls: int = 10, rate_limit_window: float = 60.0):
        """Initialize Indeed scraper.

        Args:
            rate_limit_calls: Maximum calls per window
            rate_limit_window: Time window in seconds
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        self.rate_limiter = RateLimiter(rate_limit_calls, rate_limit_window)

    def search_jobs(
        self,
        keywords: str,
        location: str = "",
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search for jobs on Indeed.

        Args:
            keywords: Search keywords
            location: Job location
            job_type: Job type filter (fulltime, parttime, contract, temporary, internship)
            experience_level: Experience level (entry_level, mid_level, senior_level)
            limit: Maximum results

        Returns:
            List of job postings
        """
        jobs = []
        start = 0
        page_size = 10

        try:
            while len(jobs) < limit:
                # Build search URL
                params = {
                    "q": keywords,
                    "l": location,
                    "start": start,
                }

                if job_type:
                    params["jt"] = job_type

                if experience_level:
                    params["explvl"] = experience_level

                url = f"{self.BASE_URL}/jobs?{urlencode(params)}"

                # Rate limit
                self.rate_limiter.wait_if_needed()

                # Fetch page
                response = self.session.get(url, timeout=15)
                response.raise_for_status()

                # Parse results
                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon"))

                if not job_cards:
                    # Try alternative selector
                    job_cards = soup.find_all("td", class_="resultContent")

                if not job_cards:
                    break

                for card in job_cards:
                    if len(jobs) >= limit:
                        break

                    try:
                        job_data = self._parse_job_card(card)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        print(f"Error parsing job card: {e}")
                        continue

                start += page_size

                # If we didn't find any jobs on this page, stop
                if not job_cards:
                    break

                # Be respectful with delays
                time.sleep(1)

        except Exception as e:
            print(f"Error searching Indeed: {e}")

        return jobs[:limit]

    def _parse_job_card(self, card: Any) -> Optional[Dict[str, Any]]:
        """Parse a job card element.

        Args:
            card: BeautifulSoup job card element

        Returns:
            Parsed job data
        """
        try:
            # Extract job ID and URL
            job_id = None
            job_url = None
            link = card.find("a", class_=re.compile(r"jcs-JobTitle"))
            if not link:
                link = card.find("a", href=re.compile(r"/rc/clk"))
            if not link:
                link = card.find("a")

            if link and link.get("href"):
                href = link["href"]
                if href.startswith("/"):
                    job_url = f"{self.BASE_URL}{href}"
                else:
                    job_url = href

                # Extract job ID from URL
                match = re.search(r"jk=([a-zA-Z0-9]+)", href)
                if match:
                    job_id = match.group(1)

            # Extract title
            title = ""
            title_elem = card.find("h2", class_=re.compile(r"jobTitle"))
            if title_elem:
                title = title_elem.get_text(strip=True)
            elif link:
                title = link.get_text(strip=True)

            # Extract company
            company = ""
            company_elem = card.find("span", class_="companyName")
            if not company_elem:
                company_elem = card.find("span", {"data-testid": "company-name"})
            if company_elem:
                company = company_elem.get_text(strip=True)

            # Extract location
            location = ""
            location_elem = card.find("div", class_="companyLocation")
            if not location_elem:
                location_elem = card.find("div", {"data-testid": "text-location"})
            if location_elem:
                location = location_elem.get_text(strip=True)

            # Extract salary (if available)
            salary = ""
            salary_elem = card.find("div", class_=re.compile(r"salary"))
            if not salary_elem:
                salary_elem = card.find("span", class_="salary-snippet")
            if salary_elem:
                salary = salary_elem.get_text(strip=True)

            # Extract description snippet
            description = ""
            desc_elem = card.find("div", class_="job-snippet")
            if not desc_elem:
                desc_elem = card.find("div", class_=re.compile(r"jobCardShelfContainer"))
            if desc_elem:
                description = desc_elem.get_text(strip=True)

            # Extract posted date
            posted_date = ""
            date_elem = card.find("span", class_="date")
            if not date_elem:
                date_elem = card.find("span", {"data-testid": "myJobsStateDate"})
            if date_elem:
                posted_date = date_elem.get_text(strip=True)

            if not title or not job_url:
                return None

            return {
                "job_id": job_id or job_url,
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "description": description,
                "url": job_url,
                "posted_date": posted_date,
                "source": "Indeed",
            }

        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None

    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """Get full job details from job URL.

        Args:
            job_url: Indeed job URL

        Returns:
            Detailed job information
        """
        try:
            self.rate_limiter.wait_if_needed()

            response = self.session.get(job_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract full description
            description = ""
            desc_elem = soup.find("div", id="jobDescriptionText")
            if not desc_elem:
                desc_elem = soup.find("div", class_=re.compile(r"jobsearch-jobDescriptionText"))
            if desc_elem:
                description = desc_elem.get_text(strip=True, separator="\n")

            # Extract job title
            title = ""
            title_elem = soup.find("h1", class_=re.compile(r"jobsearch-JobInfoHeader-title"))
            if title_elem:
                title = title_elem.get_text(strip=True)

            # Extract company
            company = ""
            company_elem = soup.find("div", {"data-company-name": True})
            if company_elem:
                company = company_elem.get("data-company-name")

            # Extract requirements from description
            requirements = self._extract_requirements(description)
            skills = self._extract_skills(description)

            return {
                "title": title,
                "company": company,
                "description": description,
                "requirements": requirements,
                "skills": skills,
                "url": job_url,
                "source": "Indeed",
            }

        except Exception as e:
            print(f"Error fetching job details: {e}")
            return None

    def _extract_requirements(self, description: str) -> List[str]:
        """Extract requirements from job description.

        Args:
            description: Job description text

        Returns:
            List of requirements
        """
        requirements = []

        # Look for common requirement patterns
        lines = description.split("\n")
        in_requirements_section = False

        for line in lines:
            line = line.strip()
            lower = line.lower()

            # Check for section headers
            if any(keyword in lower for keyword in ["requirements", "qualifications", "what you need", "you have"]):
                in_requirements_section = True
                continue

            if any(keyword in lower for keyword in ["responsibilities", "about", "benefits", "we offer"]):
                in_requirements_section = False

            # Extract bullet points in requirements section
            if in_requirements_section and (line.startswith("•") or line.startswith("-") or line.startswith("*")):
                req = re.sub(r"^[•\-\*]\s*", "", line)
                if req:
                    requirements.append(req)

        return requirements[:10]  # Limit to top 10

    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description.

        Args:
            description: Job description text

        Returns:
            List of skills
        """
        # Common technical skills to look for
        skill_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node.js", "django", "flask", "fastapi", "sql", "postgresql", "mysql",
            "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "gcp",
            "git", "ci/cd", "agile", "scrum", "rest", "graphql", "microservices",
            "machine learning", "data science", "ai", "tensorflow", "pytorch",
        ]

        description_lower = description.lower()
        found_skills = []

        for skill in skill_keywords:
            if skill in description_lower:
                # Preserve original casing
                found_skills.append(skill.title())

        return found_skills
