"""Gmail client for email operations."""

from __future__ import annotations

import os
import smtplib
import pickle
import base64
from email.message import EmailMessage
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..config.settings import settings

# Google API imports (optional - gracefully degrade if not available)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


class GmailClient:
    """Client for Gmail API operations."""

    # Gmail API scopes
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    def __init__(self, credentials_path: str = None, token_path: str = None):
        """Initialize Gmail client.

        Args:
            credentials_path: Path to Gmail API credentials JSON
            token_path: Path to store OAuth token
        """
        self.credentials_path = credentials_path or settings.gmail_credentials_path
        self.token_path = token_path or os.path.expanduser("~/.jobly/gmail_token.pickle")
        self.service = None
        self.creds = None

        if GOOGLE_API_AVAILABLE:
            self._authenticate()

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

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2."""
        if not GOOGLE_API_AVAILABLE:
            print("Google API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return

        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                self.creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    self.creds = None

            # If still no valid credentials, run OAuth flow
            if not self.creds and self.credentials_path and os.path.exists(self.credentials_path):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error in OAuth flow: {e}")
                    return

            # Save the credentials
            if self.creds:
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, "wb") as token:
                    pickle.dump(self.creds, token)

        # Build service
        if self.creds:
            try:
                self.service = build("gmail", "v1", credentials=self.creds)
            except Exception as e:
                print(f"Error building Gmail service: {e}")

    def is_authenticated(self) -> bool:
        """Check if client is authenticated with Gmail API.

        Returns:
            True if authenticated
        """
        return self.service is not None

    def fetch_emails(
        self,
        query: str = None,
        max_results: int = 10,
        after_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail.

        Args:
            query: Gmail search query (e.g., "subject:interview", "from:recruiter@company.com")
            max_results: Maximum number of emails to fetch
            after_date: Only fetch emails after this date

        Returns:
            List of email messages
        """
        if not self.is_authenticated():
            print("Gmail client not authenticated")
            return []

        try:
            # Build query
            search_query = query or ""
            if after_date:
                date_str = after_date.strftime("%Y/%m/%d")
                search_query = f"{search_query} after:{date_str}".strip()

            # Fetch message list
            results = self.service.users().messages().list(
                userId="me",
                q=search_query,
                maxResults=max_results,
            ).execute()

            messages = results.get("messages", [])
            emails = []

            # Fetch full message details
            for msg in messages:
                try:
                    email_data = self._get_email_details(msg["id"])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    print(f"Error fetching email {msg['id']}: {e}")

            return emails

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed email information.

        Args:
            message_id: Gmail message ID

        Returns:
            Email details
        """
        try:
            message = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="full",
            ).execute()

            headers = message.get("payload", {}).get("headers", [])
            headers_dict = {h["name"].lower(): h["value"] for h in headers}

            # Extract body
            body = self._extract_body(message.get("payload", {}))

            # Parse date
            date_str = headers_dict.get("date", "")
            received_date = None
            if date_str:
                try:
                    from email.utils import parsedate_to_datetime
                    received_date = parsedate_to_datetime(date_str)
                except Exception:
                    pass

            return {
                "id": message_id,
                "thread_id": message.get("threadId"),
                "from": headers_dict.get("from", ""),
                "to": headers_dict.get("to", ""),
                "subject": headers_dict.get("subject", ""),
                "date": received_date.isoformat() if received_date else date_str,
                "body": body,
                "labels": message.get("labelIds", []),
                "snippet": message.get("snippet", ""),
            }

        except Exception as e:
            print(f"Error getting email details: {e}")
            return None

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload.

        Args:
            payload: Gmail message payload

        Returns:
            Email body text
        """
        body = ""

        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        elif "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        break
                elif part["mimeType"] == "text/html" and not body:
                    if "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                elif "parts" in part:
                    # Recursive for nested parts
                    body = self._extract_body(part)
                    if body:
                        break

        return body

    def search_job_emails(
        self,
        keywords: Optional[List[str]] = None,
        days_back: int = 30,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search for job-related emails.

        Args:
            keywords: Keywords to search for (e.g., ["interview", "offer", "application"])
            days_back: Number of days to search back
            max_results: Maximum results

        Returns:
            List of job-related emails
        """
        # Build query for job-related emails
        default_keywords = [
            "interview",
            "offer",
            "application",
            "position",
            "opportunity",
            "recruiter",
            "hiring",
        ]

        keywords = keywords or default_keywords
        query_parts = [f"({' OR '.join(keywords)})"]

        after_date = datetime.now() - timedelta(days=days_back)

        return self.fetch_emails(
            query=" ".join(query_parts),
            max_results=max_results,
            after_date=after_date,
        )

    def categorize_email(self, email: Dict[str, Any]) -> str:
        """Categorize an email as interview, offer, rejection, etc.

        Args:
            email: Email data

        Returns:
            Category (interview, offer, rejection, general, etc.)
        """
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        snippet = email.get("snippet", "").lower()

        text = f"{subject} {body} {snippet}"

        # Check for specific categories
        if any(word in text for word in ["offer", "congratulations", "pleased to offer"]):
            return "offer"
        elif any(word in text for word in ["interview", "schedule", "meeting", "call"]):
            return "interview"
        elif any(word in text for word in ["unfortunately", "not moving forward", "not selected", "rejection"]):
            return "rejection"
        elif any(word in text for word in ["application received", "thank you for applying"]):
            return "acknowledgment"
        elif any(word in text for word in ["assessment", "test", "coding challenge"]):
            return "assessment"
        else:
            return "general"

    def mark_as_read(self, message_id: str) -> bool:
        """Mark email as read.

        Args:
            message_id: Gmail message ID

        Returns:
            Success status
        """
        if not self.is_authenticated():
            return False

        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False

    def add_label(self, message_id: str, label: str) -> bool:
        """Add label to email.

        Args:
            message_id: Gmail message ID
            label: Label to add

        Returns:
            Success status
        """
        if not self.is_authenticated():
            return False

        try:
            # Get or create label
            label_id = self._get_or_create_label(label)
            if not label_id:
                return False

            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"addLabelIds": [label_id]},
            ).execute()
            return True
        except Exception as e:
            print(f"Error adding label: {e}")
            return False

    def _get_or_create_label(self, label_name: str) -> Optional[str]:
        """Get or create a Gmail label.

        Args:
            label_name: Label name

        Returns:
            Label ID
        """
        try:
            # Get existing labels
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            # Check if label exists
            for label in labels:
                if label["name"] == label_name:
                    return label["id"]

            # Create new label
            label_object = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            }
            created_label = self.service.users().labels().create(
                userId="me",
                body=label_object,
            ).execute()

            return created_label["id"]

        except Exception as e:
            print(f"Error getting/creating label: {e}")
            return None
