"""Base agent class for all Jobly agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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
