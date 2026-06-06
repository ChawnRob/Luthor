from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode

import httpx


class SupabaseAuthService:
    """Thin client for Supabase Auth REST API (self-host or cloud)."""

    def __init__(
        self,
        url: str,
        anon_key: str,
        *,
        app_redirect_url: str | None = None,
    ):
        self.url = url.rstrip("/")
        self.anon_key = anon_key
        self.app_redirect_url = app_redirect_url or os.getenv(
            "LUTHOR_AUTH_REDIRECT_URL",
            "http://localhost:3000/auth/callback",
        )

    def _headers(self, access_token: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {access_token or self.anon_key}",
            "Content-Type": "application/json",
        }
        return headers

    def signup(self, email: str, password: str, name: str) -> dict[str, Any]:
        payload = {
            "email": email,
            "password": password,
            "data": {"name": name},
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.url}/auth/v1/signup",
                headers=self._headers(),
                json=payload,
            )
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        return response.json()

    def signin(self, email: str, password: str) -> dict[str, Any]:
        payload = {"email": email, "password": password}
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.url}/auth/v1/token?grant_type=password",
                headers=self._headers(),
                json=payload,
            )
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        return response.json()

    def oauth_authorize_url(self, provider: str) -> str:
        params = {
            "provider": provider,
            "redirect_to": self.app_redirect_url,
        }
        return f"{self.url}/auth/v1/authorize?{urlencode(params)}"

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.url}/auth/v1/token?grant_type=refresh_token",
                headers=self._headers(),
                json={"refresh_token": refresh_token},
            )
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        return response.json()

    def mfa_enroll(self, access_token: str) -> dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.url}/auth/v1/factors",
                headers=self._headers(access_token),
                json={"factor_type": "totp", "friendly_name": "LUTHOR Authenticator"},
            )
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        return response.json()


def _extract_error(response: httpx.Response) -> str:
    try:
        body = response.json()
        if isinstance(body, dict):
            return str(body.get("msg") or body.get("error_description") or body.get("message") or body)
    except Exception:
        pass
    return response.text or f"Supabase error {response.status_code}"


_service: SupabaseAuthService | None = None


def get_supabase_auth_service() -> SupabaseAuthService | None:
    global _service
    if _service is not None:
        return _service

    url = os.getenv("SUPABASE_URL", "").strip()
    anon_key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    if not url or not anon_key:
        return None

    _service = SupabaseAuthService(url=url, anon_key=anon_key)
    return _service


def reset_supabase_auth_service() -> None:
    global _service
    _service = None
