"""Error handler agent for managing errors and retries."""

from typing import Any, Dict
from .base import BaseAgent


class ErrorHandlerAgent(BaseAgent):
    """Agent responsible for handling errors and implementing retry logic."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="ErrorHandlerAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors and implement retry strategies.

        Args:
            input_data: Error information and context

        Returns:
            Recovery strategy and status
        """
        error_info = input_data.get("error") or input_data.get("exception") or input_data
        max_retries = int(self.config.get("max_retries", 3))
        backoff_factor = float(self.config.get("backoff_factor", 2.0))
        base_delay = float(self.config.get("base_delay_seconds", 1.0))
        retry_count = int(input_data.get("retry_count") or 0)

        message = ""
        code = ""
        if isinstance(error_info, dict):
            message = str(error_info.get("message") or error_info.get("detail") or "")
            code = str(error_info.get("code") or error_info.get("type") or "").lower()
        elif error_info:
            message = str(error_info)

        is_transient = False
        if message:
            lowered = message.lower()
            is_transient = any(
                keyword in lowered
                for keyword in ("timeout", "temporar", "rate limit", "connection", "quota")
            )
        if code in {"timeout", "retry", "throttled", "rate_limit"}:
            is_transient = True

        should_retry = is_transient and retry_count < max_retries
        next_retry = retry_count + 1 if should_retry else retry_count
        delay_seconds = base_delay * (backoff_factor ** retry_count) if should_retry else 0.0

        errors = self.state.setdefault("errors", [])
        error_record = {
            "message": message,
            "code": code,
            "retry_count": retry_count,
            "transient": is_transient
        }
        errors.append(error_record)
        self.state["errors"] = errors[-20:]
        self.state["last_error"] = error_record

        if should_retry:
            return {
                "status": "retry",
                "recovery": {
                    "action": "retry",
                    "retry_count": next_retry,
                    "delay_seconds": delay_seconds,
                    "transient": True
                }
            }

        return {
            "status": "failed" if error_info else "success",
            "recovery": {
                "action": "halt" if error_info else "noop",
                "retry_count": retry_count,
                "transient": is_transient
            }
        }
