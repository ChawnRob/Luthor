#!/usr/bin/env bash
# Deploy LUTHOR production stack on a European VPS (Docker Compose).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
MAX_WAIT_SECONDS=300

usage() {
  cat <<'EOF'
Usage: scripts/deploy_prod.sh [options]

Deploy the full LUTHOR production stack (API, monitoring, MCP tools).

Prerequisites:
  - Docker Engine + Docker Compose plugin
  - DNS A records for luthor.example.com and subdomains
  - .env.prod configured (copy from .env.prod.example)

Options:
  -h, --help       Show this help
  --pull-only      Pull images without starting services
  --no-build       Skip API image build
EOF
}

log() {
  printf '[deploy_prod] %s\n' "$*"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Error: '$1' is required but not installed."
    exit 1
  fi
}

wait_for_service() {
  local service="$1"
  local elapsed=0
  while (( elapsed < MAX_WAIT_SECONDS )); do
    if docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" ps "${service}" 2>/dev/null | grep -q "(healthy)"; then
      log "${service} is healthy"
      return 0
    fi
    if docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" ps "${service}" 2>/dev/null | grep -q "Up"; then
      if [[ "${service}" != "postgres" && "${service}" != "chromadb" && "${service}" != "api" ]]; then
        log "${service} is up"
        return 0
      fi
    fi
    sleep 5
    elapsed=$((elapsed + 5))
  done
  log "Warning: timed out waiting for ${service}"
  return 1
}

PULL_ONLY=false
NO_BUILD=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --pull-only)
      PULL_ONLY=true
      shift
      ;;
    --no-build)
      NO_BUILD=true
      shift
      ;;
    *)
      log "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

require_command docker
if ! docker compose version >/dev/null 2>&1; then
  log "Error: Docker Compose plugin is required (docker compose)."
  exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  log "Error: ${COMPOSE_FILE} not found. Run from repository root."
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ -f .env.prod.example ]]; then
    log "Creating ${ENV_FILE} from .env.prod.example — edit secrets before production use."
    cp .env.prod.example "${ENV_FILE}"
  else
    log "Error: ${ENV_FILE} missing."
    exit 1
  fi
fi

# shellcheck disable=SC1090
set -a
source "${ENV_FILE}"
set +a

for var in LUTHOR_DOMAIN POSTGRES_PASSWORD ACME_EMAIL; do
  if [[ -z "${!var:-}" ]]; then
    log "Error: ${var} must be set in ${ENV_FILE}"
    exit 1
  fi
done

if [[ "${POSTGRES_PASSWORD}" == "change-me-strong-password" ]]; then
  log "Warning: replace default POSTGRES_PASSWORD in ${ENV_FILE}"
fi

log "Deploying LUTHOR on domain: ${LUTHOR_DOMAIN}"

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" pull

if [[ "${PULL_ONLY}" == "true" ]]; then
  log "Pull complete (--pull-only)."
  exit 0
fi

BUILD_ARGS=()
if [[ "${NO_BUILD}" == "false" ]]; then
  BUILD_ARGS=(build api)
fi

if [[ ${#BUILD_ARGS[@]} -gt 0 ]]; then
  docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" "${BUILD_ARGS[@]}"
fi

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d

wait_for_service postgres || true
wait_for_service chromadb || true
wait_for_service api || true

if command -v curl >/dev/null 2>&1; then
  if curl -fsS "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    log "API health check OK (direct port if exposed)"
  elif curl -fsS "https://${LUTHOR_DOMAIN}/health" >/dev/null 2>&1; then
    log "API health check OK (https://${LUTHOR_DOMAIN}/health)"
  else
    log "Health check pending — Traefik/Let's Encrypt may need a few minutes."
  fi
fi

cat <<EOF

Deployment started.

URLs (after DNS + TLS propagation):
  API        https://${LUTHOR_DOMAIN}
  Demo UI    https://${LUTHOR_DOMAIN}/demo-ui
  Grafana    https://grafana.${LUTHOR_DOMAIN}
  Prometheus https://prometheus.${LUTHOR_DOMAIN}
  n8n        https://n8n.${LUTHOR_DOMAIN}
  Plausible  https://plausible.${LUTHOR_DOMAIN}
  Cal.com    https://cal.${LUTHOR_DOMAIN}
  Fooocus    https://fooocus.${LUTHOR_DOMAIN}

Verify:
  docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} ps
  curl -I https://${LUTHOR_DOMAIN}/health

Backups:
  scripts/backup_prod.sh

Security:
  sudo ufw allow OpenSSH
  sudo ufw allow 80,443/tcp
  sudo ufw enable

EOF
