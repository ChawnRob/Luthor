from __future__ import annotations

import json
import os
from datetime import date, datetime, time, timezone
from typing import Any

import chromadb
import psycopg2
from psycopg2.extras import Json, RealDictCursor

EXPORT_TABLES: frozenset[str] = frozenset(
    {"inference_logs", "active_learning_runs", "human_labels"}
)


class InferenceLogStore:
    """PostgreSQL store for inference logs and active-learning metadata."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv(
            "LUTHOR_POSTGRES_URL",
            "postgresql://luthor:luthor@localhost:5432/luthor",
        )

    def _connect(self):
        return psycopg2.connect(self.database_url)

    def ping(self) -> bool:
        self.ensure_schema()
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    ALTER TABLE inference_logs
                    ADD COLUMN IF NOT EXISTS model_version VARCHAR(32) DEFAULT 'default'
                    """
                )
            conn.commit()

    def log_inference(
        self,
        endpoint: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        *,
        model_version: str = "default",
    ) -> int:
        self.ensure_schema()
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO inference_logs
                        (endpoint, request_payload, response_payload, metadata, model_version)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        endpoint,
                        Json(request_payload),
                        Json(response_payload),
                        Json(metadata or {}),
                        model_version,
                    ),
                )
                row_id = cur.fetchone()[0]
            conn.commit()
        return int(row_id)

    def fetch_ab_metrics(self, *, window_hours: int = 24) -> list[dict[str, Any]]:
        self.ensure_schema()
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        COALESCE(model_version, 'default') AS model_version,
                        COUNT(*) AS calls,
                        AVG(
                            COALESCE(
                                (metadata->>'uncertainty')::double precision,
                                (response_payload->>'uncertainty')::double precision
                            )
                        ) AS mean_uncertainty,
                        AVG((metadata->>'loss')::double precision) AS mean_loss,
                        AVG((metadata->>'success_rate')::double precision) AS success_rate
                    FROM inference_logs
                    WHERE created_at >= NOW() - (%s || ' hours')::interval
                      AND endpoint IN ('/predict', '/embed')
                    GROUP BY COALESCE(model_version, 'default')
                    """,
                    (str(window_hours),),
                )
                rows = cur.fetchall()
        return [dict(row) for row in rows]

    def log_active_learning_round(
        self,
        round_index: int,
        mean_uncertainty: float,
        mean_loss: float,
        queried: int,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO active_learning_runs
                        (round_index, mean_uncertainty, mean_loss, queried, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (round_index, mean_uncertainty, mean_loss, queried, Json(metadata or {})),
                )
                row_id = cur.fetchone()[0]
            conn.commit()
        return int(row_id)

    def recent_inference_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, endpoint, request_payload, response_payload, metadata, created_at
                    FROM inference_logs
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
        return [dict(row) for row in rows]

    def fetch_export_rows(
        self,
        table: str,
        *,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> list[dict[str, Any]]:
        if table not in EXPORT_TABLES:
            raise ValueError(f"Unsupported export table: {table}")

        query = f"SELECT * FROM {table} WHERE 1=1"
        params: list[Any] = []

        if start_date is not None:
            query += " AND created_at >= %s"
            params.append(_start_of_day(start_date))

        if end_date is not None:
            query += " AND created_at <= %s"
            params.append(_end_of_day(end_date))

        query += " ORDER BY created_at ASC"

        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        return [dict(row) for row in rows]


def _start_of_day(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _end_of_day(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.max, tzinfo=timezone.utc)


class EmbeddingStore:
    """ChromaDB store for JEPA latent embeddings."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        collection_name: str | None = None,
    ):
        self.host = host or os.getenv("LUTHOR_CHROMA_HOST", "localhost")
        self.port = int(port or os.getenv("LUTHOR_CHROMA_PORT", "8001"))
        self.collection_name = collection_name or os.getenv(
            "LUTHOR_CHROMA_COLLECTION",
            "luthor_embeddings",
        )
        self._client: chromadb.HttpClient | None = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            self._client = chromadb.HttpClient(host=self.host, port=self.port)
            self._collection = self._client.get_or_create_collection(self.collection_name)
        return self._collection

    def ping(self) -> bool:
        collection = self._get_collection()
        collection.count()
        return True

    def add_embedding(
        self,
        embedding_id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        collection = self._get_collection()
        safe_metadata = {key: json.dumps(value) if isinstance(value, (list, dict)) else value
                         for key, value in (metadata or {}).items()}
        collection.add(
            ids=[embedding_id],
            embeddings=[embedding],
            metadatas=[safe_metadata],
        )

    def get_embedding(self, embedding_id: str) -> dict[str, Any] | None:
        collection = self._get_collection()
        result = collection.get(ids=[embedding_id], include=["embeddings", "metadatas"])
        if not result["ids"]:
            return None
        return {
            "embedding_id": result["ids"][0],
            "embedding": result["embeddings"][0],
            "metadata": result["metadatas"][0] if result["metadatas"] else {},
        }
