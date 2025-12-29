"""Email monitor agent for tracking job-related emails."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


class EmailMonitorAgent(BaseAgent):
    """Agent responsible for monitoring and categorizing emails."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="EmailMonitorAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and categorize incoming emails.

        Args:
            input_data: Email credentials and filters

        Returns:
            Categorized emails and action items
        """
        emails: List[Dict[str, Any]] = input_data.get("emails", []) or []
        filters: Dict[str, Any] = input_data.get("filters", {}) or {}

        category_keywords: Dict[str, List[str]] = {
            "interview": ["interview", "phone screen", "onsite", "conversation", "schedule"],
            "offer": ["offer", "compensation", "package", "salary"],
            "rejection": ["unfortunately", "not moving forward", "regret", "reject"],
            "application_received": ["application received", "applied", "received your application"],
            "follow_up": ["follow up", "checking in", "status update", "touch base"],
        }

        action_map: Dict[str, str] = {
            "interview": "Schedule and confirm interview.",
            "offer": "Review offer details and compare against expectations.",
            "rejection": "Log status and send a courteous reply if appropriate.",
            "application_received": "Track application and set reminder for follow-up.",
            "follow_up": "Send follow-up response with latest updates.",
            "other": "Review manually.",
        }

        allowed_senders = {str(s).lower() for s in filters.get("senders", []) if s}
        subject_keywords = [str(k).lower() for k in filters.get("subject_keywords", []) if k]
        since_value = filters.get("since")
        since_dt = self._parse_date(since_value)

        categorized: List[Dict[str, Any]] = []
        summary: Dict[str, int] = {}

        for email in emails:
            sender = str(email.get("from", "")).lower()
            if allowed_senders and sender not in allowed_senders:
                continue

            subject = str(email.get("subject", "") or "")
            body = str(email.get("body", "") or "")

            if subject_keywords:
                subject_lower = subject.lower()
                if not any(keyword in subject_lower for keyword in subject_keywords):
                    continue

            received_at = self._parse_date(email.get("received_at")) or self._parse_date(email.get("date"))
            if since_dt and received_at and received_at < since_dt:
                continue

            text = f"{subject} {body}".lower()
            category = "other"
            for cat, keywords in category_keywords.items():
                if any(keyword in text for keyword in keywords):
                    category = cat
                    break

            summary[category] = summary.get(category, 0) + 1
            categorized.append({
                "id": email.get("id") or email.get("message_id"),
                "from": email.get("from"),
                "subject": subject,
                "received_at": received_at.isoformat() if received_at else None,
                "category": category,
                "action": action_map.get(category, action_map["other"])
            })

        return {"status": "success", "emails": categorized, "summary": summary}

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        """Parse value into datetime if possible."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return None
