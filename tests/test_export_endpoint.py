import io
import os
import sys
import unittest
from datetime import date, datetime, timezone
from unittest import mock

import pandas as pd
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class MockInferenceLogStore:
    def __init__(self):
        self.rows = [
            {
                "id": 1,
                "endpoint": "/embed",
                "request_payload": {"observation": [1.0, 2.0]},
                "response_payload": {"embedding_id": "abc"},
                "metadata": {},
                "created_at": datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
            },
            {
                "id": 2,
                "endpoint": "/predict",
                "request_payload": {"observation": [0.0, 0.0]},
                "response_payload": {"uncertainty": 0.1},
                "metadata": {},
                "created_at": datetime(2026, 3, 15, 12, 0, tzinfo=timezone.utc),
            },
            {
                "id": 3,
                "endpoint": "/active_learn",
                "request_payload": {"num_rounds": 1},
                "response_payload": {"final_mean_loss": 0.05},
                "metadata": {},
                "created_at": datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc),
            },
        ]
        self.last_query: dict | None = None

    def ping(self) -> bool:
        return True

    def log_inference(self, **kwargs) -> int:
        return 1

    def log_active_learning_round(self, **kwargs) -> int:
        return 1

    def fetch_export_rows(self, table, *, start_date=None, end_date=None):
        from luthor.api.storage import _end_of_day, _start_of_day

        self.last_query = {
            "table": table,
            "start_date": start_date,
            "end_date": end_date,
        }
        filtered = self.rows
        if start_date is not None:
            start = _start_of_day(start_date)
            filtered = [row for row in filtered if row["created_at"] >= start]
        if end_date is not None:
            end = _end_of_day(end_date)
            filtered = [row for row in filtered if row["created_at"] <= end]
        return filtered


class ExportEndpointTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_EXPORT_TOKEN"] = "test-export-token"
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"

        from luthor.config import reset_config

        reset_config()

        from luthor.api.export_service import LogExportService
        from luthor.api.main import create_app

        self.mock_store = MockInferenceLogStore()
        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.log_store = self.mock_store
        self.client.app.state.export_service = LogExportService(self.mock_store)
        self.client.app.state.export_token = "test-export-token"
        self.client.app.state.embedding_store = mock.MagicMock()
        self.client.app.state.embedding_store.ping.return_value = True

    def tearDown(self):
        self.client.__exit__(None, None, None)
        os.environ.pop("LUTHOR_EXPORT_TOKEN", None)
        from luthor.config import reset_config

        reset_config()

    def test_export_requires_token(self):
        response = self.client.get("/export/logs")
        self.assertEqual(response.status_code, 401)

    def test_export_csv_returns_non_empty_file(self):
        response = self.client.get(
            "/export/logs",
            headers={"X-Export-Token": "test-export-token"},
            params={"table": "inference_logs", "format": "csv"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.headers["content-type"])
        self.assertIn("attachment", response.headers["content-disposition"])
        self.assertGreater(len(response.content), 0)

        dataframe = pd.read_csv(io.BytesIO(response.content))
        self.assertEqual(len(dataframe), 3)
        self.assertIn("endpoint", dataframe.columns)

    def test_export_xlsx_returns_non_empty_file(self):
        response = self.client.get(
            "/export/logs",
            headers={"X-Export-Token": "test-export-token"},
            params={"table": "inference_logs", "format": "xlsx"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheetml", response.headers["content-type"])
        self.assertGreater(len(response.content), 0)

        dataframe = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
        self.assertEqual(len(dataframe), 3)

    def test_export_date_filters(self):
        response = self.client.get(
            "/export/logs",
            headers={"X-Export-Token": "test-export-token"},
            params={
                "table": "inference_logs",
                "format": "csv",
                "start_date": "2026-03-10",
                "end_date": "2026-03-31",
            },
        )
        self.assertEqual(response.status_code, 200)

        dataframe = pd.read_csv(io.BytesIO(response.content))
        self.assertEqual(len(dataframe), 1)
        self.assertEqual(dataframe.iloc[0]["endpoint"], "/predict")
        self.assertIsNotNone(self.mock_store.last_query)
        self.assertEqual(self.mock_store.last_query["table"], "inference_logs")
        self.assertEqual(self.mock_store.last_query["start_date"], date(2026, 3, 10))

    def test_export_rejects_invalid_table(self):
        response = self.client.get(
            "/export/logs",
            headers={"X-Export-Token": "test-export-token"},
            params={"table": "users", "format": "csv"},
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
