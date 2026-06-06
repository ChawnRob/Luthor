from __future__ import annotations

from fastapi import HTTPException, Request

from luthor.api.user_store import UserRecord, UserStore
from luthor.config import LuthorConfig, QuotaTierLimits

COMPLEX_PATH_PREFIXES = (
    "/mcp/orchestrate",
    "/demo/full",
    "/active_learn",
    "/tools/",
)


def is_complex_endpoint(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in COMPLEX_PATH_PREFIXES)


def tier_limits(config: LuthorConfig, tier: str) -> QuotaTierLimits:
    return config.quotas.limits_for(tier)


def endpoint_weight(config: LuthorConfig, tier: str, path: str) -> int:
    return tier_limits(config, tier).weight_for_path(path)


def check_and_increment_usage(
    request: Request,
    user: UserRecord,
    *,
    path: str = "/",
    is_complex: bool = False,
) -> dict[str, int | str]:
    config: LuthorConfig = request.app.state.config
    store: UserStore = request.app.state.user_store
    limits = tier_limits(config, user.quota_tier)

    if user.subscription_status not in ("active", "trialing"):
        raise HTTPException(status_code=403, detail="Subscription inactive")

    daily_calls = store.get_daily_api_calls(user.id)
    if daily_calls >= limits.max_api_calls_per_day:
        raise HTTPException(
            status_code=429,
            detail=f"Daily API quota exceeded ({limits.max_api_calls_per_day} calls)",
        )

    monthly_complex = store.get_monthly_complex_tasks(user.id)
    if is_complex and monthly_complex >= limits.max_complex_tasks_per_month:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly complex-task quota exceeded ({limits.max_complex_tasks_per_month})",
        )

    if user.storage_used_mb >= limits.max_storage_mb:
        raise HTTPException(
            status_code=429,
            detail=f"Storage quota exceeded ({limits.max_storage_mb} MB)",
        )

    weight = endpoint_weight(config, user.quota_tier, path)
    new_daily = store.increment_api_call(user.id, weight=weight)
    new_complex = monthly_complex
    if is_complex:
        new_complex = store.increment_complex_task(user.id)

    return {
        "tier": user.quota_tier,
        "api_calls_today": new_daily,
        "api_calls_limit": limits.max_api_calls_per_day,
        "complex_tasks_month": new_complex,
        "complex_tasks_limit": limits.max_complex_tasks_per_month,
        "storage_used_mb": int(user.storage_used_mb),
        "storage_limit_mb": limits.max_storage_mb,
        "last_request_weight": weight,
    }


def usage_snapshot(request: Request, user: UserRecord) -> dict[str, int | str]:
    config: LuthorConfig = request.app.state.config
    store: UserStore = request.app.state.user_store
    limits = tier_limits(config, user.quota_tier)
    return {
        "tier": user.quota_tier,
        "api_calls_today": store.get_daily_api_calls(user.id),
        "api_calls_limit": limits.max_api_calls_per_day,
        "complex_tasks_month": store.get_monthly_complex_tasks(user.id),
        "complex_tasks_limit": limits.max_complex_tasks_per_month,
        "storage_used_mb": int(user.storage_used_mb),
        "storage_limit_mb": limits.max_storage_mb,
        "usage_count": user.usage_count,
        "subscription_status": user.subscription_status,
    }
