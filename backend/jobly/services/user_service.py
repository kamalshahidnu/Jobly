"""User service for managing user accounts."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from ..memory.sqlite_store import SQLiteStore
from ..auth.password import hash_password, verify_password
from ..auth.models import UserCreate, User


class UserService:
    """Service for managing users."""

    def __init__(self, db_path: str = "jobly.db"):
        """Initialize user service.

        Args:
            db_path: Path to SQLite database
        """
        self.store = SQLiteStore(db_path)
        self._ensure_users_table()

    def _ensure_users_table(self) -> None:
        """Ensure users table exists."""
        conn = self.store.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    phone TEXT,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user

        Raises:
            ValueError: If email already exists
        """
        # Check if email exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")

        user_id = str(uuid.uuid4())
        password_hash = hash_password(user_data.password)
        created_at = datetime.utcnow().isoformat()

        conn = self.store.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (user_id, email, name, phone, password_hash, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, user_data.email, user_data.name, user_data.phone, password_hash, created_at, 1)
            )
            conn.commit()

            return User(
                user_id=user_id,
                email=user_data.email,
                name=user_data.name,
                phone=user_data.phone,
                created_at=datetime.fromisoformat(created_at),
                is_active=True
            )
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User data if found
        """
        result = self.store.fetch(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        return result[0] if result else None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found
        """
        result = self.store.fetch(
            "SELECT user_id, email, name, phone, created_at, is_active FROM users WHERE user_id = ?",
            (user_id,)
        )

        if not result:
            return None

        user_data = result[0]
        return User(
            user_id=user_data["user_id"],
            email=user_data["email"],
            name=user_data["name"],
            phone=user_data.get("phone"),
            created_at=datetime.fromisoformat(user_data["created_at"]),
            is_active=bool(user_data["is_active"])
        )

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user.

        Args:
            email: User email
            password: User password

        Returns:
            User if authentication successful
        """
        user_data = self.get_user_by_email(email)

        if not user_data:
            return None

        if not verify_password(password, user_data["password_hash"]):
            return None

        return User(
            user_id=user_data["user_id"],
            email=user_data["email"],
            name=user_data["name"],
            phone=user_data.get("phone"),
            created_at=datetime.fromisoformat(user_data["created_at"]),
            is_active=bool(user_data["is_active"])
        )

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user information.

        Args:
            user_id: User ID
            updates: Fields to update

        Returns:
            Updated user
        """
        # Only allow updating certain fields
        allowed_fields = ["name", "phone"]
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

        if not update_fields:
            return self.get_user_by_id(user_id)

        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [user_id]

        conn = self.store.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE users SET {set_clause} WHERE user_id = ?",
                values
            )
            conn.commit()
        finally:
            conn.close()

        return self.get_user_by_id(user_id)

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account.

        Args:
            user_id: User ID

        Returns:
            Success status
        """
        conn = self.store.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET is_active = 0 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Success status
        """
        user_data = self.store.fetch(
            "SELECT password_hash FROM users WHERE user_id = ?",
            (user_id,)
        )

        if not user_data:
            return False

        if not verify_password(old_password, user_data[0]["password_hash"]):
            return False

        new_hash = hash_password(new_password)

        conn = self.store.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE user_id = ?",
                (new_hash, user_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()
