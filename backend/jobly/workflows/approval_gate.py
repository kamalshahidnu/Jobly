"""Approval gate system for human-in-the-loop workflows."""

import uuid
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel


class ApprovalStatus(str, Enum):
    """Status of an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalAction(str, Enum):
    """Type of action requiring approval."""

    SEND_EMAIL = "send_email"
    APPLY_TO_JOB = "apply_to_job"
    SEND_OUTREACH = "send_outreach"
    GENERATE_DOCUMENT = "generate_document"
    SCHEDULE_INTERVIEW = "schedule_interview"
    ACCEPT_OFFER = "accept_offer"
    CUSTOM = "custom"


class ApprovalRequest(BaseModel):
    """Model for an approval request."""

    request_id: str
    user_id: str
    action: ApprovalAction
    title: str
    description: str
    data: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewer_notes: Optional[str] = None


class ApprovalGate:
    """Approval gate for human-in-the-loop workflows.

    This class manages approval requests for actions that require human review
    before execution.
    """

    def __init__(self):
        """Initialize approval gate."""
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approved_requests: Dict[str, ApprovalRequest] = {}
        self.rejected_requests: Dict[str, ApprovalRequest] = {}
        self.callbacks: Dict[str, Callable] = {}

    def create_approval_request(
        self,
        user_id: str,
        action: ApprovalAction,
        title: str,
        description: str,
        data: Dict[str, Any],
        callback: Optional[Callable] = None,
    ) -> ApprovalRequest:
        """Create a new approval request.

        Args:
            user_id: User ID requesting approval
            action: Type of action requiring approval
            title: Short title for the request
            description: Detailed description
            data: Data associated with the action
            callback: Optional callback to execute on approval

        Returns:
            Created approval request
        """
        request_id = str(uuid.uuid4())

        request = ApprovalRequest(
            request_id=request_id,
            user_id=user_id,
            action=action,
            title=title,
            description=description,
            data=data,
            status=ApprovalStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        self.pending_requests[request_id] = request

        if callback:
            self.callbacks[request_id] = callback

        return request

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get an approval request by ID.

        Args:
            request_id: Request ID

        Returns:
            Approval request if found
        """
        # Check all dictionaries
        for requests_dict in [
            self.pending_requests,
            self.approved_requests,
            self.rejected_requests,
        ]:
            if request_id in requests_dict:
                return requests_dict[request_id]

        return None

    def get_pending_requests(self, user_id: Optional[str] = None) -> List[ApprovalRequest]:
        """Get all pending approval requests.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of pending requests
        """
        if user_id:
            return [
                req
                for req in self.pending_requests.values()
                if req.user_id == user_id
            ]
        return list(self.pending_requests.values())

    def approve_request(
        self,
        request_id: str,
        reviewed_by: str,
        notes: Optional[str] = None,
        execute_callback: bool = True,
    ) -> bool:
        """Approve an approval request.

        Args:
            request_id: Request ID
            reviewed_by: ID of user approving
            notes: Optional reviewer notes
            execute_callback: Whether to execute the callback

        Returns:
            Success status
        """
        request = self.pending_requests.get(request_id)

        if not request:
            return False

        # Update request
        request.status = ApprovalStatus.APPROVED
        request.reviewed_at = datetime.utcnow()
        request.reviewed_by = reviewed_by
        request.reviewer_notes = notes

        # Move to approved
        del self.pending_requests[request_id]
        self.approved_requests[request_id] = request

        # Execute callback if provided
        if execute_callback and request_id in self.callbacks:
            try:
                self.callbacks[request_id](request)
            except Exception as e:
                print(f"Error executing callback for {request_id}: {e}")

        return True

    def reject_request(
        self,
        request_id: str,
        reviewed_by: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Reject an approval request.

        Args:
            request_id: Request ID
            reviewed_by: ID of user rejecting
            notes: Optional reviewer notes

        Returns:
            Success status
        """
        request = self.pending_requests.get(request_id)

        if not request:
            return False

        # Update request
        request.status = ApprovalStatus.REJECTED
        request.reviewed_at = datetime.utcnow()
        request.reviewed_by = reviewed_by
        request.reviewer_notes = notes

        # Move to rejected
        del self.pending_requests[request_id]
        self.rejected_requests[request_id] = request

        # Remove callback if exists
        if request_id in self.callbacks:
            del self.callbacks[request_id]

        return True

    def cancel_request(self, request_id: str) -> bool:
        """Cancel a pending approval request.

        Args:
            request_id: Request ID

        Returns:
            Success status
        """
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]

            # Remove callback if exists
            if request_id in self.callbacks:
                del self.callbacks[request_id]

            return True

        return False

    def get_user_requests(self, user_id: str) -> Dict[str, List[ApprovalRequest]]:
        """Get all requests for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary of requests by status
        """
        return {
            "pending": [
                req for req in self.pending_requests.values() if req.user_id == user_id
            ],
            "approved": [
                req for req in self.approved_requests.values() if req.user_id == user_id
            ],
            "rejected": [
                req for req in self.rejected_requests.values() if req.user_id == user_id
            ],
        }

    def clear_old_requests(self, days: int = 30) -> int:
        """Clear old approved/rejected requests.

        Args:
            days: Number of days to keep

        Returns:
            Number of requests cleared
        """
        cutoff = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
        cleared = 0

        # Clear old approved requests
        to_remove = [
            req_id
            for req_id, req in self.approved_requests.items()
            if req.reviewed_at and req.reviewed_at.timestamp() < cutoff
        ]
        for req_id in to_remove:
            del self.approved_requests[req_id]
            cleared += 1

        # Clear old rejected requests
        to_remove = [
            req_id
            for req_id, req in self.rejected_requests.items()
            if req.reviewed_at and req.reviewed_at.timestamp() < cutoff
        ]
        for req_id in to_remove:
            del self.rejected_requests[req_id]
            cleared += 1

        return cleared


# Global approval gate instance
_approval_gate = ApprovalGate()


def get_approval_gate() -> ApprovalGate:
    """Get the global approval gate instance.

    Returns:
        Global approval gate
    """
    return _approval_gate
