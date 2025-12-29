"""Profile-related API routes."""

from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ...models.schemas import UserProfile
from ...services.profile_service import ProfileService
from ..deps import get_profile_service

router = APIRouter()


@router.post("/", response_model=UserProfile)
async def create_profile(
    profile_data: dict,
    service: ProfileService = Depends(get_profile_service)
):
    """Create user profile."""
    return service.create_profile(profile_data)


@router.get("/{user_id}", response_model=UserProfile)
async def get_profile(
    user_id: str,
    service: ProfileService = Depends(get_profile_service)
):
    """Get user profile."""
    profile = service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{user_id}", response_model=UserProfile)
async def update_profile(
    user_id: str,
    updates: dict,
    service: ProfileService = Depends(get_profile_service)
):
    """Update user profile."""
    profile = service.update_profile(user_id, updates)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/parse-resume")
async def parse_resume(
    file: UploadFile = File(...),
    service: ProfileService = Depends(get_profile_service)
):
    """Parse resume file and extract profile data."""
    suffix = ""
    if file.filename and "." in file.filename:
        suffix = "." + file.filename.split(".")[-1]

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        data = service.parse_resume(tmp_path)
        return {"status": "success", "data": data}
    finally:
        try:
            if "tmp_path" in locals() and tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
