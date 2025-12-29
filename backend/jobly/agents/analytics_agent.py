"""Analytics agent for generating insights and statistics."""

from datetime import datetime
from typing import Any, Dict
from .base import BaseAgent


class AnalyticsAgent(BaseAgent):
    """Agent responsible for generating analytics and insights."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="AnalyticsAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics and insights.

        Args:
            input_data: Data to analyze

        Returns:
            Analytics results and insights
        """
        applications = input_data.get("applications", [])

        def _parse_date(value: Any) -> datetime | None:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    return None
            return None

        status_breakdown: Dict[str, int] = {}
        response_times = []
        responded_count = 0
        interview_count = 0
        offer_count = 0

        for app in applications:
            status = str(app.get("status", "unknown")).lower()
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

            applied_at = _parse_date(app.get("applied_at"))
            responded_at = _parse_date(app.get("responded_at"))
            if responded_at:
                responded_count += 1
                if applied_at:
                    delta = responded_at - applied_at
                    response_times.append(delta.days + delta.seconds / 86400)

            if "interview" in status:
                interview_count += 1
            if "offer" in status:
                offer_count += 1

        total = len(applications) or 1  # Avoid division by zero
        response_rate = responded_count / total
        avg_response = sum(response_times) / len(response_times) if response_times else 0.0

        analytics = {
            "total_applications": len(applications),
            "status_breakdown": status_breakdown,
            "response_rate": response_rate,
            "avg_response_days": avg_response,
            "fastest_response_days": min(response_times) if response_times else 0.0,
            "slowest_response_days": max(response_times) if response_times else 0.0,
            "interview_rate": interview_count / total,
            "offer_rate": offer_count / total
        }

        return {"status": "success", "analytics": analytics}
