"""Document service for resume and cover letter generation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from ..memory.sqlite_store import SQLiteStore


class DocumentService:
    """Service layer for document operations."""

    def __init__(self, store: SQLiteStore):
        """Initialize document service.

        Args:
            store: Database store instance
        """
        self.store = store

    def generate_resume(self, user_id: str, job_id: Optional[str] = None) -> str:
        """Generate or tailor resume.

        Args:
            user_id: User ID
            job_id: Optional job ID for tailoring

        Returns:
            Generated resume content
        """
        user = self.store.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        job = self.store.fetch_one("SELECT * FROM jobs WHERE id = ?", (job_id,)) if job_id else None
        if not user:
            raise ValueError("User profile not found")
        skills = self.store.loads(user.get("skills"), [])
        headline = f"{user.get('name')} — {user.get('location') or ''}".strip(" —")

        lines = [
            f"# {headline}",
            "",
            f"Email: {user.get('email')}",
        ]
        if user.get("phone"):
            lines.append(f"Phone: {user.get('phone')}")
        lines.append("")
        if skills:
            lines.extend(["## Skills", ", ".join(skills), ""])
        if job:
            lines.extend(
                [
                    "## Target Role",
                    f"{job.get('title')} — {job.get('company')}",
                    "",
                    "## Tailoring Notes",
                    "This resume was lightly tailored to emphasize matching skills and experience.",
                    "",
                ]
            )
        if user.get("resume_text"):
            lines.extend(["## Resume Text (Raw)", user["resume_text"]])
        return "\n".join(lines).strip() + "\n"

    def generate_cover_letter(self, user_id: str, job_id: str) -> str:
        """Generate cover letter for job application.

        Args:
            user_id: User ID
            job_id: Job ID

        Returns:
            Generated cover letter content
        """
        user = self.store.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        job = self.store.fetch_one("SELECT * FROM jobs WHERE id = ?", (job_id,))
        if not user:
            raise ValueError("User profile not found")
        if not job:
            raise ValueError("Job not found")

        name = user.get("name", "Applicant")
        company = job.get("company", "your company")
        title = job.get("title", "the role")
        skills = self.store.loads(user.get("skills"), [])
        top_skills = ", ".join(list(skills)[:3]) if skills else "relevant skills"

        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I’m excited to apply for the {title} position. I’m {name}, and I believe my background in "
            f"{top_skills} aligns well with what you’re looking for.\n\n"
            "In my previous work, I’ve delivered impact by building reliable systems, collaborating closely "
            "with cross-functional teams, and iterating quickly based on feedback.\n\n"
            f"Thank you for your time and consideration. I’d welcome the chance to discuss how I can contribute to {company}.\n\n"
            f"Sincerely,\n{name}\n"
        )

    def save_document(self, user_id: str, doc_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save document to storage.

        Args:
            user_id: User ID
            doc_type: Document type (resume, cover_letter, etc.)
            content: Document content
            metadata: Optional metadata

        Returns:
            Document ID
        """
        doc_id = str(uuid4())
        row = {
            "id": doc_id,
            "user_id": user_id,
            "doc_type": doc_type,
            "content": content,
            "metadata": self.store.dumps(metadata or {}),
            "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        }
        self.store.insert("documents", row)
        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document data or None
        """
        row = self.store.fetch_one("SELECT * FROM documents WHERE id = ?", (doc_id,))
        if not row:
            return None
        row["metadata"] = self.store.loads(row.get("metadata"), {})
        return row

    def list_documents(self, user_id: str, doc_type: Optional[str] = None) -> list:
        """List user documents.

        Args:
            user_id: User ID
            doc_type: Optional document type filter

        Returns:
            List of documents
        """
        if doc_type:
            rows = self.store.fetch_all(
                "SELECT * FROM documents WHERE user_id = ? AND doc_type = ? ORDER BY created_at DESC",
                (user_id, doc_type),
            )
        else:
            rows = self.store.fetch_all(
                "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,),
            )
        for row in rows:
            row["metadata"] = self.store.loads(row.get("metadata"), {})
        return rows
