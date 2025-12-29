"""Analytics-related API routes."""

from fastapi import APIRouter, Depends
from ...services.analytics_service import AnalyticsService
from ..deps import get_analytics_service

router = APIRouter()


@router.get("/stats/{user_id}")
async def get_application_stats(
    user_id: str,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get application statistics."""
    return service.get_application_stats(user_id)


@router.get("/response-rate/{user_id}")
async def get_response_rate(
    user_id: str,
    days: int = 30,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get response rate."""
    rate = service.get_response_rate(user_id, days)
    return {"response_rate": rate, "days": days}


@router.get("/time-to-response/{user_id}")
async def get_time_to_response(
    user_id: str,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get time to response statistics."""
    return service.get_time_to_response(user_id)


@router.get("/pipeline/{user_id}")
async def get_pipeline(
    user_id: str,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get job pipeline by stage."""
    return service.get_job_pipeline(user_id)


@router.get("/trends/{user_id}")
async def get_trends(
    user_id: str,
    metric: str,
    days: int = 30,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get trend data for metric."""
    return service.get_trends(user_id, metric, days)


@router.get("/success-metrics/{user_id}")
async def get_success_metrics(
    user_id: str,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get success metrics."""
    return service.get_success_metrics(user_id)
