ALTER TABLE inference_logs
ADD COLUMN IF NOT EXISTS model_version VARCHAR(32) DEFAULT 'default';

UPDATE inference_logs
SET model_version = 'default'
WHERE model_version IS NULL;
