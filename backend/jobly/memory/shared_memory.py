"""Shared memory for inter-agent communication."""

from typing import Dict, Any, Optional
from datetime import datetime
import threading


class SharedMemory:
    """Thread-safe shared memory for agents."""

    def __init__(self):
        """Initialize shared memory."""
        self._data: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._access_log: Dict[str, datetime] = {}

    def set(self, key: str, value: Any, agent_name: Optional[str] = None) -> None:
        """Set a value in shared memory.

        Args:
            key: Memory key
            value: Value to store
            agent_name: Name of agent setting the value
        """
        with self._lock:
            self._data[key] = value
            self._access_log[key] = datetime.utcnow()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from shared memory.

        Args:
            key: Memory key
            default: Default value if key not found

        Returns:
            Stored value or default
        """
        with self._lock:
            return self._data.get(key, default)

    def delete(self, key: str) -> bool:
        """Delete a key from shared memory.

        Args:
            key: Memory key

        Returns:
            Success status
        """
        with self._lock:
            if key in self._data:
                del self._data[key]
                del self._access_log[key]
                return True
            return False

    def keys(self) -> list:
        """Get all keys in shared memory.

        Returns:
            List of keys
        """
        with self._lock:
            return list(self._data.keys())

    def clear(self) -> None:
        """Clear all data from shared memory."""
        with self._lock:
            self._data.clear()
            self._access_log.clear()

    def snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current memory state.

        Returns:
            Copy of current memory data
        """
        with self._lock:
            return self._data.copy()
