#!/usr/bin/env bash
# Backup LUTHOR production Docker volumes to ./backups/
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${ROOT_DIR}/backups/${STAMP}"
mkdir -p "${BACKUP_DIR}"

VOLUMES=(
  luthor-prod_postgres_data
  luthor-prod_chroma_data
  luthor-prod_grafana_data
  luthor-prod_n8n_data
  luthor-prod_demo_outputs
  luthor-prod_ytdlp_downloads
)

echo "Backing up to ${BACKUP_DIR}"

for volume in "${VOLUMES[@]}"; do
  if docker volume inspect "${volume}" >/dev/null 2>&1; then
    echo "  → ${volume}"
    docker run --rm \
      -v "${volume}:/volume:ro" \
      -v "${BACKUP_DIR}:/backup" \
      alpine:3.20 \
      tar czf "/backup/${volume}.tar.gz" -C /volume .
  else
    echo "  (skip ${volume} — not found)"
  fi
done

echo "Done: ${BACKUP_DIR}"
