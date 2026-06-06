# A/B Testing and Prompt Versioning

This guide explains how to version human-facing instructions and compare JEPA model variants in Luthor.

## Prompt versioning

Prompts live in the Git-tracked `prompts/` directory at the repository root.

| File | Purpose |
|------|---------|
| `prompts/system_v1.txt` | Baseline human oracle instructions |
| `prompts/system_v2.txt` | Updated instructions for experiments |

### Configure the active prompt

In `params.yaml`:

```yaml
prompt_version: v1
```

Or via environment variable:

```bash
export LUTHOR_PROMPT_VERSION=v2
```

### List available prompts

```bash
curl http://localhost:8080/prompts
```

Returns each file name, version label, and full text content.

### Traceability in active learning

When `active_learning.human_in_loop` is `true`, `HumanLabelOracle` loads the selected prompt and writes it to application logs on every label request. No LLM is called; this is for auditability only.

```bash
# Example log line
HumanLabelOracle using prompt_version=v1 | prompt=You are the Luthor human oracle assistant (v1). ...
```

Workflow:

1. Edit or add `prompts/system_vX.txt`
2. Commit to Git
3. Set `prompt_version: vX` in `params.yaml`
4. Restart the API or active-learning job

## A/B testing

Compare two checkpoint files through the API using the `X-Model-Version` header.

### Configuration

```yaml
ab_testing:
  enabled: true
  models:
    default: "models/jepa_model.pth"
    candidate: "models/jepa_model_v2.pth"
```

Environment overrides:

```bash
export LUTHOR_AB_TESTING_ENABLED=true
export LUTHOR_AB_MODEL_DEFAULT=models/jepa_model.pth
export LUTHOR_AB_MODEL_CANDIDATE=models/jepa_model_v2.pth
```

Checkpoint format:

```python
torch.save({"state_dict": world_model.state_dict()}, "models/jepa_model.pth")
```

If a checkpoint path is missing, Luthor falls back to a freshly initialized model.

### Routing requests

```bash
# Default model
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -H "X-Model-Version: default" \
  -d '{"observation":[1.0,2.0],"action":[0.1,0.2]}'

# Candidate model
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -H "X-Model-Version: candidate" \
  -d '{"observation":[1.0,2.0],"action":[0.1,0.2]}'
```

The same header works for `POST /embed`.

When `ab_testing.enabled` is `false`, the header is ignored and all traffic uses `default`.

### Logged metrics

Each `/predict` and `/embed` call stores `model_version` in PostgreSQL (`inference_logs.model_version`).

`/predict` also stores `uncertainty` in `metadata` for comparison.

### Read A/B results

```bash
curl http://localhost:8080/ab/metrics
```

Example response:

```json
{
  "window_hours": 24,
  "versions": {
    "default": {
      "calls": 120,
      "mean_uncertainty": 0.11,
      "mean_loss": null,
      "success_rate": null
    },
    "candidate": {
      "calls": 118,
      "mean_uncertainty": 0.08,
      "mean_loss": null,
      "success_rate": null
    }
  },
  "winner": "candidate"
}
```

Winner selection priority:

1. Higher `success_rate` in metadata (if present)
2. Lower `mean_loss` in metadata (if present)
3. Lower `mean_uncertainty` from `/predict` logs

## Typical PME workflow

1. Train two variants (e.g. with and without context compression) and save checkpoints.
2. Enable `ab_testing` in `params.yaml`.
3. Send production-like traffic split across `default` and `candidate` headers.
4. Review `/ab/metrics` each morning.
5. Version human instructions separately via `prompts/` and `prompt_version`.

## Database migration

New installations include `model_version` in `docker/postgres/init.sql`.

Existing databases apply:

```sql
ALTER TABLE inference_logs
ADD COLUMN IF NOT EXISTS model_version VARCHAR(32) DEFAULT 'default';
```

The API also runs this migration automatically on startup via `InferenceLogStore.ensure_schema()`.

## Compatibility

- `make demo`, `make active`, and `make docker-up` are unchanged.
- Unit tests force `LUTHOR_AB_TESTING_ENABLED=false` unless testing A/B explicitly.
- Prompt files are optional for non-human-in-the-loop workflows.
