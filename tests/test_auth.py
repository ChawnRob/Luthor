import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

TEST_SECRET = "test-jwt-secret-for-luthor-auth-suite"
TEST_USER_ID = "11111111-1111-1111-1111-111111111111"


class MockUserStore:
    def ensure_schema(self) -> None:
        return None

    def upsert_from_jwt(self, *, user_id: str, email: str, name: str | None = None):
        from luthor.api.user_store import UserRecord

        return UserRecord(
            id=user_id,
            email=email,
            name=name,
            quota_tier="free",
            usage_count=0,
            subscription_status="active",
            storage_used_mb=0.0,
            mfa_enabled=False,
        )

    def get_daily_api_calls(self, user_id: str, usage_date=None) -> int:
        return 0

    def get_monthly_complex_tasks(self, user_id: str, month_start=None) -> int:
        return 0

    def increment_api_call(self, user_id: str) -> int:
        return 1

    def increment_complex_task(self, user_id: str) -> int:
        return 1

    def set_mfa_enabled(self, user_id: str, enabled: bool) -> None:
        return None

    def list_tool_sync(self):
        return []

    def record_tool_sync(self, *args, **kwargs) -> None:
        return None


def _make_token(email: str = "user@example.com") -> str:
    payload = {
        "sub": TEST_USER_ID,
        "email": email,
        "aud": "authenticated",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "user_metadata": {"name": "Test User"},
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


class AuthTests(unittest.TestCase):
    def setUp(self):
        os.environ["LUTHOR_ENCODER_LATENT_DIM"] = "4"
        os.environ["LUTHOR_ENCODER_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_ENCODER_NUM_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_HIDDEN_DIM"] = "16"
        os.environ["LUTHOR_PREDICTOR_LAYERS"] = "2"
        os.environ["LUTHOR_PREDICTOR_USE_ATTENTION"] = "true"
        os.environ["LUTHOR_PLANNER_LR"] = "0.01"
        os.environ["LUTHOR_AL_ROUNDS"] = "1"
        os.environ["LUTHOR_AL_POOL_SIZE"] = "4"
        os.environ["LUTHOR_AL_QUERY_BATCH"] = "2"
        os.environ["LUTHOR_AL_MC_SAMPLES"] = "2"
        os.environ["LUTHOR_AL_TRAIN_STEPS"] = "1"
        os.environ["LUTHOR_AB_TESTING_ENABLED"] = "false"
        os.environ["LUTHOR_AUTH_REQUIRED"] = "true"
        os.environ["SUPABASE_JWT_SECRET"] = TEST_SECRET

        from luthor.config import reset_config

        reset_config()

        from luthor.api.main import create_app

        self.app = create_app()
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.client.app.state.user_store = MockUserStore()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        os.environ.pop("LUTHOR_AUTH_REQUIRED", None)
        os.environ.pop("SUPABASE_JWT_SECRET", None)
        from luthor.config import reset_config

        reset_config()

    def test_health_without_token(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_config_requires_token(self):
        response = self.client.get("/config")
        self.assertEqual(response.status_code, 401)

    def test_config_with_valid_token(self):
        token = _make_token()
        response = self.client.get("/config", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)

    def test_oauth_google_url_without_supabase(self):
        response = self.client.get("/auth/oauth/google/url")
        self.assertEqual(response.status_code, 503)

    @patch("luthor.api.routes.auth.get_supabase_auth_service")
    def test_signin_returns_token(self, mock_service):
        mock_service.return_value = MagicMock()
        mock_service.return_value.signin.return_value = {
            "access_token": "abc",
            "refresh_token": "def",
            "expires_in": 3600,
            "user": {"id": TEST_USER_ID, "email": "user@example.com", "user_metadata": {"name": "A"}},
        }
        response = self.client.post(
            "/auth/signin",
            json={"email": "user@example.com", "password": "password123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access_token"], "abc")


if __name__ == "__main__":
    unittest.main()
