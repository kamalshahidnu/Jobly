"""Outreach service for networking and contact management."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..models.schemas import Contact
from ..memory.sqlite_store import SQLiteStore
from ..tools.gmail_client import GmailClient


class OutreachService:
    """Service layer for outreach operations."""

    def __init__(self, store: SQLiteStore):
        """Initialize outreach service.

        Args:
            store: Database store instance
        """
        self.store = store

    def create_contact(self, contact_data: Dict[str, Any]) -> Contact:
        """Create new contact.

        Args:
            contact_data: Contact data

        Returns:
            Created contact
        """
        payload = dict(contact_data or {})
        payload.setdefault("id", str(uuid4()))
        contact = Contact(**payload)
        row = {
            "id": contact.id,
            "name": contact.name,
            "email": str(contact.email) if contact.email else None,
            "linkedin_url": contact.linkedin_url,
            "company": contact.company,
            "position": contact.position,
            "notes": contact.notes,
            "last_contacted": contact.last_contacted.isoformat() if contact.last_contacted else None,
            "created_at": contact.created_at.isoformat(),
        }
        self.store.insert("contacts", row)
        return contact

    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """Get contact by ID.

        Args:
            contact_id: Contact ID

        Returns:
            Contact or None
        """
        row = self.store.fetch_one("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        if not row:
            return None
        last = row.get("last_contacted")
        if last:
            try:
                row["last_contacted"] = datetime.fromisoformat(last)
            except ValueError:
                row["last_contacted"] = None
        created = row.get("created_at")
        if created:
            try:
                row["created_at"] = datetime.fromisoformat(created)
            except ValueError:
                row["created_at"] = datetime.utcnow()
        return Contact(**row)

    def list_contacts(self, filters: Optional[Dict[str, Any]] = None) -> List[Contact]:
        """List contacts with optional filters.

        Args:
            filters: Optional filter criteria

        Returns:
            List of contacts
        """
        filters = filters or {}
        where: List[str] = []
        params: List[Any] = []

        if company := filters.get("company"):
            where.append("LOWER(company) = LOWER(?)")
            params.append(company)
        if email := filters.get("email"):
            where.append("LOWER(email) = LOWER(?)")
            params.append(email)

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        rows = self.store.fetch_all(
            f"SELECT * FROM contacts {where_sql} ORDER BY created_at DESC",
            tuple(params),
        )
        contacts: List[Contact] = []
        for row in rows:
            last = row.get("last_contacted")
            if last:
                try:
                    row["last_contacted"] = datetime.fromisoformat(last)
                except ValueError:
                    row["last_contacted"] = None
            created = row.get("created_at")
            if created:
                try:
                    row["created_at"] = datetime.fromisoformat(created)
                except ValueError:
                    row["created_at"] = datetime.utcnow()
            contacts.append(Contact(**row))
        return contacts

    def generate_outreach_message(self, contact_id: str, context: Dict[str, Any]) -> str:
        """Generate personalized outreach message.

        Args:
            contact_id: Target contact ID
            context: Context for message generation

        Returns:
            Generated message
        """
        contact = self.get_contact(contact_id)
        if not contact:
            raise ValueError("Contact not found")

        ctx = context or {}
        sender_name = ctx.get("sender_name", "there")
        target_role = ctx.get("target_role") or "a role"
        reason = ctx.get("reason") or "I’m exploring new opportunities and would love your perspective."
        ask = ctx.get("ask") or "Would you be open to a quick 15-minute chat this week?"
        company = contact.company or "your company"
        position = contact.position or "your team"

        return (
            f"Hi {contact.name},\n\n"
            f"I hope you’re doing well. I’m {sender_name} and I’m interested in {target_role} at {company}. "
            f"I came across your profile and noticed your work as {position}.\n\n"
            f"{reason}\n\n"
            f"{ask}\n\n"
            f"Thanks,\n{sender_name}\n"
        )

    def send_message(self, contact_id: str, message: str, method: str = "email") -> bool:
        """Send outreach message to contact.

        Args:
            contact_id: Target contact ID
            message: Message content
            method: Communication method

        Returns:
            Success status
        """
        contact = self.get_contact(contact_id)
        if not contact:
            return False
        if method.lower() != "email":
            # Future: LinkedIn, SMS, etc.
            return False
        if not contact.email:
            return False

        client = GmailClient()
        ok = client.send_email(
            to=str(contact.email),
            subject="Quick question",
            body=message,
        )
        if ok:
            self.store.update(
                "contacts",
                contact_id,
                {"last_contacted": datetime.utcnow().isoformat(timespec="seconds")},
            )
        return ok
