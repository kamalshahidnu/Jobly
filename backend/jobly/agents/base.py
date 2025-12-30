"""Base agent class for all Jobly agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..utils.llm import get_llm_client, LLMClient


class BaseAgent(ABC):
    """Abstract base class for all agents in the Jobly system."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the base agent.

        Args:
            name: The name of the agent
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.state: Dict[str, Any] = {}

        # Initialize LLM client if available
        self.llm: Optional[LLMClient] = None
        try:
            self.llm = get_llm_client(
                provider=config.get("llm_provider") if config else None,
                model=config.get("llm_model") if config else None,
            )
        except Exception:
            # LLM not available, agents can fall back to deterministic logic
            pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task.

        Args:
            input_data: Input data for the agent

        Returns:
            Result dictionary from agent execution
        """
        pass

    def reset(self) -> None:
        """Reset the agent's state."""
        self.state = {}
