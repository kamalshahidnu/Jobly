"""Coordinator for managing agent execution and workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from ..agents.base import BaseAgent


class AgentCoordinator:
    """Coordinates execution of multiple agents."""

    def __init__(self):
        """Initialize agent coordinator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the coordinator.

        Args:
            agent: Agent instance to register
        """
        self.agents[agent.name] = agent

    async def execute_workflow(self, workflow: List[str], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow of agents.

        Args:
            workflow: List of agent names to execute in order
            input_data: Initial input data

        Returns:
            Final workflow result
        """
        result: Dict[str, Any] = input_data or {}
        for agent_name in workflow:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                started_at = datetime.utcnow().isoformat(timespec="seconds")
                try:
                    result = await agent.execute(result)
                    status = "success"
                except Exception as exc:
                    result = {"status": "error", "error": str(exc), "agent": agent_name}
                    status = "error"

                self.execution_history.append(
                    {
                        "agent": agent_name,
                        "status": status,
                        "started_at": started_at,
                        "finished_at": datetime.utcnow().isoformat(timespec="seconds"),
                        "result": result,
                    }
                )
            else:
                self.execution_history.append(
                    {
                        "agent": agent_name,
                        "status": "skipped",
                        "started_at": datetime.utcnow().isoformat(timespec="seconds"),
                        "finished_at": datetime.utcnow().isoformat(timespec="seconds"),
                        "result": {"status": "skipped", "reason": "agent not registered"},
                    }
                )
        return result or {}

    def get_agent(self, name: str) -> BaseAgent:
        """Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance
        """
        return self.agents.get(name)
