"""Coordinator for managing agent execution and workflow."""

from typing import Dict, Any, List
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
        # TODO: Implement workflow execution
        result = input_data
        for agent_name in workflow:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = await agent.execute(result)
                self.execution_history.append({
                    "agent": agent_name,
                    "result": result
                })
        return result

    def get_agent(self, name: str) -> BaseAgent:
        """Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance
        """
        return self.agents.get(name)
