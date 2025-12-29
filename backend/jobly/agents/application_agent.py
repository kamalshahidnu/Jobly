"""Application agent for automating job applications."""

from datetime import datetime
from typing import Any, Dict, List
from ..utils.helpers import generate_id
from ..utils.validators import validate_job_status
from .base import BaseAgent


class ApplicationAgent(BaseAgent):
    """Agent responsible for submitting job applications."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="ApplicationAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit job application.

        Args:
            input_data: Job details and application materials

        Returns:
            Application submission status
        """
        # Normalize to a list so we can handle batch submissions quickly
        payloads: List[Dict[str, Any]]
        if isinstance(input_data.get("applications"), list):
            payloads = input_data["applications"]
        else:
            payloads = [input_data]

        applications = self.state.setdefault("applications", {})
        submitted: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        now = datetime.utcnow().isoformat()

        for payload in payloads:
            job_id = str(payload.get("job_id") or payload.get("id") or "").strip()
            user_id = str(payload.get("user_id") or "").strip()

            if not job_id or not user_id:
                errors.append(
                    {
                        "error": "missing_required_fields",
                        "job_id": job_id,
                        "user_id": user_id,
                    }
                )
                continue

            status_raw = payload.get("status") or "applied"
            status = status_raw.lower()
            if not validate_job_status(status):
                status = "applied"

            application_id = str(payload.get("application_id") or generate_id("app_"))
            record = {
                "application_id": application_id,
                "user_id": user_id,
                "job_id": job_id,
                "status": status,
                "applied_at": payload.get("applied_at") or now,
                "resume_version": payload.get("resume_version"),
                "cover_letter": payload.get("cover_letter"),
                "notes": payload.get("notes"),
                "metadata": payload.get("metadata") or {},
                "job_url": payload.get("job_url") or payload.get("url"),
            }

            applications[application_id] = record
            submitted.append(record)

        self.state["applications"] = applications

        submission_status = "success"
        if errors and submitted:
            submission_status = "partial_success"
        elif errors and not submitted:
            submission_status = "failed"

        return {
            "status": submission_status,
            "submitted": submitted,
            "errors": errors,
            "application_ids": [app["application_id"] for app in submitted],
        }
