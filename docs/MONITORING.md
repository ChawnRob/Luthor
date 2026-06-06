# Monitoring LUTHOR (Prometheus + Grafana)

LUTHOR exposes Prometheus metrics on the FastAPI API so you can observe latency, success rates, model versions, and active-learning activity in production.

## Quick start (Docker Compose)

```bash
make docker-up
```

| Service    | URL                         | Credentials      |
|-----------|-----------------------------|------------------|
| API       | http://localhost:8080       | —                |
| Metrics   | http://localhost:8080/metrics | —              |
| Prometheus| http://localhost:9090       | —                |
| Grafana   | http://localhost:3000       | `admin` / `luthor` |

Grafana loads automatically:

- **Datasource**: Prometheus (`http://prometheus:9090`)
- **Dashboard**: *LUTHOR — Observabilité PME* (folder **LUTHOR**)

Panels include HTTP throughput, success rate, HTTP/JEPA latency, A/B model-version traffic, and active-learning rounds.

## Exposed metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | `method`, `endpoint`, `status` | All HTTP requests (except `/metrics`) |
| `http_request_duration_seconds` | Histogram | `method`, `endpoint` | End-to-end HTTP latency |
| `jepa_inference_latency` | Histogram | `endpoint` | Embed/predict model inference time |
| `active_learning_rounds_total` | Counter | — | Completed active-learning rounds |
| `model_version_requests_total` | Counter | `endpoint`, `model_version` | Traffic per model version (A/B) |

Example:

```bash
curl -s http://localhost:8080/metrics | grep http_requests_total
```

## Google Cloud Run

Cloud Run instances are short-lived; scraping `/metrics` directly is unreliable. Use the optional Pushgateway:

```bash
export GCP_PROJECT_ID=my-project
export LUTHOR_PROMETHEUS_PUSH_GATEWAY=https://pushgateway.example.com:9091

./scripts/deploy_cloud_run.sh
```

The deploy script wraps `cloudbuild.yaml` (build image → push → `gcloud run deploy`). When `LUTHOR_PROMETHEUS_PUSH_GATEWAY` is set, metrics are pushed every 15 seconds and once on shutdown.

Configure Prometheus to scrape the Pushgateway job `luthor-api`.

### Manual deploy variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `GCP_PROJECT_ID` | — | Required GCP project |
| `GCP_REGION` | `europe-west1` | Cloud Run region |
| `CLOUD_RUN_SERVICE` | `luthor` | Service name |
| `IMAGE_TAG` | git short SHA | Image tag |
| `LUTHOR_PROMETHEUS_PUSH_GATEWAY` | — | Optional Pushgateway URL |

## Reading metrics in Grafana

1. Open **Dashboards → LUTHOR → LUTHOR — Observabilité PME**.
2. Use the last 6 hours by default; change the time range in the top-right corner.
3. Key panels for a PME operator:
   - **Taux de succès HTTP**: should stay near 100%.
   - **Latence inférence JEPA (p95)**: watch `/embed` and `/predict` separately.
   - **Requêtes par version de modèle**: compare `default` vs `candidate` during A/B tests.
   - **Tours d'apprentissage actif**: spikes after `/active_learn` calls.

## Alerting examples (Prometheus)

Add rules to `docker/prometheus/prometheus.yml` or a dedicated rules file:

```yaml
groups:
  - name: luthor
    rules:
      - alert: LuthorHighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / clamp_min(sum(rate(http_requests_total[5m])), 0.001) > 0.05
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "LUTHOR HTTP 5xx rate above 5%"

      - alert: LuthorHighJEPALatency
        expr: |
          histogram_quantile(
            0.95,
            sum(rate(jepa_inference_latency_bucket[5m])) by (le, endpoint)
          ) > 1
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "JEPA p95 latency above 1s on {{ $labels.endpoint }}"
```

Wire Alertmanager (not included in the default Compose stack) or Grafana alert rules to notify Slack, email, or PagerDuty.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Empty Grafana panels | Prometheus targets: http://localhost:9090/targets — `luthor-api` should be **UP** |
| No metrics on Cloud Run | Set `LUTHOR_PROMETHEUS_PUSH_GATEWAY` and verify Pushgateway receives `luthor-api` jobs |
| `/metrics` 404 | Ensure you run the API image built from this repository (`luthor.api.main:app`) |

## Tests

```bash
python -m unittest tests.test_prometheus_metrics -v
```

Tests verify `/metrics` format and that counters increment after API calls.
