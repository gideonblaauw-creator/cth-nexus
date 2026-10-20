#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/../screenshots"
mkdir -p "$OUT"
PORT=8765
python3 -m http.server "$PORT" --directory "$ROOT" >/tmp/eco-http.log 2>&1 &
PID=$!
sleep 1
trap 'kill $PID 2>/dev/null || true' EXIT

declare -a SPECS=(
  "d1-geo-arcs|d1-geo-arcs.png"
  "d2-force-cluster|d2-force-cluster.png"
  "d3-hybrid-split|d3-hybrid-split.png"
  "d4-flow-matrix|d4-flow-matrix.png"
  "d5-story-explorer|d5-story-explorer.png"
)

for spec in "${SPECS[@]}"; do
  dir="${spec%%|*}"
  file="${spec##*|}"
  url="http://127.0.0.1:${PORT}/${dir}/index.html"
  google-chrome --headless=new --disable-gpu --hide-scrollbars \
    --window-size=1440,900 --virtual-time-budget=8000 \
    --screenshot="$OUT/$file" "$url"
  echo "Wrote $OUT/$file"
done
