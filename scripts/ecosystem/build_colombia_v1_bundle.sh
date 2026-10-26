#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
python3 scripts/ecosystem/append_colombia_v1_from_snapshot.py
python3 scripts/ecosystem/build_public_data.py
python3 scripts/ecosystem/preserve_main_existing_actors.py
python3 scripts/ecosystem/strip_colombia_v1_public_addresses.py
python3 scripts/ecosystem/verify_colombia_v1_baseline.py
