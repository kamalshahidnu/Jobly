"""Rate limiter for API calls and web requests."""

import time
from typing import Callable, Any
from functools import wraps


class RateLimiter:
    """Rate limiter for controlling API request rates."""

    def __init__(self, max_calls: int, time_window: float):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def __call__(self, func: Callable) -> Callable:
        """Decorator to rate limit function calls.

        Args:
            func: Function to rate limit

        Returns:
            Wrapped function
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            self.calls = [call for call in self.calls if call > now - self.time_window]

            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self.calls.append(time.time())
            return func(*args, **kwargs)

        return wrapper

    def reset(self) -> None:
        """Reset the rate limiter."""
        self.calls = []
