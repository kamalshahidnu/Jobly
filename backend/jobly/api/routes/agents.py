"""Agent-related API routes."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ...agents.analytics_agent import AnalyticsAgent
from ...agents.application_agent import ApplicationAgent
from ...agents.assessment_agent import AssessmentAgent
from ...agents.contact_discovery_agent import ContactDiscoveryAgent
from ...agents.cover_letter_agent import CoverLetterAgent
from ...agents.dedup_agent import DedupAgent
from ...agents.email_monitor_agent import EmailMonitorAgent
from ...agents.error_handler_agent import ErrorHandlerAgent
from ...agents.followup_agent import FollowupAgent
from ...agents.interview_prep_agent import InterviewPrepAgent
from ...agents.job_ranker_agent import JobRankerAgent
from ...agents.job_search_agent import JobSearchAgent
from ...agents.offer_eval_agent import OfferEvalAgent
from ...agents.outreach_writer_agent import OutreachWriterAgent
from ...agents.profile_agent import ProfileAgent
from ...agents.resume_tailor_agent import ResumeTailorAgent
from ...agents.tracker_agent import TrackerAgent
from ...orchestrator.coordinator import AgentCoordinator

router = APIRouter()

_coordinator: AgentCoordinator | None = None


def _get_coordinator() -> AgentCoordinator:
    global _coordinator
    if _coordinator is not None:
        return _coordinator

    coordinator = AgentCoordinator()
    for agent in [
        ProfileAgent(),
        JobSearchAgent(),
        DedupAgent(),
        JobRankerAgent(),
        AnalyticsAgent(),
        ResumeTailorAgent(),
        CoverLetterAgent(),
        ContactDiscoveryAgent(),
        OutreachWriterAgent(),
        FollowupAgent(),
        ApplicationAgent(),
        AssessmentAgent(),
        EmailMonitorAgent(),
        InterviewPrepAgent(),
        TrackerAgent(),
        ErrorHandlerAgent(),
        OfferEvalAgent(),
    ]:
        coordinator.register_agent(agent)

    _coordinator = coordinator
    return coordinator


def _normalize_agent_name(agent_name: str) -> str:
    # Accept both "profile_agent" and "ProfileAgent".
    name = (agent_name or "").strip()
    if not name:
        return ""
    if "_" in name:
        parts = [p for p in name.replace("-", "_").split("_") if p]
        return "".join([p[:1].upper() + p[1:] for p in parts[:-1]]) + "Agent"
    if not name.lower().endswith("agent"):
        return name + "Agent"
    return name

@router.post("/execute/{agent_name}")
async def execute_agent(
    agent_name: str,
    input_data: Dict[str, Any]
):
    """Execute a specific agent."""
    coordinator = _get_coordinator()
    normalized = _normalize_agent_name(agent_name)
    agent = coordinator.get_agent(normalized)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_name}")
    result = await agent.execute(input_data or {})
    return {"status": "success", "agent": normalized, "result": result}


@router.get("/status/{agent_name}")
async def get_agent_status(
    agent_name: str
):
    """Get agent execution status."""
    coordinator = _get_coordinator()
    normalized = _normalize_agent_name(agent_name)
    agent = coordinator.get_agent(normalized)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_name}")
    # Phase 1: no background job runner; treat as always idle.
    return {"agent": normalized, "status": "idle", "state": agent.state}


@router.post("/workflow/execute")
async def execute_workflow(
    workflow: list,
    input_data: Dict[str, Any]
):
    """Execute a workflow of agents."""
    coordinator = _get_coordinator()
    if not isinstance(workflow, list) or not workflow:
        raise HTTPException(status_code=400, detail="workflow must be a non-empty list of agent names")

    resolved: List[str] = []
    for name in workflow:
        normalized = _normalize_agent_name(str(name))
        if not coordinator.get_agent(normalized):
            raise HTTPException(status_code=404, detail=f"Unknown agent: {name}")
        resolved.append(normalized)

    result = await coordinator.execute_workflow(resolved, input_data or {})
    return {"status": "success", "workflow": resolved, "result": result}


@router.get("/list")
async def list_agents():
    """List all available agents."""
    agents = [
        "profile_agent",
        "job_search_agent",
        "dedup_agent",
        "job_ranker_agent",
        "analytics_agent",
        "resume_tailor_agent",
        "cover_letter_agent",
        "contact_discovery_agent",
        "outreach_writer_agent",
        "followup_agent",
        "application_agent",
        "assessment_agent",
        "email_monitor_agent",
        "interview_prep_agent",
        "tracker_agent",
        "error_handler_agent",
        "offer_eval_agent"
    ]
    return {"agents": agents}
