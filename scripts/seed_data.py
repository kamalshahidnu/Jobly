"""Seed the local database with demo data."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from jobly.config.settings import settings
from jobly.memory.sqlite_store import SQLiteStore


def _db_path_from_url(url: str) -> str:
    if not url:
        return "jobly.db"
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "", 1)
    return url


def seed(database_url: str, user_id: str = "demo_user") -> None:
    store = SQLiteStore(_db_path_from_url(database_url))
    store.connect()

    now = datetime.utcnow().isoformat(timespec="seconds")

    # Upsert-ish demo user
    existing = store.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if existing:
        store.update(
            "users",
            user_id,
            {
                "updated_at": now,
            },
        )
    else:
        store.insert(
            "users",
            {
                "id": user_id,
                "name": "Demo User",
                "email": "demo@example.com",
                "phone": "+15551234567",
                "location": "Remote",
                "skills": json.dumps(["Python", "FastAPI", "SQL", "Streamlit"]),
                "experience_years": 5,
                "resume_text": "Demo resume text for Jobly.",
                "created_at": now,
                "updated_at": now,
            },
        )

    # Insert a couple demo jobs if none exist
    jobs_cnt = store.fetch_one("SELECT COUNT(*) as cnt FROM jobs", ()) or {"cnt": 0}
    if int(jobs_cnt["cnt"]) == 0:
        store.insert(
            "jobs",
            {
                "id": "demo_job_1",
                "title": "Software Engineer",
                "company": "Example Corp",
                "location": "Remote",
                "description": "Build APIs and ship features.",
                "requirements": json.dumps(["Python", "API development", "SQL"]),
                "url": "https://example.com/jobs/1",
                "source": "seed",
                "posted_date": now,
                "salary_range": "$120k-$160k",
                "job_type": "full_time",
                "created_at": now,
            },
        )
        store.insert(
            "jobs",
            {
                "id": "demo_job_2",
                "title": "Backend Engineer",
                "company": "Acme Inc",
                "location": "San Francisco, CA",
                "description": "Own backend systems and reliability.",
                "requirements": json.dumps(["Python", "FastAPI", "Docker"]),
                "url": "https://example.com/jobs/2",
                "source": "seed",
                "posted_date": now,
                "salary_range": "$140k-$190k",
                "job_type": "full_time",
                "created_at": now,
            },
        )

    store.disconnect()
    print("✓ Seed data inserted")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Jobly demo data.")
    parser.add_argument("--database-url", default=settings.database_url)
    parser.add_argument("--user-id", default="demo_user")
    args = parser.parse_args()
    seed(args.database_url, user_id=args.user_id)


if __name__ == "__main__":
    main()

