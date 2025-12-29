"""Tests for job ranker agent."""

import pytest
from jobly.agents.job_ranker_agent import JobRankerAgent


class TestJobRankerAgent:
    """Test cases for JobRankerAgent."""

    @pytest.fixture
    def agent(self):
        """Create JobRankerAgent instance.

        Returns:
            JobRankerAgent instance
        """
        return JobRankerAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "JobRankerAgent"

    @pytest.mark.asyncio
    async def test_execute_returns_ranked_jobs(self, agent, sample_profile, sample_job):
        """Test execute returns ranked jobs."""
        input_data = {
            "profile": sample_profile,
            "jobs": [sample_job]
        }
        result = await agent.execute(input_data)
        assert result["status"] == "success"
        assert "ranked_jobs" in result
