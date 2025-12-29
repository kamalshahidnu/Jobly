"""FastAPI dependencies."""

from typing import Generator
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


def get_job_service(store: SQLiteStore = None) -> JobService:
    """Get job service dependency.

    Args:
        store: Database store

    Returns:
        JobService instance
    """
    if store is None:
        store = SQLiteStore()
    return JobService(store)


def get_profile_service(store: SQLiteStore = None) -> ProfileService:
    """Get profile service dependency.

    Args:
        store: Database store

    Returns:
        ProfileService instance
    """
    if store is None:
        store = SQLiteStore()
    return ProfileService(store)


def get_outreach_service(store: SQLiteStore = None) -> OutreachService:
    """Get outreach service dependency.

    Args:
        store: Database store

    Returns:
        OutreachService instance
    """
    if store is None:
        store = SQLiteStore()
    return OutreachService(store)


def get_document_service(store: SQLiteStore = None) -> DocumentService:
    """Get document service dependency.

    Args:
        store: Database store

    Returns:
        DocumentService instance
    """
    if store is None:
        store = SQLiteStore()
    return DocumentService(store)


def get_analytics_service(store: SQLiteStore = None) -> AnalyticsService:
    """Get analytics service dependency.

    Args:
        store: Database store

    Returns:
        AnalyticsService instance
    """
    if store is None:
        store = SQLiteStore()
    return AnalyticsService(store)
