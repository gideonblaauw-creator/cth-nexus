#!/bin/bash
# Daily backup of origo.db — run via cron:
# 0 3 * * * www-data /opt/data-platform/scripts/backup.sh

BACKUP_DIR="/opt/data-platform/backups"
mkdir -p "$BACKUP_DIR"

DATE=$(date +%Y%m%d)

sqlite3 /opt/data-platform/db/origo.db .dump | gzip > "$BACKUP_DIR/origo_${DATE}.sql.gz"
sqlite3 /opt/data-platform/db/apikeys.db .dump | gzip > "$BACKUP_DIR/apikeys_${DATE}.sql.gz"
sqlite3 /opt/data-platform/db/provenance.db .dump | gzip > "$BACKUP_DIR/provenance_${DATE}.sql.gz"

# Retain 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
