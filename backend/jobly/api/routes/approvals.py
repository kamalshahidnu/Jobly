"""Approval gates API routes."""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List
from ...workflows.approval_gate import get_approval_gate, ApprovalRequest, ApprovalStatus
from ...auth.jwt_handler import get_current_user

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending", response_model=List[Dict[str, Any]])
async def get_pending_approvals(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all pending approval requests for current user.

    Args:
        current_user: Current authenticated user

    Returns:
        List of pending approval requests
    """
    gate = get_approval_gate()
    requests = gate.get_pending_requests(user_id=current_user["sub"])

    return [req.dict() for req in requests]


@router.get("/{request_id}", response_model=Dict[str, Any])
async def get_approval_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific approval request.

    Args:
        request_id: Request ID
        current_user: Current authenticated user

    Returns:
        Approval request details

    Raises:
        HTTPException: If request not found or unauthorized
    """
    gate = get_approval_gate()
    request = gate.get_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )

    # Verify user owns the request
    if request.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this request"
        )

    return request.dict()


@router.post("/{request_id}/approve")
async def approve_request(
    request_id: str,
    notes: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Approve an approval request.

    Args:
        request_id: Request ID
        notes: Optional reviewer notes
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If request not found or unauthorized
    """
    gate = get_approval_gate()
    request = gate.get_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )

    # Verify user owns the request
    if request.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to approve this request"
        )

    success = gate.approve_request(
        request_id=request_id,
        reviewed_by=current_user["sub"],
        notes=notes
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to approve request"
        )

    return {"message": "Request approved successfully"}


@router.post("/{request_id}/reject")
async def reject_request(
    request_id: str,
    notes: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Reject an approval request.

    Args:
        request_id: Request ID
        notes: Optional reviewer notes
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If request not found or unauthorized
    """
    gate = get_approval_gate()
    request = gate.get_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )

    # Verify user owns the request
    if request.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject this request"
        )

    success = gate.reject_request(
        request_id=request_id,
        reviewed_by=current_user["sub"],
        notes=notes
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reject request"
        )

    return {"message": "Request rejected successfully"}


@router.delete("/{request_id}")
async def cancel_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Cancel a pending approval request.

    Args:
        request_id: Request ID
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If request not found or unauthorized
    """
    gate = get_approval_gate()
    request = gate.get_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )

    # Verify user owns the request
    if request.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this request"
        )

    success = gate.cancel_request(request_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel request"
        )

    return {"message": "Request cancelled successfully"}


@router.get("/user/all", response_model=Dict[str, List[Dict[str, Any]]])
async def get_all_user_requests(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all approval requests for current user.

    Args:
        current_user: Current authenticated user

    Returns:
        Dictionary of requests by status
    """
    gate = get_approval_gate()
    requests = gate.get_user_requests(current_user["sub"])

    return {
        "pending": [req.dict() for req in requests["pending"]],
        "approved": [req.dict() for req in requests["approved"]],
        "rejected": [req.dict() for req in requests["rejected"]],
    }
