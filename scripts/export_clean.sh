#!/usr/bin/env bash
# Export a clean copy of LUTHOR without dev/cache artifacts.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:-${ROOT_DIR}/../LUTHOR-complete}"

mkdir -p "${DEST}"

tar -C "${ROOT_DIR}" \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='node_modules' \
  --exclude='website/node_modules' \
  --exclude='.dvc/cache' \
  --exclude='backups' \
  --exclude='demo_outputs' \
  --exclude='.cursor' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='*.egg-info' \
  --exclude='.env.prod' \
  --exclude="$(basename "${DEST}")" \
  -cf - . | tar -xf - -C "${DEST}"

echo "Export terminé : ${DEST}"
