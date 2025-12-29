"""Gmail client for email operations."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import List, Dict, Any

from ..config.settings import settings


class GmailClient:
    """Client for Gmail API operations."""

    def __init__(self, credentials_path: str = None):
        """Initialize Gmail client.

        Args:
            credentials_path: Path to Gmail API credentials
        """
        self.credentials_path = credentials_path

    def send_email(self, to: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Send email via Gmail.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            attachments: List of attachment paths

        Returns:
            Success status
        """
        attachments = attachments or []
        if not to:
            return False

        # Phase 1: support SMTP (Gmail App Password / any SMTP relay).
        if not settings.smtp_server or not settings.smtp_username or not settings.smtp_password:
            return False

        msg = EmailMessage()
        msg["From"] = settings.smtp_username
        msg["To"] = to
        msg["Subject"] = subject or ""
        msg.set_content(body or "")

        for path in attachments:
            if not path or not os.path.exists(path):
                continue
            try:
                with open(path, "rb") as handle:
                    data = handle.read()
                filename = os.path.basename(path)
                # Default to application/octet-stream
                msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=filename)
            except OSError:
                continue

        try:
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(msg)
            return True
        except Exception:
            return False

    def fetch_emails(self, query: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail.

        Args:
            query: Gmail search query
            max_results: Maximum number of emails to fetch

        Returns:
            List of email messages
        """
        # Not implemented in Phase 1 (requires Gmail OAuth scopes and token storage).
        # The interface is here so the rest of the system can depend on it.
        return []
