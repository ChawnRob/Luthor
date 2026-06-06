from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from luthor.api.quota_service import usage_snapshot
from luthor.api.schemas import (
    AuthMfaEnableRequest,
    AuthMfaEnableResponse,
    AuthOAuthResponse,
    AuthRefreshRequest,
    AuthSigninRequest,
    AuthSignupRequest,
    AuthTokenResponse,
    UserProfileResponse,
)
from luthor.api.user_store import UserRecord, UserStore
from luthor.auth.supabase_service import get_supabase_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(payload: dict, user_store: UserStore) -> AuthTokenResponse:
    access = payload.get("access_token", "")
    user = payload.get("user") or {}
    user_id = user.get("id")
    email = user.get("email", "")
    metadata = user.get("user_metadata") or {}
    name = metadata.get("name") if isinstance(metadata, dict) else None

    if user_id and email:
        user_store.upsert_from_jwt(user_id=str(user_id), email=email, name=name)

    return AuthTokenResponse(
        access_token=access,
        refresh_token=payload.get("refresh_token"),
        expires_in=payload.get("expires_in"),
        user_id=str(user_id) if user_id else None,
    )


@router.post("/signup", response_model=AuthTokenResponse)
def signup(payload: AuthSignupRequest, request: Request) -> AuthTokenResponse:
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")

    store: UserStore = request.app.state.user_store
    try:
        result = service.signup(payload.email, payload.password, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _token_response(result, store)


@router.post("/signin", response_model=AuthTokenResponse)
def signin(payload: AuthSigninRequest, request: Request) -> AuthTokenResponse:
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")

    store: UserStore = request.app.state.user_store
    try:
        result = service.signin(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return _token_response(result, store)


@router.get("/oauth/google", response_model=None)
def oauth_google():
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")
    return RedirectResponse(service.oauth_authorize_url("google"))


@router.get("/oauth/apple", response_model=None)
def oauth_apple():
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")
    return RedirectResponse(service.oauth_authorize_url("apple"))


@router.get("/oauth/google/url", response_model=AuthOAuthResponse)
def oauth_google_url():
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")
    return AuthOAuthResponse(provider="google", authorization_url=service.oauth_authorize_url("google"))


@router.get("/oauth/apple/url", response_model=AuthOAuthResponse)
def oauth_apple_url():
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")
    return AuthOAuthResponse(provider="apple", authorization_url=service.oauth_authorize_url("apple"))


@router.post("/refresh", response_model=AuthTokenResponse)
def refresh_session(payload: AuthRefreshRequest, request: Request) -> AuthTokenResponse:
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")

    store: UserStore = request.app.state.user_store
    try:
        result = service.refresh_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return _token_response(result, store)


@router.post("/mfa/enable", response_model=AuthMfaEnableResponse)
def mfa_enable(payload: AuthMfaEnableRequest, request: Request) -> AuthMfaEnableResponse:
    service = get_supabase_auth_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")

    store: UserStore = request.app.state.user_store
    try:
        result = service.mfa_enroll(payload.access_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    totp = result.get("totp") or {}
    factor_id = result.get("id")
    if factor_id and hasattr(request.state, "user"):
        store.set_mfa_enabled(request.state.user.id, True)

    return AuthMfaEnableResponse(
        factor_id=str(factor_id) if factor_id else None,
        totp_uri=totp.get("uri"),
        qr_code=totp.get("qr_code"),
        secret=totp.get("secret"),
    )


@router.get("/me", response_model=UserProfileResponse)
def auth_me(request: Request) -> UserProfileResponse:
    user: UserRecord | None = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    usage = usage_snapshot(request, user)
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        quota_tier=user.quota_tier,
        subscription_status=user.subscription_status,
        mfa_enabled=user.mfa_enabled,
        usage=usage,
    )
