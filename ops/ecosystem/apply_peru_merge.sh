#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET_ROOT="${NEXUS_STATIC_ROOT:-/opt/cth-nexus/static}"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/var/backups/nexus-eco-peru-${TS}"
SRC_DIR="${ROOT}/static"

echo "Source:      ${SRC_DIR}/ecosystem"
echo "Target:      ${TARGET_ROOT}/ecosystem"
echo "Backup:      ${BACKUP_DIR}"

sudo mkdir -p "${BACKUP_DIR}"
if [[ -d "${TARGET_ROOT}/ecosystem" ]]; then
  sudo cp -a "${TARGET_ROOT}/ecosystem" "${BACKUP_DIR}/"
fi

cat > "/tmp/rollback-nexus-eco-peru-${TS}.sh" <<ROLL
#!/usr/bin/env bash
set -euo pipefail
sudo rm -rf "${TARGET_ROOT}/ecosystem"
sudo cp -a "${BACKUP_DIR}/ecosystem" "${TARGET_ROOT}/ecosystem"
echo "Restored ecosystem from ${BACKUP_DIR}"
ROLL
chmod +x "/tmp/rollback-nexus-eco-peru-${TS}.sh"
sudo cp "/tmp/rollback-nexus-eco-peru-${TS}.sh" "${BACKUP_DIR}/rollback.sh"
sudo chmod +x "${BACKUP_DIR}/rollback.sh"

sudo mkdir -p "${TARGET_ROOT}/ecosystem/data" "${TARGET_ROOT}/nexus-assets"
sudo cp -a "${SRC_DIR}/ecosystem/." "${TARGET_ROOT}/ecosystem/"
if [[ -f "${ROOT}/nexus-assets/nexus-latam-map.js" ]]; then
  sudo cp -a "${ROOT}/nexus-assets/nexus-latam-map.js" "${TARGET_ROOT}/nexus-assets/nexus-latam-map.js"
fi

VERIFY_URL="${NEXUS_ECOSYSTEM_VERIFY_URL:-https://nexus.cleantechhub.net/ecosystem/}"
curl -fsSI "${VERIFY_URL}" | head -5
echo "Rollback: sudo ${BACKUP_DIR}/rollback.sh"
