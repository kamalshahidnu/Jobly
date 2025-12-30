"""Tests for DedupAgent."""

import pytest
from jobly.agents.dedup_agent import DedupAgent


@pytest.mark.asyncio
async def test_dedup_by_url():
    """Test deduplication by URL."""
    agent = DedupAgent()

    jobs = [
        {
            "title": "Software Engineer",
            "company": "TechCorp",
            "url": "https://example.com/job/123"
        },
        {
            "title": "Software Engineer",
            "company": "TechCorp",
            "url": "https://example.com/job/123"  # Duplicate URL
        },
        {
            "title": "Data Scientist",
            "company": "DataCo",
            "url": "https://example.com/job/456"
        }
    ]

    result = await agent.execute({"jobs": jobs})

    assert result["status"] == "success"
    assert len(result["deduplicated_jobs"]) == 2


@pytest.mark.asyncio
async def test_dedup_by_composite_key():
    """Test deduplication by company + title."""
    agent = DedupAgent()

    jobs = [
        {
            "title": "Backend Engineer",
            "company": "StartupX",
            "location": "Remote"
        },
        {
            "title": "Backend Engineer",
            "company": "StartupX",
            "location": "San Francisco"  # Same title + company, different location
        },
        {
            "title": "Frontend Engineer",
            "company": "StartupX",
            "location": "Remote"  # Different title
        }
    ]

    result = await agent.execute({"jobs": jobs})

    assert result["status"] == "success"
    # Should keep only unique company + title combinations
    assert len(result["deduplicated_jobs"]) == 2


@pytest.mark.asyncio
async def test_dedup_empty_list():
    """Test deduplication with empty job list."""
    agent = DedupAgent()

    result = await agent.execute({"jobs": []})

    assert result["status"] == "success"
    assert result["deduplicated_jobs"] == []


@pytest.mark.asyncio
async def test_dedup_preserves_order():
    """Test that deduplication preserves order of first occurrence."""
    agent = DedupAgent()

    jobs = [
        {"title": "Job A", "company": "Company 1", "score": 90},
        {"title": "Job B", "company": "Company 2", "score": 85},
        {"title": "Job A", "company": "Company 1", "score": 95},  # Duplicate with higher score
    ]

    result = await agent.execute({"jobs": jobs})

    deduped = result["deduplicated_jobs"]
    assert len(deduped) == 2
    # Should keep first occurrence
    assert deduped[0]["score"] == 90
