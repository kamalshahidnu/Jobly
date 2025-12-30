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
        """Ensure auth-related user columns exist on the shared `users` table."""
        # `SQLiteStore.connect()` creates the base schema (including `users`) and runs migrations.
        self.store.connect()

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

        self.store.connect()
        self.store.execute(
            """
            INSERT INTO users (id, email, name, phone, password_hash, created_at, updated_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, user_data.email, user_data.name, user_data.phone, password_hash, created_at, created_at, 1)
        )
        if self.store.conn:
            self.store.conn.commit()

        return User(
            user_id=user_id,
            email=user_data.email,
            name=user_data.name,
            phone=user_data.phone,
            created_at=datetime.fromisoformat(created_at),
            is_active=True
        )

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User data if found
        """
        return self.store.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found
        """
        user_data = self.store.fetch_one(
            "SELECT id, email, name, phone, created_at, is_active FROM users WHERE id = ?",
            (user_id,)
        )

        if not user_data:
            return None
        return User(
            user_id=user_data["id"],
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

        if not user_data.get("password_hash"):
            return None
        if not verify_password(password, user_data["password_hash"]):
            return None

        return User(
            user_id=user_data["id"],
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

        self.store.connect()
        self.store.execute(
            f"UPDATE users SET {set_clause} WHERE id = ?",
            tuple(values)
        )
        if self.store.conn:
            self.store.conn.commit()

        return self.get_user_by_id(user_id)

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account.

        Args:
            user_id: User ID

        Returns:
            Success status
        """
        self.store.connect()
        cursor = self.store.execute(
            "UPDATE users SET is_active = 0 WHERE id = ?",
            (user_id,)
        )
        if self.store.conn:
            self.store.conn.commit()
        return cursor.rowcount > 0

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Success status
        """
        user_data = self.store.fetch_one(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,)
        )

        if not user_data:
            return False

        if not verify_password(old_password, user_data["password_hash"]):
            return False

        new_hash = hash_password(new_password)

        self.store.connect()
        self.store.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_hash, user_id)
        )
        if self.store.conn:
            self.store.conn.commit()
        return True
