#!/bin/bash
# Monthly archive of provenance data older than 5 years — EUDR Article 10 retention
# Cron: 0 2 1 * * www-data /opt/data-platform/scripts/archive_policy_evals.sh

CUTOFF=$(date -d "5 years ago" +%Y-%m-%d 2>/dev/null || date -v-5y +%Y-%m-%d)
ARCHIVE_DIR="/opt/data-platform/archive"
mkdir -p "$ARCHIVE_DIR"

sqlite3 /opt/data-platform/db/provenance.db \
  "SELECT json_object('id',id,'entity_id',entity_id,'action',action,'created_at',created_at)
   FROM provenance_log WHERE created_at < '$CUTOFF';" \
  | gzip > "$ARCHIVE_DIR/provenance_log_archived_$(date +%Y%m%d).jsonl.gz"

# NOTE: Do NOT delete from provenance_log — triggers prevent it by design.
# Archive is a copy for off-VPS storage. The DB retains all rows.
