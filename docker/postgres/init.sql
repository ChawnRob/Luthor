CREATE TABLE IF NOT EXISTS inference_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(64) NOT NULL,
    request_payload JSONB NOT NULL,
    response_payload JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS active_learning_runs (
    id SERIAL PRIMARY KEY,
    round_index INTEGER NOT NULL,
    mean_uncertainty DOUBLE PRECISION NOT NULL,
    mean_loss DOUBLE PRECISION NOT NULL,
    queried INTEGER NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inference_logs_endpoint ON inference_logs (endpoint);
CREATE INDEX IF NOT EXISTS idx_inference_logs_created_at ON inference_logs (created_at DESC);

CREATE TABLE IF NOT EXISTS human_labels (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(128) NOT NULL UNIQUE,
    correct_outcome JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_human_labels_sample_id ON human_labels (sample_id);
CREATE INDEX IF NOT EXISTS idx_human_labels_created_at ON human_labels (created_at DESC);
