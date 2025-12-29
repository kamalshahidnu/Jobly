"""State machine for managing application workflow states."""

from typing import Dict, Any, Optional
from enum import Enum


class WorkflowState(str, Enum):
    """Workflow state enumeration."""
    INIT = "init"
    PROFILE_PARSING = "profile_parsing"
    JOB_SEARCH = "job_search"
    JOB_RANKING = "job_ranking"
    DOCUMENT_PREP = "document_prep"
    CONTACT_DISCOVERY = "contact_discovery"
    OUTREACH = "outreach"
    APPLICATION = "application"
    INTERVIEW = "interview"
    OFFER = "offer"
    COMPLETE = "complete"
    ERROR = "error"


class StateMachine:
    """State machine for workflow management."""

    def __init__(self, initial_state: WorkflowState = WorkflowState.INIT):
        """Initialize state machine.

        Args:
            initial_state: Initial workflow state
        """
        self.current_state = initial_state
        self.state_history = [initial_state]
        self.context: Dict[str, Any] = {}
        self._allowed_transitions: Dict[WorkflowState, set[WorkflowState]] = {
            WorkflowState.INIT: {WorkflowState.PROFILE_PARSING, WorkflowState.JOB_SEARCH, WorkflowState.ERROR},
            WorkflowState.PROFILE_PARSING: {WorkflowState.JOB_SEARCH, WorkflowState.ERROR},
            WorkflowState.JOB_SEARCH: {WorkflowState.JOB_RANKING, WorkflowState.ERROR},
            WorkflowState.JOB_RANKING: {WorkflowState.DOCUMENT_PREP, WorkflowState.ERROR},
            WorkflowState.DOCUMENT_PREP: {WorkflowState.CONTACT_DISCOVERY, WorkflowState.APPLICATION, WorkflowState.ERROR},
            WorkflowState.CONTACT_DISCOVERY: {WorkflowState.OUTREACH, WorkflowState.ERROR},
            WorkflowState.OUTREACH: {WorkflowState.APPLICATION, WorkflowState.ERROR},
            WorkflowState.APPLICATION: {WorkflowState.INTERVIEW, WorkflowState.COMPLETE, WorkflowState.ERROR},
            WorkflowState.INTERVIEW: {WorkflowState.OFFER, WorkflowState.COMPLETE, WorkflowState.ERROR},
            WorkflowState.OFFER: {WorkflowState.COMPLETE, WorkflowState.ERROR},
            WorkflowState.COMPLETE: {WorkflowState.INIT},
            WorkflowState.ERROR: {WorkflowState.INIT},
        }

    def transition(self, new_state: WorkflowState, context: Optional[Dict[str, Any]] = None) -> bool:
        """Transition to a new state.

        Args:
            new_state: Target state
            context: Additional context data

        Returns:
            Success status
        """
        if not self.can_transition_to(new_state):
            return False
        self.current_state = new_state
        self.state_history.append(new_state)
        if context:
            self.context.update(context)
        return True

    def can_transition_to(self, target_state: WorkflowState) -> bool:
        """Check if transition to target state is valid.

        Args:
            target_state: Target state

        Returns:
            Whether transition is valid
        """
        allowed = self._allowed_transitions.get(self.current_state)
        if not allowed:
            return False
        return target_state in allowed

    def get_current_state(self) -> WorkflowState:
        """Get current workflow state.

        Returns:
            Current state
        """
        return self.current_state
