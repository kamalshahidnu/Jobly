"""Web scraper for job boards and company websites."""

from __future__ import annotations

from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup


class WebScraper:
    """Generic web scraper for job postings."""

    def __init__(self, user_agent: str = None):
        """Initialize web scraper.

        Args:
            user_agent: Custom user agent string
        """
        self.user_agent = user_agent or "Jobly/1.0"
        self.session = requests.Session()

    def scrape_url(self, url: str) -> str:
        """Scrape content from URL.

        Args:
            url: Target URL

        Returns:
            Page content
        """
        if not url:
            return ""
        try:
            resp = self.session.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=20,
            )
            resp.raise_for_status()
            return resp.text
        except Exception:
            return ""

    def extract_job_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract job data from HTML.

        Args:
            html: HTML content
            selectors: CSS selectors for data extraction

        Returns:
            Extracted job data
        """
        if not html:
            return {}
        soup = BeautifulSoup(html, "html.parser")
        data: Dict[str, Any] = {}

        for key, selector in (selectors or {}).items():
            if not selector:
                continue
            # Support simple "css|attr:href" selector syntax.
            attr = None
            css = selector
            if "|" in selector:
                css, right = selector.split("|", 1)
                right = right.strip()
                if right.startswith("attr:"):
                    attr = right.replace("attr:", "", 1).strip()

            el = soup.select_one(css.strip())
            if not el:
                data[key] = None
                continue
            if attr:
                data[key] = el.get(attr)
            else:
                data[key] = el.get_text(strip=True)
        return data

    def scrape_job_board(self, board_name: str, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape specific job board.

        Args:
            board_name: Name of job board
            search_params: Search parameters

        Returns:
            List of job postings
        """
        board = (board_name or "").strip().lower()
        params = search_params or {}

        # Minimal generic implementation: caller supplies a list of URLs and selectors.
        urls = params.get("urls") or []
        selectors = params.get("selectors") or {}
        postings: List[Dict[str, Any]] = []

        if board in ("generic", "custom", ""):
            for url in urls:
                html = self.scrape_url(url)
                if not html:
                    continue
                item = {"url": url}
                item.update(self.extract_job_data(html, selectors))
                postings.append(item)
            return postings

        # Phase 1: board-specific scrapers can be added here.
        return []
