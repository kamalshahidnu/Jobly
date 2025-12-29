"""Outreach-related API routes."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...models.schemas import Contact
from ...services.outreach_service import OutreachService
from ..deps import get_outreach_service

router = APIRouter()


@router.post("/contacts", response_model=Contact)
async def create_contact(
    contact_data: dict,
    service: OutreachService = Depends(get_outreach_service)
):
    """Create new contact."""
    return service.create_contact(contact_data)


@router.get("/contacts/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: str,
    service: OutreachService = Depends(get_outreach_service)
):
    """Get contact by ID."""
    contact = service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/contacts", response_model=List[Contact])
async def list_contacts(
    service: OutreachService = Depends(get_outreach_service)
):
    """List all contacts."""
    return service.list_contacts()


@router.post("/generate-message")
async def generate_message(
    contact_id: str,
    context: dict,
    service: OutreachService = Depends(get_outreach_service)
):
    """Generate personalized outreach message."""
    message = service.generate_outreach_message(contact_id, context)
    return {"message": message}


@router.post("/send-message")
async def send_message(
    contact_id: str,
    message: str,
    method: str = "email",
    service: OutreachService = Depends(get_outreach_service)
):
    """Send message to contact."""
    success = service.send_message(contact_id, message, method)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send message")
    return {"status": "success"}
