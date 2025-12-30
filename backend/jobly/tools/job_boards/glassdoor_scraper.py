"""Glassdoor job board scraper."""

import time
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from ...utils.rate_limiter import RateLimiter


class GlassdoorScraper:
    """Scraper for Glassdoor job board."""

    BASE_URL = "https://www.glassdoor.com"

    def __init__(self, rate_limit_calls: int = 5, rate_limit_window: float = 60.0):
        """Initialize Glassdoor scraper.

        Args:
            rate_limit_calls: Maximum calls per window (Glassdoor is more strict)
            rate_limit_window: Time window in seconds
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
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
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search for jobs on Glassdoor.

        Args:
            keywords: Search keywords
            location: Job location
            job_type: Job type filter
            limit: Maximum results

        Returns:
            List of job postings
        """
        jobs = []

        try:
            # Build search URL - Glassdoor uses different URL patterns
            params = {
                "keyword": keywords,
                "location": location,
            }

            url = f"{self.BASE_URL}/Job/jobs.htm?{urlencode(params)}"

            # Rate limit
            self.rate_limiter.wait_if_needed()

            # Fetch page
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Parse results
            soup = BeautifulSoup(response.text, "html.parser")

            # Glassdoor uses dynamic loading - try to find job listings
            job_cards = soup.find_all("li", class_=re.compile(r"react-job-listing"))
            if not job_cards:
                job_cards = soup.find_all("div", {"data-test": "jobListing"})
            if not job_cards:
                job_cards = soup.find_all("article", class_=re.compile(r"job"))

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

            # Note: Glassdoor heavily uses JavaScript for dynamic loading
            # Full implementation would require Selenium or Playwright
            # This is a basic implementation that may have limited results

        except Exception as e:
            print(f"Error searching Glassdoor: {e}")

        return jobs[:limit]

    def _parse_job_card(self, card: Any) -> Optional[Dict[str, Any]]:
        """Parse a job card element.

        Args:
            card: BeautifulSoup job card element

        Returns:
            Parsed job data
        """
        try:
            # Extract title
            title = ""
            title_elem = card.find("a", {"data-test": "job-link"})
            if not title_elem:
                title_elem = card.find("a", class_=re.compile(r"job-title"))
            if title_elem:
                title = title_elem.get_text(strip=True)

            # Extract company
            company = ""
            company_elem = card.find("span", {"data-test": "employer-name"})
            if not company_elem:
                company_elem = card.find("div", class_=re.compile(r"employer"))
            if company_elem:
                company = company_elem.get_text(strip=True)

            # Extract location
            location = ""
            location_elem = card.find("span", {"data-test": "emp-location"})
            if not location_elem:
                location_elem = card.find("div", class_=re.compile(r"location"))
            if location_elem:
                location = location_elem.get_text(strip=True)

            # Extract salary (if available)
            salary = ""
            salary_elem = card.find("span", {"data-test": "detailSalary"})
            if not salary_elem:
                salary_elem = card.find("div", class_=re.compile(r"salary"))
            if salary_elem:
                salary = salary_elem.get_text(strip=True)

            # Extract job URL
            job_url = ""
            if title_elem and title_elem.get("href"):
                href = title_elem["href"]
                if href.startswith("/"):
                    job_url = f"{self.BASE_URL}{href}"
                else:
                    job_url = href

            # Extract rating
            rating = ""
            rating_elem = card.find("span", class_=re.compile(r"rating"))
            if rating_elem:
                rating = rating_elem.get_text(strip=True)

            if not title:
                return None

            return {
                "job_id": job_url,
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "rating": rating,
                "url": job_url,
                "source": "Glassdoor",
            }

        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None

    def get_company_rating(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get company rating and reviews.

        Args:
            company_name: Company name

        Returns:
            Company rating data
        """
        try:
            self.rate_limiter.wait_if_needed()

            # Build company search URL
            search_url = f"{self.BASE_URL}/Search/results.htm?keyword={company_name}"

            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Try to extract rating
            rating = None
            rating_elem = soup.find("span", class_=re.compile(r"rating"))
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                try:
                    rating = float(rating_text)
                except ValueError:
                    pass

            # Try to extract review count
            review_count = None
            review_elem = soup.find("div", {"data-test": "num-reviews"})
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                # Extract numbers from text
                numbers = re.findall(r"\d+", review_text.replace(",", ""))
                if numbers:
                    review_count = int(numbers[0])

            return {
                "company": company_name,
                "rating": rating,
                "review_count": review_count,
                "source": "Glassdoor",
            }

        except Exception as e:
            print(f"Error fetching company rating: {e}")
            return None


# Note: Glassdoor API Integration
# For production use, consider using Glassdoor's official API if you have access:
# https://www.glassdoor.com/developer/index.htm
#
# The API provides:
# - Job listings with detailed information
# - Company reviews and ratings
# - Salary data
# - Interview reviews
#
# This requires API credentials and has its own rate limits.
