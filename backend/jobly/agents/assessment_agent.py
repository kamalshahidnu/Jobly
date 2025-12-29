"""Assessment agent for handling coding challenges and assessments."""

from typing import Any, Dict
from .base import BaseAgent


class AssessmentAgent(BaseAgent):
    """Agent responsible for managing assessments and coding challenges."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="AssessmentAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and prepare for assessments.

        Args:
            input_data: Assessment details and requirements

        Returns:
            Assessment strategy and preparation materials
        """
        assessments = input_data.get("assessments")
        assessments = assessments if isinstance(assessments, list) else [input_data]

        def _as_list(value: Any) -> list:
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]

        strategies = []

        for item in assessments:
            assessment = item if isinstance(item, dict) else {}
            a_type = (assessment.get("type") or "coding_challenge").lower()
            difficulty = (assessment.get("difficulty") or "medium").lower()
            duration = int(assessment.get("duration_minutes") or assessment.get("duration") or 90)

            languages = [lang.strip() for lang in _as_list(assessment.get("languages")) if str(lang).strip()]
            topics = [topic.strip() for topic in _as_list(assessment.get("topics")) if str(topic).strip()]
            tools = [tool.strip() for tool in _as_list(assessment.get("tools")) if str(tool).strip()]

            planning_time = max(5, int(duration * 0.15))
            testing_time = max(10, int(duration * 0.15))
            implementation_time = max(15, duration - planning_time - testing_time)
            buffer_time = max(0, duration - (planning_time + testing_time + implementation_time))

            steps = [
                "Clarify requirements and constraints",
                "Outline solution approach and edge cases",
                "Set up environment and scaffolding",
                "Implement solution incrementally with tests",
                "Run validations and polish deliverables"
            ]

            if a_type in {"live_coding", "pairing"}:
                steps.insert(0, "Confirm coding environment and communication expectations")
            elif a_type in {"take_home", "project"}:
                steps.insert(3, "Create checkpoints to demonstrate progress")

            focus_areas = topics or languages or ["problem_solving"]

            strategy = {
                "type": a_type,
                "difficulty": difficulty,
                "duration_minutes": duration,
                "languages": languages,
                "topics": topics,
                "tools": tools,
                "time_allocation": {
                    "planning": planning_time,
                    "implementation": implementation_time,
                    "testing": testing_time,
                    "buffer": buffer_time
                },
                "steps": steps,
                "focus_areas": focus_areas,
                "risk_mitigations": [
                    "Write tests for critical paths",
                    "Keep solution simple and readable",
                    "Document assumptions inline"
                ]
            }

            strategies.append(strategy)

        self.state["last_strategy"] = strategies
        return {"status": "success", "strategy": {"assessments": strategies}}
