#!/usr/bin/env bash
# Build and deploy the LUTHOR FastAPI service to Google Cloud Run.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PROJECT_ID="${GCP_PROJECT_ID:-${GOOGLE_CLOUD_PROJECT:-}}"
REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-luthor}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)}"
MEMORY="${CLOUD_RUN_MEMORY:-1Gi}"
CPU="${CLOUD_RUN_CPU:-1}"
TIMEOUT="${CLOUD_RUN_TIMEOUT:-3600}"
PUSH_GATEWAY="${LUTHOR_PROMETHEUS_PUSH_GATEWAY:-}"

usage() {
  cat <<'EOF'
Usage: scripts/deploy_cloud_run.sh [options]

Environment variables:
  GCP_PROJECT_ID / GOOGLE_CLOUD_PROJECT   Google Cloud project (required)
  GCP_REGION                              Cloud Run region (default: europe-west1)
  CLOUD_RUN_SERVICE                       Service name (default: luthor)
  IMAGE_TAG                               Image tag / SHORT_SHA (default: git short SHA)
  CLOUD_RUN_MEMORY                        Memory limit (default: 1Gi)
  CLOUD_RUN_CPU                           CPU count (default: 1)
  CLOUD_RUN_TIMEOUT                       Request timeout seconds (default: 3600)
  LUTHOR_PROMETHEUS_PUSH_GATEWAY          Optional Pushgateway URL for serverless metrics

Options:
  -h, --help    Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${PROJECT_ID}" ]]; then
  echo "Error: set GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT." >&2
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "Error: gcloud CLI is required." >&2
  exit 1
fi

echo "Deploying LUTHOR to Cloud Run"
echo "  project : ${PROJECT_ID}"
echo "  region  : ${REGION}"
echo "  service : ${SERVICE_NAME}"
echo "  image   : gcr.io/${PROJECT_ID}/luthor:${IMAGE_TAG}"
if [[ -n "${PUSH_GATEWAY}" ]]; then
  echo "  pushgw  : ${PUSH_GATEWAY}"
fi

gcloud builds submit \
  --project "${PROJECT_ID}" \
  --config cloudbuild.yaml \
  --substitutions="SHORT_SHA=${IMAGE_TAG},_REGION=${REGION},_SERVICE_NAME=${SERVICE_NAME},_MEMORY=${MEMORY},_CPU=${CPU},_TIMEOUT=${TIMEOUT},_LUTHOR_PROMETHEUS_PUSH_GATEWAY=${PUSH_GATEWAY}"

echo "Deployment complete."
echo "Service URL:"
gcloud run services describe "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --format='value(status.url)'
