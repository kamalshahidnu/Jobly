"""Document-related API routes."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ...services.document_service import DocumentService
from ..deps import get_document_service

router = APIRouter()


@router.post("/resume/generate")
async def generate_resume(
    user_id: str,
    job_id: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Generate or tailor resume."""
    content = service.generate_resume(user_id, job_id)
    return {"content": content}


@router.post("/cover-letter/generate")
async def generate_cover_letter(
    user_id: str,
    job_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Generate cover letter."""
    content = service.generate_cover_letter(user_id, job_id)
    return {"content": content}


@router.post("/save")
async def save_document(
    user_id: str,
    doc_type: str,
    content: str,
    metadata: Optional[dict] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Save document."""
    doc_id = service.save_document(user_id, doc_type, content, metadata)
    return {"doc_id": doc_id}


@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID."""
    doc = service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/user/{user_id}")
async def list_user_documents(
    user_id: str,
    doc_type: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """List user documents."""
    return service.list_documents(user_id, doc_type)
