#!/usr/bin/env bash
# Restore LUTHOR production Docker volumes from ./backups/<stamp>/
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

BACKUP_DIR="${1:-}"
if [[ -z "${BACKUP_DIR}" ]]; then
  echo "Usage: $0 <backup-directory>"
  echo "Example: $0 backups/20260104-120000"
  exit 1
fi

if [[ ! -d "${BACKUP_DIR}" ]]; then
  echo "Backup directory not found: ${BACKUP_DIR}"
  exit 1
fi

read -r -p "This will OVERWRITE production volumes. Continue? [y/N] " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

echo "Stopping stack..."
docker compose -f docker-compose.prod.yml down

restore_volume() {
  local archive="$1"
  local volume="$2"
  if [[ ! -f "${archive}" ]]; then
    echo "  (skip ${volume} — archive missing)"
    return
  fi
  echo "  → ${volume}"
  docker volume create "${volume}" >/dev/null 2>&1 || true
  docker run --rm \
    -v "${volume}:/volume" \
    -v "${ROOT_DIR}/${BACKUP_DIR}:/backup:ro" \
    alpine:3.20 \
    sh -c "rm -rf /volume/* /volume/.[!.]* 2>/dev/null || true; tar xzf /backup/$(basename "${archive}") -C /volume"
}

for archive in "${BACKUP_DIR}"/*.tar.gz; do
  [[ -e "${archive}" ]] || continue
  base="$(basename "${archive}" .tar.gz)"
  restore_volume "${archive}" "${base}"
done

echo "Starting stack..."
docker compose -f docker-compose.prod.yml up -d

echo "Restore complete from ${BACKUP_DIR}"
