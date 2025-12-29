"""Data validation utilities."""

import re
from typing import Optional
from email_validator import validate_email as validate_email_address, EmailNotValidError


def validate_email(email: str) -> bool:
    """Validate email address.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        validate_email_address(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone(phone: str) -> bool:
    """Validate phone number.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Basic phone validation (US format)
    pattern = r'^\+?1?\d{9,15}$'
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(pattern, cleaned))


def validate_url(url: str) -> bool:
    """Validate URL.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://[\w\-\.]+(:\d+)?(/.*)?$'
    return bool(re.match(pattern, url))


def validate_linkedin_url(url: str) -> bool:
    """Validate LinkedIn profile URL.

    Args:
        url: LinkedIn URL to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$'
    return bool(re.match(pattern, url))


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize text input.

    Args:
        text: Text to sanitize
        max_length: Optional maximum length

    Returns:
        Sanitized text
    """
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # Trim whitespace
    sanitized = sanitized.strip()

    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_job_status(status: str) -> bool:
    """Validate job application status.

    Args:
        status: Status to validate

    Returns:
        True if valid, False otherwise
    """
    valid_statuses = {
        "discovered", "ranked", "preparing", "ready_to_apply",
        "applied", "interviewing", "offered", "accepted",
        "rejected", "withdrawn"
    }
    return status.lower() in valid_statuses
