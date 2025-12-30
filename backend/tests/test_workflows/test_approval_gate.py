"""Tests for ApprovalGate system."""

import pytest
from datetime import datetime
from jobly.workflows.approval_gate import ApprovalGate, ApprovalAction, ApprovalStatus


def test_create_approval_request():
    """Test creating an approval request."""
    gate = ApprovalGate()

    request = gate.create_approval_request(
        user_id="user123",
        action=ApprovalAction.SEND_EMAIL,
        title="Send Email",
        description="Send follow-up email to recruiter",
        data={"to": "recruiter@example.com", "subject": "Follow-up"}
    )

    assert request.request_id is not None
    assert request.user_id == "user123"
    assert request.action == ApprovalAction.SEND_EMAIL
    assert request.status == ApprovalStatus.PENDING
    assert isinstance(request.created_at, datetime)


def test_approve_request():
    """Test approving a request."""
    gate = ApprovalGate()

    request = gate.create_approval_request(
        user_id="user123",
        action=ApprovalAction.APPLY_TO_JOB,
        title="Apply to Job",
        description="Apply to Software Engineer position",
        data={"job_id": "job456"}
    )

    success = gate.approve_request(
        request_id=request.request_id,
        reviewed_by="user123",
        notes="Looks good!"
    )

    assert success is True

    # Check request status
    approved_request = gate.get_request(request.request_id)
    assert approved_request.status == ApprovalStatus.APPROVED
    assert approved_request.reviewed_by == "user123"
    assert approved_request.reviewer_notes == "Looks good!"


def test_reject_request():
    """Test rejecting a request."""
    gate = ApprovalGate()

    request = gate.create_approval_request(
        user_id="user123",
        action=ApprovalAction.SEND_OUTREACH,
        title="Send Outreach",
        description="Send networking message",
        data={"contact_id": "contact789"}
    )

    success = gate.reject_request(
        request_id=request.request_id,
        reviewed_by="user123",
        notes="Need to revise message"
    )

    assert success is True

    # Check request status
    rejected_request = gate.get_request(request.request_id)
    assert rejected_request.status == ApprovalStatus.REJECTED


def test_get_pending_requests():
    """Test getting pending requests."""
    gate = ApprovalGate()

    # Create multiple requests
    gate.create_approval_request(
        user_id="user1",
        action=ApprovalAction.SEND_EMAIL,
        title="Email 1",
        description="Test",
        data={}
    )

    gate.create_approval_request(
        user_id="user2",
        action=ApprovalAction.SEND_EMAIL,
        title="Email 2",
        description="Test",
        data={}
    )

    gate.create_approval_request(
        user_id="user1",
        action=ApprovalAction.APPLY_TO_JOB,
        title="Application",
        description="Test",
        data={}
    )

    # Get pending requests for user1
    pending = gate.get_pending_requests(user_id="user1")
    assert len(pending) == 2


def test_callback_execution():
    """Test that callback is executed on approval."""
    gate = ApprovalGate()
    callback_executed = {"value": False}

    def callback(request):
        callback_executed["value"] = True

    request = gate.create_approval_request(
        user_id="user123",
        action=ApprovalAction.CUSTOM,
        title="Custom Action",
        description="Test callback",
        data={},
        callback=callback
    )

    gate.approve_request(
        request_id=request.request_id,
        reviewed_by="user123"
    )

    assert callback_executed["value"] is True


def test_cancel_request():
    """Test canceling a pending request."""
    gate = ApprovalGate()

    request = gate.create_approval_request(
        user_id="user123",
        action=ApprovalAction.SEND_EMAIL,
        title="Email",
        description="Test",
        data={}
    )

    success = gate.cancel_request(request.request_id)
    assert success is True

    # Request should no longer exist
    assert gate.get_request(request.request_id) is None


def test_get_user_requests():
    """Test getting all requests for a user."""
    gate = ApprovalGate()

    # Create and approve one
    req1 = gate.create_approval_request(
        user_id="user1",
        action=ApprovalAction.SEND_EMAIL,
        title="Email 1",
        description="Test",
        data={}
    )
    gate.approve_request(req1.request_id, "user1")

    # Create and reject one
    req2 = gate.create_approval_request(
        user_id="user1",
        action=ApprovalAction.SEND_EMAIL,
        title="Email 2",
        description="Test",
        data={}
    )
    gate.reject_request(req2.request_id, "user1")

    # Create one pending
    gate.create_approval_request(
        user_id="user1",
        action=ApprovalAction.SEND_EMAIL,
        title="Email 3",
        description="Test",
        data={}
    )

    user_requests = gate.get_user_requests("user1")

    assert len(user_requests["approved"]) == 1
    assert len(user_requests["rejected"]) == 1
    assert len(user_requests["pending"]) == 1
