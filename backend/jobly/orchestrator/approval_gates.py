"""Approval gates for human-in-the-loop workflow control."""

from typing import Dict, Any, Callable, Optional
from enum import Enum


class ApprovalStatus(str, Enum):
    """Approval status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class ApprovalGate:
    """Gate for requiring human approval before proceeding."""

    def __init__(self, gate_name: str, description: str):
        """Initialize approval gate.

        Args:
            gate_name: Name of the gate
            description: Description of what requires approval
        """
        self.gate_name = gate_name
        self.description = description
        self.status = ApprovalStatus.PENDING
        self.data: Optional[Dict[str, Any]] = None
        self.feedback: Optional[str] = None

    def submit_for_approval(self, data: Dict[str, Any]) -> None:
        """Submit data for approval.

        Args:
            data: Data to be approved
        """
        self.data = data
        self.status = ApprovalStatus.PENDING

    def approve(self, feedback: Optional[str] = None) -> None:
        """Approve the submitted data.

        Args:
            feedback: Optional feedback
        """
        self.status = ApprovalStatus.APPROVED
        self.feedback = feedback

    def reject(self, feedback: str) -> None:
        """Reject the submitted data.

        Args:
            feedback: Rejection reason
        """
        self.status = ApprovalStatus.REJECTED
        self.feedback = feedback

    def modify(self, modified_data: Dict[str, Any], feedback: Optional[str] = None) -> None:
        """Modify and approve the data.

        Args:
            modified_data: Modified data
            feedback: Optional feedback
        """
        self.data = modified_data
        self.status = ApprovalStatus.MODIFIED
        self.feedback = feedback


class ApprovalGateManager:
    """Manager for multiple approval gates."""

    def __init__(self):
        """Initialize approval gate manager."""
        self.gates: Dict[str, ApprovalGate] = {}

    def create_gate(self, gate_name: str, description: str) -> ApprovalGate:
        """Create a new approval gate.

        Args:
            gate_name: Name of the gate
            description: Gate description

        Returns:
            Created approval gate
        """
        gate = ApprovalGate(gate_name, description)
        self.gates[gate_name] = gate
        return gate

    def get_gate(self, gate_name: str) -> Optional[ApprovalGate]:
        """Get approval gate by name.

        Args:
            gate_name: Name of the gate

        Returns:
            Approval gate or None
        """
        return self.gates.get(gate_name)

    def get_pending_gates(self) -> Dict[str, ApprovalGate]:
        """Get all pending approval gates.

        Returns:
            Dictionary of pending gates
        """
        return {name: gate for name, gate in self.gates.items()
                if gate.status == ApprovalStatus.PENDING}
