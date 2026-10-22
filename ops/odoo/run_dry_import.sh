#!/usr/bin/env bash
# Dry-run Nexus → Odoo import. Credentials from Infisical only (cth-agents / prod).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export INFISICAL_DOMAIN="${INFISICAL_DOMAIN:-https://secrets.cleantechhub.net/api}"
exec npx --yes @infisical/cli@latest run --env=prod --projectId="${INFISICAL_PROJECT_ID:?Set INFISICAL_PROJECT_ID for cth-agents}" -- \
  python3 ops/odoo/import_nexus_partners.py "$@"
