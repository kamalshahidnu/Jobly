"""Profile service for user profile operations."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from ..agents.profile_agent import ProfileAgent
from ..models.schemas import UserProfile
from ..memory.sqlite_store import SQLiteStore
from ..tools.pdf_parser import PDFParser


class ProfileService:
    """Service layer for profile operations."""

    def __init__(self, store: SQLiteStore):
        """Initialize profile service.

        Args:
            store: Database store instance
        """
        self.store = store

    def create_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Create user profile.

        Args:
            profile_data: Profile data

        Returns:
            Created profile
        """
        payload = dict(profile_data or {})
        payload.setdefault("id", str(uuid4()))
        profile = UserProfile(**payload)

        row = {
            "id": profile.id,
            "name": profile.name,
            "email": str(profile.email),
            "phone": profile.phone,
            "location": profile.location,
            "skills": self.store.dumps(profile.skills),
            "experience_years": profile.experience_years,
            "resume_text": profile.resume_text,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        }
        self.store.insert("users", row)
        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile.

        Args:
            user_id: User ID

        Returns:
            User profile or None
        """
        row = self.store.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if not row:
            return None
        row["skills"] = self.store.loads(row.get("skills"), [])
        created = row.get("created_at")
        if created:
            try:
                row["created_at"] = datetime.fromisoformat(created)
            except ValueError:
                row["created_at"] = datetime.utcnow()
        updated = row.get("updated_at")
        if updated:
            try:
                row["updated_at"] = datetime.fromisoformat(updated)
            except ValueError:
                row["updated_at"] = datetime.utcnow()
        return UserProfile(**row)

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile.

        Args:
            user_id: User ID
            updates: Fields to update

        Returns:
            Updated profile or None
        """
        existing = self.get_profile(user_id)
        if not existing:
            return None
        patch = dict(updates or {})
        merged = existing.model_copy(update=patch)

        update_row: Dict[str, Any] = {"updated_at": datetime.utcnow().isoformat(timespec="seconds")}
        for key in ("name", "phone", "location", "experience_years", "resume_text"):
            if key in patch:
                update_row[key] = getattr(merged, key)
        if "email" in patch:
            update_row["email"] = str(merged.email)
        if "skills" in patch:
            update_row["skills"] = self.store.dumps(merged.skills)

        self.store.update("users", user_id, update_row)
        return self.get_profile(user_id)

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume and extract profile data.

        Args:
            file_path: Path to resume file

        Returns:
            Extracted profile data
        """
        file_path = str(file_path)
        resume_text = ""
        if file_path.lower().endswith(".pdf"):
            resume_text = PDFParser().extract_text(file_path)
        else:
            try:
                with open(file_path, "r", encoding="utf-8") as handle:
                    resume_text = handle.read()
            except OSError:
                resume_text = ""

        agent = ProfileAgent()
        # ProfileAgent is async; to keep service sync, we use a small fallback.
        # If there's an active event loop (e.g. inside FastAPI), callers should run the agent directly.
        try:
            import asyncio

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # best-effort parse without awaiting
                return {"resume_text": resume_text}

            result = asyncio.run(agent.execute({"resume_text": resume_text}))
            return result.get("profile", {"resume_text": resume_text})
        except Exception:
            return {"resume_text": resume_text}
