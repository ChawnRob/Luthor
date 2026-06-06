from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from datetime import date, datetime, timezone
from typing import Any

import psycopg2
from psycopg2.extras import Json, RealDictCursor


@dataclass
class UserRecord:
    id: str
    email: str
    name: str | None
    quota_tier: str
    usage_count: int
    subscription_status: str
    storage_used_mb: float
    mfa_enabled: bool

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> UserRecord:
        return cls(
            id=str(row["id"]),
            email=row["email"],
            name=row.get("name"),
            quota_tier=row.get("quota_tier", "free"),
            usage_count=int(row.get("usage_count", 0)),
            subscription_status=row.get("subscription_status", "active"),
            storage_used_mb=float(row.get("storage_used_mb", 0)),
            mfa_enabled=bool(row.get("mfa_enabled", False)),
        )


class UserStore:
    """PostgreSQL persistence for LUTHOR users and usage counters."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv(
            "LUTHOR_POSTGRES_URL",
            "postgresql://luthor:luthor@localhost:5432/luthor",
        )

    def _connect(self):
        return psycopg2.connect(self.database_url)

    def ensure_schema(self) -> None:
        migration = (
            Path(__file__).resolve().parents[3]
            / "docker"
            / "postgres"
            / "migrations"
            / "002_users_and_quotas.sql"
        )
        if not migration.exists():
            return
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(migration.read_text(encoding="utf-8"))
            conn.commit()

    def upsert_from_jwt(
        self,
        *,
        user_id: str,
        email: str,
        name: str | None = None,
    ) -> UserRecord:
        self.ensure_schema()
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (id, email, name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        email = EXCLUDED.email,
                        name = COALESCE(EXCLUDED.name, users.name),
                        updated_at = NOW()
                    RETURNING *
                    """,
                    (user_id, email, name),
                )
                row = cur.fetchone()
            conn.commit()
        return UserRecord.from_row(dict(row))

    def get_user(self, user_id: str) -> UserRecord | None:
        self.ensure_schema()
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
        return UserRecord.from_row(dict(row)) if row else None

    def get_daily_api_calls(self, user_id: str, usage_date: date | None = None) -> int:
        usage_date = usage_date or datetime.now(timezone.utc).date()
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT api_calls FROM usage_daily
                    WHERE user_id = %s AND usage_date = %s
                    """,
                    (user_id, usage_date),
                )
                row = cur.fetchone()
        return int(row[0]) if row else 0

    def get_monthly_complex_tasks(self, user_id: str, month_start: date | None = None) -> int:
        today = datetime.now(timezone.utc).date()
        month_start = month_start or today.replace(day=1)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT complex_tasks FROM usage_monthly
                    WHERE user_id = %s AND usage_month = %s
                    """,
                    (user_id, month_start),
                )
                row = cur.fetchone()
        return int(row[0]) if row else 0

    def increment_api_call(self, user_id: str, weight: int = 1) -> int:
        weight = max(int(weight), 1)
        today = datetime.now(timezone.utc).date()
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO usage_daily (user_id, usage_date, api_calls)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, usage_date) DO UPDATE SET
                        api_calls = usage_daily.api_calls + %s
                    RETURNING api_calls
                    """,
                    (user_id, today, weight, weight),
                )
                daily = int(cur.fetchone()[0])
                cur.execute(
                    """
                    UPDATE users SET usage_count = usage_count + %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (weight, user_id),
                )
            conn.commit()
        return daily

    def increment_complex_task(self, user_id: str) -> int:
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO usage_monthly (user_id, usage_month, complex_tasks)
                    VALUES (%s, %s, 1)
                    ON CONFLICT (user_id, usage_month) DO UPDATE SET
                        complex_tasks = usage_monthly.complex_tasks + 1
                    RETURNING complex_tasks
                    """,
                    (user_id, month_start),
                )
                monthly = int(cur.fetchone()[0])
            conn.commit()
        return monthly

    def set_mfa_enabled(self, user_id: str, enabled: bool) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET mfa_enabled = %s, updated_at = NOW() WHERE id = %s",
                    (enabled, user_id),
                )
            conn.commit()

    def record_tool_sync(
        self,
        connector_name: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.ensure_schema()
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tool_sync_status (connector_name, last_sync_at, status, metadata)
                    VALUES (%s, NOW(), %s, %s)
                    ON CONFLICT (connector_name) DO UPDATE SET
                        last_sync_at = NOW(),
                        status = EXCLUDED.status,
                        metadata = EXCLUDED.metadata
                    """,
                    (connector_name, status, Json(metadata or {})),
                )
            conn.commit()

    def list_tool_sync(self) -> list[dict[str, Any]]:
        self.ensure_schema()
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT connector_name, last_sync_at, status, metadata FROM tool_sync_status"
                )
                rows = cur.fetchall()
        result = []
        for row in rows:
            item = dict(row)
            ts = item.get("last_sync_at")
            if hasattr(ts, "isoformat"):
                item["last_sync_at"] = ts.isoformat()
            result.append(item)
        return result
