#!/usr/bin/env bash
# Deploy Nexus static surfaces from this repo to VPS paths. Creates rollback.sh under /var/backups/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/var/backups/nexus-deploy-${STAMP}"
ROLLBACK="${BACKUP}/rollback.sh"

mkdir -p "$BACKUP"
cat > "$ROLLBACK" <<EOF
#!/usr/bin/env bash
set -euo pipefail
# Rollback Nexus deploy ${STAMP}
rsync -a "${BACKUP}/var-www-nexus/" /var/www/nexus/
rsync -a "${BACKUP}/opt-cth-nexus-static/" /opt/cth-nexus/static/
rsync -a "${BACKUP}/var-www-nexus-assets/" /var/www/nexus-assets/
rsync -a "${BACKUP}/opt-nexus-onepagers/" /opt/nexus-onepagers/
echo "Rollback complete for ${STAMP}"
EOF
chmod +x "$ROLLBACK"

echo "Backing up live trees to ${BACKUP}..."
mkdir -p "${BACKUP}/var-www-nexus" "${BACKUP}/opt-cth-nexus-static" "${BACKUP}/var-www-nexus-assets" "${BACKUP}/opt-nexus-onepagers"
rsync -a /var/www/nexus/ "${BACKUP}/var-www-nexus/"
rsync -a /opt/cth-nexus/static/ "${BACKUP}/opt-cth-nexus-static/"
rsync -a /var/www/nexus-assets/ "${BACKUP}/var-www-nexus-assets/"
rsync -a /opt/nexus-onepagers/ "${BACKUP}/opt-nexus-onepagers/"

echo "Deploying portfolio..."
install -D -m 0644 "${ROOT}/site/nexus-www/startup-portfolio.html" /var/www/nexus/startup-portfolio.html

echo "Deploying hubs + ecosystem static..."
rsync -a "${ROOT}/site/cth-static/hubs/" /opt/cth-nexus/static/hubs/
rsync -a "${ROOT}/static/ecosystem/" /opt/cth-nexus/static/ecosystem/

echo "Deploying nexus-assets..."
rsync -a "${ROOT}/nexus-assets/" /var/www/nexus-assets/

echo "Deploying /s/ one-pagers..."
rsync -a "${ROOT}/onepagers/sites/" /opt/nexus-onepagers/

echo "Deploy finished. Rollback: sudo bash ${ROLLBACK}"
