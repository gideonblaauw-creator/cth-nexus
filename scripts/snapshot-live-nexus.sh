#!/usr/bin/env bash
# Read-only snapshot of live Nexus paths into repo site/ and app/
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$REPO_ROOT/ops/snapshot-exclusions.txt"
: > "$MANIFEST"

RSYNC_EXCLUDES=(
  --exclude='.env'
  --exclude='.env.*'
  --exclude='*.pem'
  --exclude='*.key'
  --exclude='id_rsa*'
  --exclude='*.p12'
  --exclude='*.pfx'
  --exclude='credentials*'
  --exclude='*secret*'
  --exclude='*.bak'
  --exclude='*.bak-*'
  --exclude='*~'
  --exclude='*.db'
  --exclude='*.sqlite'
  --exclude='*.sqlite3'
  --exclude='node_modules/'
  --exclude='venv/'
  --exclude='.venv/'
  --exclude='.git/'
  --exclude='__pycache__/'
  --exclude='logs/'
  --exclude='backups/'
  --exclude='.next/'
  --exclude='graphify-out/'
)

log_exclusion() {
  echo "$1" >> "$MANIFEST"
}

# Record rsync exclude patterns for the report
for x in "${RSYNC_EXCLUDES[@]}"; do
  log_exclusion "pattern: ${x#--exclude=}"
done

copy_tree() {
  local src="$1"
  local dest="$2"
  local label="$3"
  if [[ ! -d "$src" ]]; then
    echo "SKIP missing: $src" >&2
    return 0
  fi
  mkdir -p "$dest"
  rsync -a "${RSYNC_EXCLUDES[@]}" "$src/" "$dest/"
  # Drop files >50MB
  while IFS= read -r -d '' big; do
    rel="${big#"$dest"/}"
    log_exclusion "$label/$rel (>50MB)"
    rm -f "$big"
  done < <(find "$dest" -type f -size +50M -print0)
  if [[ "$label" == app/cth-nexus* ]]; then
    rm -rf "$dest/data" 2>/dev/null || true
    log_exclusion "$label/data/ (runtime data dir)"
  fi
}

echo "Snapshot into $REPO_ROOT"

# Static roots (Caddy file_server)
copy_tree /var/www/nexus "$REPO_ROOT/site/nexus-www" "site/nexus-www"
copy_tree /var/www/nexus-assets "$REPO_ROOT/site/nexus-assets" "site/nexus-assets"
copy_tree /var/www/seo-static "$REPO_ROOT/site/seo-static" "site/seo-static"
copy_tree /opt/nexus-onepagers "$REPO_ROOT/site/onepagers" "site/onepagers"
copy_tree /opt/nexus-investors/dist "$REPO_ROOT/site/investors" "site/investors"
copy_tree /opt/cth-nexus/static "$REPO_ROOT/site/cth-static" "site/cth-static"

# reverse_proxy :5050 Flask (WorkingDirectory /opt/cth-nexus)
mkdir -p "$REPO_ROOT/app/cth-nexus"
copy_tree /opt/cth-nexus/api "$REPO_ROOT/app/cth-nexus/api" "app/cth-nexus/api"
copy_tree /opt/cth-nexus/docs "$REPO_ROOT/app/cth-nexus/docs" "app/cth-nexus/docs"
for f in /opt/cth-nexus/*.py /opt/cth-nexus/*.md /opt/cth-nexus/requirements*.txt; do
  [[ -f "$f" ]] && cp -a "$f" "$REPO_ROOT/app/cth-nexus/" || true
done

# reverse_proxy :3010 Next.js idea browser
copy_tree /opt/nexus-idea-browser "$REPO_ROOT/app/nexus-ideas" "app/nexus-ideas"

# reverse_proxy :8011 data platform API
mkdir -p "$REPO_ROOT/app/data-platform"
copy_tree /opt/data-platform/app "$REPO_ROOT/app/data-platform/app" "app/data-platform/app"
copy_tree /opt/data-platform/deploy "$REPO_ROOT/app/data-platform/deploy" "app/data-platform/deploy"
copy_tree /opt/data-platform/scripts "$REPO_ROOT/app/data-platform/scripts" "app/data-platform/scripts"
copy_tree /opt/data-platform/shacl "$REPO_ROOT/app/data-platform/shacl" "app/data-platform/shacl"
copy_tree /opt/data-platform/opa "$REPO_ROOT/app/data-platform/opa" "app/data-platform/opa"
copy_tree /opt/data-platform/tests "$REPO_ROOT/app/data-platform/tests" "app/data-platform/tests"
for f in /opt/data-platform/pyproject.toml /opt/data-platform/requirements.txt /opt/data-platform/CLAUDE.md; do
  [[ -f "$f" ]] && cp -a "$f" "$REPO_ROOT/app/data-platform/" || true
done

# reverse_proxy :8080 catch-all (HumHub themes on disk; full app is container babo)
copy_tree /opt/nexus/humhub "$REPO_ROOT/app/humhub" "app/humhub"
log_exclusion "app/babo/ (reverse_proxy 127.0.0.1:8080 Docker babo/channel-layer; no source tree on VPS)"

sort -u "$MANIFEST" -o "$MANIFEST"
echo "Done. Exclusions logged to ops/snapshot-exclusions.txt"
