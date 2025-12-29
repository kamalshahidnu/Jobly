"""Job-related API routes."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ...models.schemas import JobPosting
from ...services.job_service import JobService
from ..deps import get_job_service

router = APIRouter()


@router.post("/", response_model=JobPosting)
async def create_job(
    job_data: dict,
    service: JobService = Depends(get_job_service)
):
    """Create a new job posting."""
    return service.create_job(job_data)


@router.get("/{job_id}", response_model=JobPosting)
async def get_job(
    job_id: str,
    service: JobService = Depends(get_job_service)
):
    """Get job by ID."""
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/", response_model=List[JobPosting])
async def list_jobs(
    limit: int = 50,
    service: JobService = Depends(get_job_service)
):
    """List all jobs."""
    return service.list_jobs(limit=limit)


@router.put("/{job_id}", response_model=JobPosting)
async def update_job(
    job_id: str,
    updates: dict,
    service: JobService = Depends(get_job_service)
):
    """Update job posting."""
    job = service.update_job(job_id, updates)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    service: JobService = Depends(get_job_service)
):
    """Delete job posting."""
    success = service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "success"}


@router.get("/search/")
async def search_jobs(
    q: str,
    limit: int = 50,
    service: JobService = Depends(get_job_service)
):
    """Search jobs by query."""
    return service.search_jobs(q, limit=limit)
