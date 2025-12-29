"""Script to set up the database."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from jobly.models.database import get_engine, init_db
from jobly.config.settings import settings


def setup_database():
    """Initialize the database with tables."""
    print(f"Setting up database at: {settings.database_url}")

    engine = get_engine(settings.database_url)
    init_db(engine)

    print("✓ Database initialized successfully!")
    print("Tables created:")
    print("  - users")
    print("  - jobs")
    print("  - applications")
    print("  - contacts")


if __name__ == "__main__":
    setup_database()
