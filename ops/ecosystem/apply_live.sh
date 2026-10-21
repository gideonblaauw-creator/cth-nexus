#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/var/backups/nexus-eco-geo-${TS}"
LIVE_DATA="/opt/cth-nexus/static/ecosystem/data/actors.json"
LIVE_MAP="/opt/cth-nexus/static/nexus-assets/nexus-latam-map.js"

mkdir -p "$BACKUP/ecosystem/data" "$BACKUP/nexus-assets"
cp -a "$LIVE_DATA" "$BACKUP/ecosystem/data/actors.json"
if [[ -f "$LIVE_MAP" ]]; then
  cp -a "$LIVE_MAP" "$BACKUP/nexus-assets/nexus-latam-map.js"
fi

cat > "$BACKUP/rollback.sh" <<ROLL
#!/usr/bin/env bash
set -euo pipefail
cp -a "$BACKUP/ecosystem/data/actors.json" "$LIVE_DATA"
if [[ -f "$BACKUP/nexus-assets/nexus-latam-map.js" ]]; then
  cp -a "$BACKUP/nexus-assets/nexus-latam-map.js" "$LIVE_MAP"
fi
echo "Rolled back ecosystem geo from $BACKUP"
ROLL
chmod +x "$BACKUP/rollback.sh"

cp -a "$ROOT/static/ecosystem/data/actors.json" "$LIVE_DATA"
cp -a "$ROOT/nexus-assets/nexus-latam-map.js" "$LIVE_MAP"
echo "Applied geo data. Backup: $BACKUP"
echo "Rollback: $BACKUP/rollback.sh"
