#!/usr/bin/env bash
set -euo pipefail

# Deploy Nexus Ecosystem static bundle to /opt/cth-nexus/static (live Nexus root).
# Creates a timestamped backup under /var/backups/nexus-ecosystem-<ts>/ before copying.

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_ROOT="${NEXUS_STATIC_ROOT:-/opt/cth-nexus/static}"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/var/backups/nexus-ecosystem-${TS}"

echo "Source:      ${SRC_DIR}"
echo "Target root: ${TARGET_ROOT}"
echo "Backup:      ${BACKUP_DIR}"

sudo mkdir -p "${BACKUP_DIR}"
if [[ -d "${TARGET_ROOT}/ecosystem" ]]; then
  sudo cp -a "${TARGET_ROOT}/ecosystem" "${BACKUP_DIR}/"
fi
if [[ -f "${TARGET_ROOT}/nexus-assets/nexus-nav.js" ]]; then
  sudo mkdir -p "${BACKUP_DIR}/nexus-assets"
  sudo cp -a "${TARGET_ROOT}/nexus-assets/nexus-nav.js" "${BACKUP_DIR}/nexus-assets/" || true
fi

sudo mkdir -p "${TARGET_ROOT}/ecosystem/data" "${TARGET_ROOT}/nexus-assets"
sudo cp -a "${SRC_DIR}/ecosystem/." "${TARGET_ROOT}/ecosystem/"
sudo cp -a "${SRC_DIR}/nexus-assets/nexus-nav.js" "${TARGET_ROOT}/nexus-assets/nexus-nav.js"
if [[ -f "${SRC_DIR}/nexus-assets/nexus-brand.css" ]]; then
  sudo cp -a "${SRC_DIR}/nexus-assets/nexus-brand.css" "${TARGET_ROOT}/nexus-assets/nexus-brand.css"
fi

VERIFY_URL="${NEXUS_ECOSYSTEM_VERIFY_URL:-https://nexus.cleantechhub.net/ecosystem/}"
echo "Verify: curl -fsSI ${VERIFY_URL}"
curl -fsSI "${VERIFY_URL}" | head -5 || {
  echo "WARN: verify failed (expected if Caddy forward_auth not configured yet)." >&2
  exit 0
}

echo "Done."
