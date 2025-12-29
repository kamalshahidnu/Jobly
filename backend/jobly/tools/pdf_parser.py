"""PDF parser for extracting text from resume PDFs."""

from __future__ import annotations

import os
from typing import Any, Dict

import PyPDF2


class PDFParser:
    """Parse PDF documents."""

    def __init__(self):
        """Initialize PDF parser."""
        # Kept for future configuration (passwords, OCR, etc.)
        self._last_error: str | None = None

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        self._last_error = None
        if not file_path:
            return ""
        if not os.path.exists(file_path):
            return ""
        try:
            with open(file_path, "rb") as handle:
                reader = PyPDF2.PdfReader(handle)
                parts: list[str] = []
                for page in reader.pages:
                    try:
                        parts.append(page.extract_text() or "")
                    except Exception:
                        continue
                return "\n".join(p.strip() for p in parts if p and p.strip())
        except Exception as exc:
            self._last_error = str(exc)
            return ""

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            PDF metadata
        """
        self._last_error = None
        if not file_path:
            return {}
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "rb") as handle:
                reader = PyPDF2.PdfReader(handle)
                meta = reader.metadata or {}
                out: Dict[str, Any] = {}
                for k, v in dict(meta).items():
                    key = str(k).lstrip("/") if k is not None else ""
                    out[key] = str(v) if v is not None else None
                out["pages"] = len(reader.pages)
                return out
        except Exception as exc:
            self._last_error = str(exc)
            return {}
