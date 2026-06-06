from __future__ import annotations

import json
import os
from typing import Any

import chromadb
import psycopg2
from psycopg2.extras import Json, RealDictCursor


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
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True

    def log_inference(
        self,
        endpoint: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO inference_logs (endpoint, request_payload, response_payload, metadata)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (endpoint, Json(request_payload), Json(response_payload), Json(metadata or {})),
                )
                row_id = cur.fetchone()[0]
            conn.commit()
        return int(row_id)

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
