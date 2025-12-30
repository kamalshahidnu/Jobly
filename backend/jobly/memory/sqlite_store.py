"""SQLite storage for persistent data.

This module intentionally uses the built-in `sqlite3` driver (not SQLAlchemy) to keep
the "service layer" lightweight and easy to use from CLI / Streamlit / FastAPI.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


class SQLiteStore:
    """SQLite-based storage layer."""

    def __init__(self, db_path: str = "jobly.db"):
        """Initialize SQLite store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Connect to the database and ensure schema exists."""
        if self.conn:
            return
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.execute("PRAGMA foreign_keys = ON")
        self.init_schema()

    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor object
        """
        if not self.conn:
            self.connect()
        assert self.conn is not None  # for type checkers
        return self.conn.execute(query, params)

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

    # Backwards-compatibility: older services used `fetch()` to mean "fetch all".
    def fetch(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows (alias for `fetch_all`)."""
        return self.fetch_all(query, params)

    def commit(self) -> None:
        """Commit current transaction."""
        if self.conn:
            self.conn.commit()

    def init_schema(self) -> None:
        """Create tables if they don't exist.

        This is safe to call multiple times.
        """
        # Users table is shared by profile + auth.
        # We keep profile fields (location/skills/experience) and also support auth fields
        # (password_hash/is_active).
        self.execute(
            """
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
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._ensure_users_columns()
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
        self.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_apps_user ON applications(user_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_docs_user ON documents(user_id)")
        self.commit()

    def _ensure_users_columns(self) -> None:
        """Add missing columns to `users` table for backwards-compatible migrations."""
        # NOTE: SQLite can only ADD COLUMN; it cannot easily change constraints via ALTER.
        existing = {row["name"] for row in self.fetch_all("PRAGMA table_info(users)")}
        # Columns added after initial scaffolding.
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

    def insert(self, table: str, data: Dict[str, Any]) -> None:
        """Insert a row into `table`."""
        columns = list(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_sql = ", ".join(columns)
        values = tuple(self.dumps(data[col]) for col in columns)
        self.execute(f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})", values)
        self.commit()

    def update(
        self,
        table: str,
        row_id: str,
        updates: Dict[str, Any],
        id_column: str = "id",
    ) -> int:
        """Update a row and return affected row count."""
        if not updates:
            return 0
        columns = list(updates.keys())
        set_sql = ", ".join([f"{c} = ?" for c in columns])
        values: Tuple[Any, ...] = tuple(self.dumps(updates[c]) for c in columns) + (row_id,)
        cursor = self.execute(f"UPDATE {table} SET {set_sql} WHERE {id_column} = ?", values)
        self.commit()
        return int(cursor.rowcount or 0)

    def delete(self, table: str, row_id: str, id_column: str = "id") -> int:
        """Delete a row and return affected row count."""
        cursor = self.execute(f"DELETE FROM {table} WHERE {id_column} = ?", (row_id,))
        self.commit()
        return int(cursor.rowcount or 0)

    def ensure_timestamps(self, data: Dict[str, Any], *, created: bool) -> Dict[str, Any]:
        """Ensure common timestamp fields exist."""
        now = _utc_now_iso()
        payload = dict(data)
        if created:
            payload.setdefault("created_at", now)
        payload.setdefault("updated_at", now)
        return payload
