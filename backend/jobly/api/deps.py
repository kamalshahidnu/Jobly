"""FastAPI dependencies."""

from typing import Generator
from fastapi import Depends
from ..memory.sqlite_store import SQLiteStore
from ..services.job_service import JobService
from ..services.profile_service import ProfileService
from ..services.outreach_service import OutreachService
from ..services.document_service import DocumentService
from ..services.analytics_service import AnalyticsService


def get_db_store() -> Generator[SQLiteStore, None, None]:
    """Get database store dependency.

    Yields:
        SQLiteStore instance
    """
    store = SQLiteStore()
    try:
        store.connect()
        yield store
    finally:
        store.disconnect()


def get_job_service(store: SQLiteStore = Depends(get_db_store)) -> JobService:
    """Get job service dependency.

    Args:
        store: Database store

    Returns:
        JobService instance
    """
    return JobService(store)


def get_profile_service(store: SQLiteStore = Depends(get_db_store)) -> ProfileService:
    """Get profile service dependency.

    Args:
        store: Database store

    Returns:
        ProfileService instance
    """
    return ProfileService(store)


def get_outreach_service(store: SQLiteStore = Depends(get_db_store)) -> OutreachService:
    """Get outreach service dependency.

    Args:
        store: Database store

    Returns:
        OutreachService instance
    """
    return OutreachService(store)


def get_document_service(store: SQLiteStore = Depends(get_db_store)) -> DocumentService:
    """Get document service dependency.

    Args:
        store: Database store

    Returns:
        DocumentService instance
    """
    return DocumentService(store)


def get_analytics_service(store: SQLiteStore = Depends(get_db_store)) -> AnalyticsService:
    """Get analytics service dependency.

    Args:
        store: Database store

    Returns:
        AnalyticsService instance
    """
    return AnalyticsService(store)
