"""Document generator for creating resumes and cover letters."""

from __future__ import annotations

import os
from typing import Dict, Any

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class DocGenerator:
    """Generate professional documents."""

    def __init__(self):
        """Initialize document generator."""
        self.page_size = LETTER

    def generate_resume_pdf(self, content: Dict[str, Any], output_path: str) -> str:
        """Generate resume PDF.

        Args:
            content: Resume content
            output_path: Output file path

        Returns:
            Path to generated PDF
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        c = canvas.Canvas(output_path, pagesize=self.page_size)
        width, height = self.page_size

        y = height - 1 * inch
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, y, str(content.get("name") or "Resume"))
        y -= 0.35 * inch

        c.setFont("Helvetica", 10)
        for key in ("email", "phone", "location"):
            val = content.get(key)
            if val:
                c.drawString(1 * inch, y, f"{key.title()}: {val}")
                y -= 0.22 * inch

        skills = content.get("skills") or []
        if skills:
            y -= 0.15 * inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, y, "Skills")
            y -= 0.25 * inch
            c.setFont("Helvetica", 10)
            c.drawString(1 * inch, y, ", ".join([str(s) for s in skills]))
            y -= 0.35 * inch

        resume_text = content.get("resume_text") or content.get("text") or ""
        if resume_text:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, y, "Summary")
            y -= 0.25 * inch
            c.setFont("Helvetica", 10)
            for line in str(resume_text).splitlines():
                if y < 1 * inch:
                    c.showPage()
                    y = height - 1 * inch
                    c.setFont("Helvetica", 10)
                c.drawString(1 * inch, y, line[:120])
                y -= 0.18 * inch

        c.save()
        return output_path

    def generate_cover_letter_pdf(self, content: str, output_path: str) -> str:
        """Generate cover letter PDF.

        Args:
            content: Cover letter text
            output_path: Output file path

        Returns:
            Path to generated PDF
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        c = canvas.Canvas(output_path, pagesize=self.page_size)
        width, height = self.page_size

        y = height - 1 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y, "Cover Letter")
        y -= 0.4 * inch

        c.setFont("Helvetica", 11)
        for paragraph in str(content or "").split("\n\n"):
            for line in paragraph.splitlines() or [""]:
                if y < 1 * inch:
                    c.showPage()
                    y = height - 1 * inch
                    c.setFont("Helvetica", 11)
                c.drawString(1 * inch, y, line[:120])
                y -= 0.22 * inch
            y -= 0.18 * inch

        c.save()
        return output_path
