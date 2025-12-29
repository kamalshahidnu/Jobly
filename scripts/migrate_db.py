"""Database migration/initialization script.

This repo currently uses "create tables if missing" semantics rather than Alembic.
For local development this keeps setup simple.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from jobly.config.settings import settings
from jobly.memory.sqlite_store import SQLiteStore
from jobly.models.database import get_engine, init_db


def _db_path_from_url(url: str) -> str:
    if not url:
        return "jobly.db"
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "", 1)
    return url


def migrate(database_url: str) -> None:
    print(f"Migrating/initializing DB at: {database_url}")

    # SQLAlchemy models (used by `scripts/setup_db.py` + tests)
    engine = get_engine(database_url)
    init_db(engine)

    # sqlite3 schema used by service layer (safe no-op if already present)
    store = SQLiteStore(_db_path_from_url(database_url))
    store.connect()
    store.disconnect()

    print("✓ Migration/initialization complete")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize Jobly database schema.")
    parser.add_argument(
        "--database-url",
        default=settings.database_url,
        help="Database URL (default from settings)",
    )
    args = parser.parse_args()
    migrate(args.database_url)


if __name__ == "__main__":
    main()

