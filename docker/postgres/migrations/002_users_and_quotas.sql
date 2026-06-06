CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    quota_tier VARCHAR(32) NOT NULL DEFAULT 'free',
    usage_count INTEGER NOT NULL DEFAULT 0,
    subscription_status VARCHAR(32) NOT NULL DEFAULT 'active',
    storage_used_mb DOUBLE PRECISION NOT NULL DEFAULT 0,
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS usage_daily (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    api_calls INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, usage_date)
);

CREATE TABLE IF NOT EXISTS usage_monthly (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    usage_month DATE NOT NULL,
    complex_tasks INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, usage_month)
);

CREATE TABLE IF NOT EXISTS tool_sync_status (
    connector_name VARCHAR(64) PRIMARY KEY,
    last_sync_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'unknown',
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS human_labels (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(128) NOT NULL,
    correct_outcome JSONB NOT NULL,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE inference_logs
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

CREATE INDEX IF NOT EXISTS idx_usage_daily_user_date ON usage_daily (user_id, usage_date);
CREATE INDEX IF NOT EXISTS idx_inference_logs_user_id ON inference_logs (user_id);
