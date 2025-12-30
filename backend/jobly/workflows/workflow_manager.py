"""Workflow manager for orchestrating approval-based workflows."""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from .approval_gate import ApprovalGate, ApprovalAction, ApprovalRequest, get_approval_gate


class WorkflowManager:
    """Manager for approval-based workflows.

    This class orchestrates workflows that require human approval before execution.
    """

    def __init__(self, approval_gate: Optional[ApprovalGate] = None):
        """Initialize workflow manager.

        Args:
            approval_gate: Optional approval gate instance (uses global if not provided)
        """
        self.approval_gate = approval_gate or get_approval_gate()
        self.workflow_configs: Dict[str, Dict[str, Any]] = {}

    def register_workflow(
        self,
        workflow_id: str,
        name: str,
        action: ApprovalAction,
        requires_approval: bool = True,
        auto_approve_conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a new workflow.

        Args:
            workflow_id: Unique workflow ID
            name: Human-readable workflow name
            action: Type of action
            requires_approval: Whether approval is required
            auto_approve_conditions: Conditions for automatic approval
        """
        self.workflow_configs[workflow_id] = {
            "name": name,
            "action": action,
            "requires_approval": requires_approval,
            "auto_approve_conditions": auto_approve_conditions or {},
        }

    def execute_workflow(
        self,
        workflow_id: str,
        user_id: str,
        data: Dict[str, Any],
        callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Execute a workflow with approval gating.

        Args:
            workflow_id: Workflow ID
            user_id: User ID
            data: Workflow data
            callback: Optional callback to execute on approval

        Returns:
            Workflow execution result
        """
        config = self.workflow_configs.get(workflow_id)

        if not config:
            return {
                "success": False,
                "error": f"Unknown workflow: {workflow_id}",
            }

        # Check if approval required
        if not config["requires_approval"]:
            # Execute immediately
            if callback:
                try:
                    callback(data)
                    return {"success": True, "executed": True}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            return {"success": True, "executed": True}

        # Check auto-approve conditions
        if self._check_auto_approve(config["auto_approve_conditions"], data):
            if callback:
                try:
                    callback(data)
                    return {"success": True, "executed": True, "auto_approved": True}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            return {"success": True, "executed": True, "auto_approved": True}

        # Create approval request
        request = self.approval_gate.create_approval_request(
            user_id=user_id,
            action=config["action"],
            title=config["name"],
            description=self._generate_description(workflow_id, data),
            data=data,
            callback=callback,
        )

        return {
            "success": True,
            "executed": False,
            "approval_required": True,
            "request_id": request.request_id,
        }

    def _check_auto_approve(
        self, conditions: Dict[str, Any], data: Dict[str, Any]
    ) -> bool:
        """Check if data meets auto-approve conditions.

        Args:
            conditions: Auto-approve conditions
            data: Workflow data

        Returns:
            True if conditions are met
        """
        if not conditions:
            return False

        # Simple condition checking (can be extended)
        for key, expected_value in conditions.items():
            if key not in data or data[key] != expected_value:
                return False

        return True

    def _generate_description(self, workflow_id: str, data: Dict[str, Any]) -> str:
        """Generate description for approval request.

        Args:
            workflow_id: Workflow ID
            data: Workflow data

        Returns:
            Generated description
        """
        # Generate a description based on workflow type
        if workflow_id == "send_email":
            return f"Send email to {data.get('to', 'recipient')}: {data.get('subject', 'No subject')}"
        elif workflow_id == "apply_to_job":
            return f"Apply to {data.get('job_title', 'job')} at {data.get('company', 'company')}"
        elif workflow_id == "send_outreach":
            return f"Send outreach message to {data.get('contact_name', 'contact')}"
        else:
            return f"Execute {workflow_id} workflow"


# Pre-configured workflows
def setup_default_workflows(manager: WorkflowManager) -> None:
    """Set up default workflows.

    Args:
        manager: Workflow manager instance
    """
    # Email sending workflow
    manager.register_workflow(
        workflow_id="send_email",
        name="Send Email",
        action=ApprovalAction.SEND_EMAIL,
        requires_approval=True,
    )

    # Job application workflow
    manager.register_workflow(
        workflow_id="apply_to_job",
        name="Apply to Job",
        action=ApprovalAction.APPLY_TO_JOB,
        requires_approval=True,
    )

    # Outreach message workflow
    manager.register_workflow(
        workflow_id="send_outreach",
        name="Send Networking Message",
        action=ApprovalAction.SEND_OUTREACH,
        requires_approval=True,
    )

    # Document generation (auto-approve)
    manager.register_workflow(
        workflow_id="generate_document",
        name="Generate Document",
        action=ApprovalAction.GENERATE_DOCUMENT,
        requires_approval=False,  # Auto-approve document generation
    )

    # Interview scheduling
    manager.register_workflow(
        workflow_id="schedule_interview",
        name="Schedule Interview",
        action=ApprovalAction.SCHEDULE_INTERVIEW,
        requires_approval=True,
    )

    # Offer acceptance
    manager.register_workflow(
        workflow_id="accept_offer",
        name="Accept Job Offer",
        action=ApprovalAction.ACCEPT_OFFER,
        requires_approval=True,
    )


# Example usage functions
def create_job_application_workflow(
    manager: WorkflowManager,
    user_id: str,
    job_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a job application workflow.

    Args:
        manager: Workflow manager
        user_id: User ID
        job_data: Job application data

    Returns:
        Workflow result
    """

    def on_approve(request: ApprovalRequest):
        """Callback when application is approved."""
        print(f"Application approved! Applying to {request.data.get('job_title')}")
        # Here you would actually submit the application

    return manager.execute_workflow(
        workflow_id="apply_to_job",
        user_id=user_id,
        data=job_data,
        callback=on_approve,
    )


def create_outreach_workflow(
    manager: WorkflowManager,
    user_id: str,
    outreach_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create an outreach message workflow.

    Args:
        manager: Workflow manager
        user_id: User ID
        outreach_data: Outreach message data

    Returns:
        Workflow result
    """

    def on_approve(request: ApprovalRequest):
        """Callback when outreach is approved."""
        print(f"Outreach approved! Sending to {request.data.get('contact_name')}")
        # Here you would actually send the message

    return manager.execute_workflow(
        workflow_id="send_outreach",
        user_id=user_id,
        data=outreach_data,
        callback=on_approve,
    )
