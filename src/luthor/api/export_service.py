from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from luthor.api.storage import InferenceLogStore

ExportFormat = Literal["csv", "xlsx"]
ExportTable = Literal["inference_logs", "active_learning_runs", "human_labels"]

ALLOWED_TABLES: frozenset[str] = frozenset(
    {"inference_logs", "active_learning_runs", "human_labels"}
)
ALLOWED_FORMATS: frozenset[str] = frozenset({"csv", "xlsx"})

MEDIA_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def get_export_token() -> str | None:
    token = os.getenv("LUTHOR_EXPORT_TOKEN")
    return token if token else None


def verify_export_token(provided: str | None, expected: str | None) -> bool:
    if not expected:
        return False
    return provided == expected


class LogExportService:
    """Build CSV/XLSX exports from PostgreSQL log tables."""

    def __init__(self, log_store: InferenceLogStore | None = None):
        self.log_store = log_store or InferenceLogStore()

    def fetch_rows(
        self,
        table: ExportTable,
        *,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> list[dict[str, Any]]:
        if table not in ALLOWED_TABLES:
            raise ValueError(f"Unsupported table: {table}")
        return self.log_store.fetch_export_rows(table, start_date=start_date, end_date=end_date)

    def build_export_file(
        self,
        table: ExportTable,
        export_format: ExportFormat,
        *,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> tuple[Path, str]:
        if export_format not in ALLOWED_FORMATS:
            raise ValueError(f"Unsupported format: {export_format}")

        rows = self.fetch_rows(table, start_date=start_date, end_date=end_date)
        dataframe = pd.DataFrame(rows)
        dataframe = self._normalize_dataframe(dataframe)

        suffix = f".{export_format}"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=f"luthor_{table}_")
        tmp_path = Path(tmp.name)
        tmp.close()

        if export_format == "csv":
            dataframe.to_csv(tmp_path, index=False)
        else:
            dataframe.to_excel(tmp_path, index=False, engine="openpyxl")

        filename = self._build_filename(table, export_format, start_date, end_date)
        return tmp_path, filename

    @staticmethod
    def _normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe.empty:
            return dataframe

        for column in dataframe.columns:
            if pd.api.types.is_datetime64_any_dtype(dataframe[column]):
                series = pd.to_datetime(dataframe[column], utc=True)
                dataframe[column] = series.dt.tz_localize(None)
                continue

            if dataframe[column].apply(lambda value: isinstance(value, (dict, list))).any():
                dataframe[column] = dataframe[column].apply(
                    lambda value: json.dumps(value) if isinstance(value, (dict, list)) else value
                )
            elif dataframe[column].apply(
                lambda value: isinstance(value, datetime) and value.tzinfo is not None
            ).any():
                dataframe[column] = dataframe[column].apply(
                    lambda value: value.replace(tzinfo=None)
                    if isinstance(value, datetime) and value.tzinfo is not None
                    else value
                )
        return dataframe

    @staticmethod
    def _build_filename(
        table: str,
        export_format: str,
        start_date: date | datetime | None,
        end_date: date | datetime | None,
    ) -> str:
        parts = [table]
        if start_date is not None:
            parts.append(f"from_{_format_date(start_date)}")
        if end_date is not None:
            parts.append(f"to_{_format_date(end_date)}")
        return f"{'_'.join(parts)}.{export_format}"


def _format_date(value: date | datetime) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    return value.isoformat()
