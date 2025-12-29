"""Tests for profile agent."""

import pytest
from jobly.agents.profile_agent import ProfileAgent


class TestProfileAgent:
    """Test cases for ProfileAgent."""

    @pytest.fixture
    def agent(self):
        """Create ProfileAgent instance.

        Returns:
            ProfileAgent instance
        """
        return ProfileAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "ProfileAgent"
        assert agent.config == {}
        assert agent.state == {}

    @pytest.mark.asyncio
    async def test_execute_returns_success(self, agent, sample_profile):
        """Test execute method returns success."""
        result = await agent.execute(sample_profile)
        assert result["status"] == "success"
        assert "profile" in result

    @pytest.mark.asyncio
    async def test_reset_clears_state(self, agent):
        """Test reset clears agent state."""
        agent.state = {"test": "data"}
        agent.reset()
        assert agent.state == {}
