"""Tests for CoverLetterAgent."""

import pytest
from jobly.agents.cover_letter_agent import CoverLetterAgent


@pytest.mark.asyncio
async def test_cover_letter_generation_template():
    """Test cover letter generation with template fallback."""
    agent = CoverLetterAgent()

    profile = {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_years": 5
    }

    job = {
        "title": "Senior Backend Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "description": "Looking for experienced backend engineer",
        "requirements": ["Python", "FastAPI", "SQL"]
    }

    result = await agent.execute({
        "profile": profile,
        "job": job
    })

    assert result["status"] == "success"
    assert "cover_letter" in result
    assert "TechCorp" in result["cover_letter"]
    assert "Senior Backend Engineer" in result["cover_letter"]
    assert "John Doe" in result["cover_letter"]


@pytest.mark.asyncio
async def test_cover_letter_with_company_info():
    """Test cover letter generation with company research."""
    agent = CoverLetterAgent()

    profile = {
        "name": "Jane Smith",
        "skills": ["React", "TypeScript", "Node.js"],
        "experience_years": 3
    }

    job = {
        "title": "Frontend Developer",
        "company": "StartupX"
    }

    company_info = "is a fast-growing startup in the fintech space"

    result = await agent.execute({
        "profile": profile,
        "job": job,
        "company_info": company_info
    })

    assert result["status"] == "success"
    assert "cover_letter" in result
    assert "StartupX" in result["cover_letter"]
    assert "fintech" in result["cover_letter"].lower()


@pytest.mark.asyncio
async def test_cover_letter_minimal_data():
    """Test cover letter generation with minimal data."""
    agent = CoverLetterAgent()

    result = await agent.execute({
        "profile": {"name": "Test User"},
        "job": {"title": "Developer", "company": "Company"}
    })

    assert result["status"] == "success"
    assert "cover_letter" in result
    # Should still generate something reasonable
    assert len(result["cover_letter"]) > 50
