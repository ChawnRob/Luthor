#!/usr/bin/env bash
# Export a clean copy of LUTHOR without dev/cache artifacts.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:-${ROOT_DIR}/../LUTHOR-complete}"

mkdir -p "${DEST}"

rsync -a --delete \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  --exclude 'node_modules/' \
  --exclude 'website/node_modules/' \
  --exclude '.dvc/cache/' \
  --exclude 'backups/' \
  --exclude 'demo_outputs/' \
  --exclude '*.pyc' \
  --exclude '.cursor/' \
  --exclude 'dist/' \
  --exclude 'build/' \
  --exclude '*.egg-info/' \
  --exclude '.env.prod' \
  "${ROOT_DIR}/" "${DEST}/"

echo "Export terminé : ${DEST}"
