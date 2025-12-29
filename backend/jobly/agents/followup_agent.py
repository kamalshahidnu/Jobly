"""Follow-up agent for managing follow-up communications."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from .base import BaseAgent


class FollowupAgent(BaseAgent):
    """Agent responsible for managing follow-up communications."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="FollowupAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate follow-up messages and manage timing.

        Args:
            input_data: Previous communication and context

        Returns:
            Follow-up message and timing recommendation
        """
        now = datetime.utcnow()
        cadence = self.config.get("cadence_days", [3, 7, 14])

        def _parse_date(value: Any) -> Optional[datetime]:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    return None
            return None

        contact_name = input_data.get("contact_name") or "there"
        role = input_data.get("role") or "the position"
        company = input_data.get("company") or "your team"
        context = input_data.get("context") or ""

        followup_count = int(input_data.get("followup_count", 0) or 0)
        response_received = bool(input_data.get("response_received", False))
        last_contact_at = _parse_date(
            input_data.get("last_contact_at") or input_data.get("last_message_at")
        )
        days_since_last = (
            (now - last_contact_at).total_seconds() / 86400 if last_contact_at else None
        )

        if response_received:
            message_body = (
                f"Hi {contact_name},\n\n"
                "Thank you for the update. Please let me know if there is anything else "
                "you need from me."
            )
            next_followup_days = None
        else:
            target_gap = cadence[min(followup_count, len(cadence) - 1)] if cadence else 7
            wait_remaining = (
                max(target_gap - days_since_last, 0) if days_since_last is not None else 0
            )
            next_followup_days = round(wait_remaining, 2)
            message_body = (
                f"Hi {contact_name},\n\n"
                f"I hope you are well. I am following up on my application for {role} "
                f"at {company}. "
                "I remain very interested and would appreciate any updates. "
                "Please let me know if I can provide additional information."
            )
            if context:
                message_body += f"\n\nNotes: {context}"

        followup = {
            "message": message_body,
            "next_followup_days": next_followup_days,
            "scheduled_for": (
                (now + timedelta(days=next_followup_days)).isoformat()
                if next_followup_days is not None
                else None
            ),
            "followup_number": followup_count + (0 if response_received else 1),
            "days_since_last_contact": days_since_last,
            "response_received": response_received,
        }

        return {"status": "success", "followup": followup}
