"""Tracker agent for tracking application status and progress."""

from datetime import datetime
from typing import Any, Dict, List
from ..utils.validators import validate_job_status
from .base import BaseAgent


class TrackerAgent(BaseAgent):
    """Agent responsible for tracking application status."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="TrackerAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update and track application status.

        Args:
            input_data: Application updates

        Returns:
            Updated tracking information
        """
        updates: List[Dict[str, Any]]
        if isinstance(input_data.get("updates"), list):
            updates = input_data["updates"]
        else:
            updates = [input_data]

        tracking = self.state.setdefault("tracking_data", {})
        processed: List[Dict[str, Any]] = []
        now = datetime.utcnow().isoformat()

        for update in updates:
            app_id = str(update.get("application_id") or update.get("id") or "").strip()
            status_raw = update.get("status") or update.get("state")
            note = update.get("note") or update.get("notes")
            metadata = update.get("metadata") or {}

            if not app_id:
                processed.append({"status": "failed", "error": "missing_application_id"})
                continue

            status = status_raw.lower() if status_raw else None
            if status and not validate_job_status(status):
                processed.append(
                    {
                        "application_id": app_id,
                        "status": "failed",
                        "error": "invalid_status"
                    }
                )
                continue

            entry = tracking.get(app_id, {"history": []})

            if status:
                entry["current_status"] = status
                entry.setdefault("history", []).append(
                    {"status": status, "timestamp": now, "note": note}
                )

            if metadata:
                entry["metadata"] = {**entry.get("metadata", {}), **metadata}

            entry["updated_at"] = now
            tracking[app_id] = entry
            processed.append({"application_id": app_id, "tracking": entry})

        self.state["tracking_data"] = tracking
        return {"status": "success", "tracking_data": tracking, "processed": processed}
