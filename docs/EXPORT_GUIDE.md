# Luthor Log Export Guide

This guide explains how to export Luthor PostgreSQL logs to CSV/Excel and optionally publish them to Google Sheets.

## Prerequisites

- Luthor API running with PostgreSQL (`make docker-up` or `make run-api`)
- Dependencies installed: `make install`
- Export libraries: `pandas`, `openpyxl`

## 1. Configure the export token

Set a secret token in the API environment:

```bash
export LUTHOR_EXPORT_TOKEN="change-me-to-a-long-random-string"
```

When using Docker Compose, add the same variable to the API service environment.

Every export request must include:

```http
X-Export-Token: change-me-to-a-long-random-string
```

Without a valid token, `GET /export/logs` returns `401 Unauthorized`.

## 2. Call the export endpoint

```bash
curl -H "X-Export-Token: $LUTHOR_EXPORT_TOKEN" \
  "http://localhost:8080/export/logs?table=inference_logs&format=csv" \
  -o inference_logs.csv
```

### Query parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `table` | `inference_logs` | `inference_logs`, `active_learning_runs`, or `human_labels` |
| `format` | `csv` | `csv` or `xlsx` |
| `start_date` | none | ISO date (`YYYY-MM-DD`), inclusive |
| `end_date` | none | ISO date (`YYYY-MM-DD`), inclusive |

### Examples

Excel export for active learning runs in March 2026:

```bash
curl -H "X-Export-Token: $LUTHOR_EXPORT_TOKEN" \
  "http://localhost:8080/export/logs?table=active_learning_runs&format=xlsx&start_date=2026-03-01&end_date=2026-03-31" \
  -o active_learning_runs.xlsx
```

Human labels for the last week:

```bash
curl -H "X-Export-Token: $LUTHOR_EXPORT_TOKEN" \
  "http://localhost:8080/export/logs?table=human_labels&format=csv&start_date=2026-03-25&end_date=2026-04-01" \
  -o human_labels.csv
```

The response is streamed as a file download with `Content-Disposition: attachment`.

## 3. Automated export to Google Sheets (optional)

The script `scripts/export_to_sheets.py` calls the API and uploads CSV data to Google Sheets using a service account.

### Google Cloud setup

1. Create a Google Cloud project and enable the Google Sheets API.
2. Create a service account and download its JSON key.
3. Share the target spreadsheet with the service account email.

### Environment variables

```bash
export LUTHOR_EXPORT_TOKEN="your-export-token"
export LUTHOR_API_URL="http://localhost:8080"
export GOOGLE_SERVICE_ACCOUNT_JSON="/path/to/service-account.json"
export LUTHOR_SHEETS_NAME="Luthor Logs"
export LUTHOR_SHEETS_WORKSHEET="inference_logs"
```

### Run manually

```bash
python3 scripts/export_to_sheets.py --table inference_logs --yesterday
```

### Schedule with cron (daily at 07:00)

```cron
0 7 * * * cd /path/to/Luthor && \
  LUTHOR_EXPORT_TOKEN=secret \
  GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/key.json \
  python3 scripts/export_to_sheets.py --table inference_logs --yesterday >> /var/log/luthor-export.log 2>&1
```

## 4. Security notes

- Keep `LUTHOR_EXPORT_TOKEN` secret and rotate it periodically.
- Do not expose the export endpoint publicly without TLS and network restrictions.
- JSON columns are serialized as strings in CSV/Excel for readability.

## 5. Troubleshooting

| Issue | Fix |
|-------|-----|
| `401 Invalid or missing export token` | Set `LUTHOR_EXPORT_TOKEN` and pass `X-Export-Token` |
| `503 Export failed` | Check PostgreSQL connectivity (`/health`) |
| Empty file | Widen the date range or verify data exists in the selected table |
| `human_labels` table missing | Apply the latest `docker/postgres/init.sql` migration |
