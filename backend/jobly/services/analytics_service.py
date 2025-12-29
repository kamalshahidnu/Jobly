"""Analytics service for insights and statistics."""

from datetime import datetime, timedelta
from statistics import median
from typing import Any, Dict, List

from ..memory.sqlite_store import SQLiteStore


class AnalyticsService:
    """Service layer for analytics operations."""

    def __init__(self, store: SQLiteStore):
        """Initialize analytics service.

        Args:
            store: Database store instance
        """
        self.store = store

    def get_application_stats(self, user_id: str) -> Dict[str, Any]:
        """Get application statistics.

        Args:
            user_id: User ID

        Returns:
            Application statistics
        """
        rows = self.store.fetch_all(
            "SELECT status, COUNT(*) as cnt FROM applications WHERE user_id = ? GROUP BY status",
            (user_id,),
        )
        by_status = {str(r["status"]).lower(): int(r["cnt"]) for r in rows}
        total = sum(by_status.values())
        return {
            "total_applications": total,
            "pending": by_status.get("pending", 0),
            "interviewing": by_status.get("interviewing", 0),
            "rejected": by_status.get("rejected", 0),
            "offers": by_status.get("offer", 0) + by_status.get("offers", 0),
        }

    def get_response_rate(self, user_id: str, days: int = 30) -> float:
        """Calculate response rate over time period.

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            Response rate as percentage
        """
        since = (datetime.utcnow() - timedelta(days=days)).isoformat(timespec="seconds")
        total = self.store.fetch_one(
            "SELECT COUNT(*) as cnt FROM applications WHERE user_id = ? AND applied_date >= ?",
            (user_id, since),
        ) or {"cnt": 0}
        responded = self.store.fetch_one(
            """
            SELECT COUNT(*) as cnt
            FROM applications
            WHERE user_id = ?
              AND applied_date >= ?
              AND LOWER(status) IN ('interviewing', 'offer', 'offers', 'rejected')
            """,
            (user_id, since),
        ) or {"cnt": 0}

        denom = int(total["cnt"]) or 0
        if denom == 0:
            return 0.0
        return round((int(responded["cnt"]) / denom) * 100.0, 2)

    def get_time_to_response(self, user_id: str) -> Dict[str, float]:
        """Calculate average time to response.

        Args:
            user_id: User ID

        Returns:
            Average response time statistics
        """
        # In this simplified schema we don't track first-response timestamp; use updated_at - applied_date.
        rows = self.store.fetch_all(
            """
            SELECT applied_date, updated_at
            FROM applications
            WHERE user_id = ?
              AND LOWER(status) IN ('interviewing', 'offer', 'offers', 'rejected')
            """,
            (user_id,),
        )
        deltas: List[float] = []
        for row in rows:
            try:
                applied = datetime.fromisoformat(row["applied_date"])
                updated = datetime.fromisoformat(row["updated_at"])
                deltas.append(max(0.0, (updated - applied).total_seconds() / 86400.0))
            except Exception:
                continue

        if not deltas:
            return {"average_days": 0.0, "median_days": 0.0, "min_days": 0.0, "max_days": 0.0}
        return {
            "average_days": round(sum(deltas) / len(deltas), 2),
            "median_days": round(float(median(deltas)), 2),
            "min_days": round(min(deltas), 2),
            "max_days": round(max(deltas), 2),
        }

    def get_job_pipeline(self, user_id: str) -> Dict[str, int]:
        """Get job pipeline by stage.

        Args:
            user_id: User ID

        Returns:
            Count of jobs by stage
        """
        rows = self.store.fetch_all(
            "SELECT status, COUNT(*) as cnt FROM applications WHERE user_id = ? GROUP BY status",
            (user_id,),
        )
        return {str(r["status"]).lower(): int(r["cnt"]) for r in rows}

    def get_trends(self, user_id: str, metric: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get trend data for metric over time.

        Args:
            user_id: User ID
            metric: Metric to track
            days: Number of days of history

        Returns:
            List of data points over time
        """
        metric = (metric or "").lower().strip()
        since_dt = datetime.utcnow() - timedelta(days=days)
        points: List[Dict[str, Any]] = []

        if metric in ("applications", "applications_per_day"):
            rows = self.store.fetch_all(
                """
                SELECT substr(applied_date, 1, 10) as day, COUNT(*) as cnt
                FROM applications
                WHERE user_id = ? AND applied_date >= ?
                GROUP BY day
                ORDER BY day ASC
                """,
                (user_id, since_dt.isoformat(timespec="seconds")),
            )
            points = [{"date": r["day"], "value": int(r["cnt"])} for r in rows]
        elif metric in ("responses", "responses_per_day"):
            rows = self.store.fetch_all(
                """
                SELECT substr(updated_at, 1, 10) as day, COUNT(*) as cnt
                FROM applications
                WHERE user_id = ?
                  AND updated_at >= ?
                  AND LOWER(status) IN ('interviewing', 'offer', 'offers', 'rejected')
                GROUP BY day
                ORDER BY day ASC
                """,
                (user_id, since_dt.isoformat(timespec="seconds")),
            )
            points = [{"date": r["day"], "value": int(r["cnt"])} for r in rows]
        return points

    def get_success_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate success metrics.

        Args:
            user_id: User ID

        Returns:
            Success metrics
        """
        stats = self.get_application_stats(user_id)
        total = stats["total_applications"] or 0
        if total == 0:
            return {"interview_rate": 0.0, "offer_rate": 0.0, "acceptance_rate": 0.0}

        interviewing = stats.get("interviewing", 0)
        offers = stats.get("offers", 0)

        accepted = self.store.fetch_one(
            """
            SELECT COUNT(*) as cnt FROM applications
            WHERE user_id = ? AND LOWER(status) IN ('accepted', 'accept')
            """,
            (user_id,),
        ) or {"cnt": 0}

        interview_rate = (interviewing / total) * 100.0
        offer_rate = (offers / total) * 100.0
        acceptance_rate = (int(accepted["cnt"]) / max(offers, 1)) * 100.0 if offers else 0.0

        return {
            "interview_rate": round(interview_rate, 2),
            "offer_rate": round(offer_rate, 2),
            "acceptance_rate": round(acceptance_rate, 2),
        }
