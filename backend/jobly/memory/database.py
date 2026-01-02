"""Database abstraction layer supporting both SQLite and PostgreSQL."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


def _utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


class DatabaseStore:
    """Database storage layer with support for SQLite and PostgreSQL."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database store.

        Args:
            database_url: Database connection URL. If None, uses DATABASE_URL env var
                         or defaults to SQLite
        """
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./data/jobly.db")
        self.conn: Any = None
        self._is_postgres = self.database_url.startswith(("postgres://", "postgresql://"))

    def connect(self) -> None:
        """Connect to the database and ensure schema exists."""
        if self.conn:
            return

        if self._is_postgres:
            self._connect_postgres()
        else:
            self._connect_sqlite()

        self.init_schema()

    def _connect_sqlite(self) -> None:
        """Connect to SQLite database."""
        import sqlite3

        # Extract path from sqlite:///path/to/db.db URL
        db_path = self.database_url.replace("sqlite:///", "").replace("sqlite://", "")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.execute("PRAGMA foreign_keys = ON")

    def _connect_postgres(self) -> None:
        """Connect to PostgreSQL database."""
        import psycopg2
        import psycopg2.extras

        # psycopg2 requires postgresql:// not postgres://
        connection_url = self.database_url.replace("postgres://", "postgresql://", 1)
        self.conn = psycopg2.connect(connection_url)
        self.conn.set_session(autocommit=False)
        # Use DictCursor for dictionary-like row access
        psycopg2.extras.register_default_jsonb(self.conn)

    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, query: str, params: tuple = ()) -> Any:
        """Execute a SQL query.

        Args:
            query: SQL query string (use ? for SQLite, %s for PostgreSQL)
            params: Query parameters

        Returns:
            Cursor object
        """
        if not self.conn:
            self.connect()

        # Convert SQLite placeholders (?) to PostgreSQL placeholders (%s)
        if self._is_postgres and "?" in query:
            query = query.replace("?", "%s")

        import psycopg2.extras if self._is_postgres else None

        if self._is_postgres:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = self.conn.cursor()

        cursor.execute(query, params)
        return cursor

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Row as dictionary or None
        """
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def commit(self) -> None:
        """Commit current transaction."""
        if self.conn:
            self.conn.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        if self.conn:
            self.conn.rollback()

    def init_schema(self) -> None:
        """Create tables if they don't exist.

        This is safe to call multiple times.
        """
        # Use TEXT for PostgreSQL instead of INTEGER for booleans
        bool_type = "BOOLEAN" if self._is_postgres else "INTEGER"

        # Users table
        self.execute(
            f"""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                location TEXT,
                skills TEXT,
                experience_years INTEGER,
                resume_text TEXT,
                password_hash TEXT,
                is_active {bool_type} DEFAULT {'true' if self._is_postgres else '1'},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        if not self._is_postgres:
            self._ensure_users_columns()

        # Jobs table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                description TEXT,
                requirements TEXT,
                url TEXT,
                source TEXT,
                posted_date TEXT,
                salary_range TEXT,
                job_type TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        # Applications table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                status TEXT NOT NULL,
                applied_date TEXT NOT NULL,
                resume_version TEXT,
                cover_letter TEXT,
                notes TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
            )
            """
        )

        # Contacts table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                linkedin_url TEXT,
                company TEXT,
                position TEXT,
                notes TEXT,
                last_contacted TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        # Documents table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Indexes
        self.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_apps_user ON applications(user_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_docs_user ON documents(user_id)")

        self.commit()

    def _ensure_users_columns(self) -> None:
        """Add missing columns to users table (SQLite only)."""
        existing = {row["name"] for row in self.fetch_all("PRAGMA table_info(users)")}
        wanted = {
            "password_hash": "TEXT",
            "is_active": "INTEGER DEFAULT 1",
            "location": "TEXT",
            "skills": "TEXT",
            "experience_years": "INTEGER",
            "resume_text": "TEXT",
            "updated_at": "TEXT",
        }
        for col, ddl in wanted.items():
            if col not in existing:
                self.execute(f"ALTER TABLE users ADD COLUMN {col} {ddl}")
        self.commit()

    @staticmethod
    def dumps(value: Any) -> Optional[str]:
        """JSON-serialize lists/dicts, pass through primitives."""
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    @staticmethod
    def loads(value: Any, default: Any):
        """JSON-deserialize values that look like JSON; else return as-is."""
        if value in (None, ""):
            return default
        if isinstance(value, (dict, list)):
            return value
        if not isinstance(value, str):
            return value
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
