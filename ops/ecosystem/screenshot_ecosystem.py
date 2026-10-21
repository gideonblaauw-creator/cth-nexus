#!/usr/bin/env python3
"""Capture Leaflet ecosystem map zooms (Peru, Colombia, El Salvador)."""
from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTORS = ROOT / "static" / "ecosystem" / "data" / "actors.json"
MAP_JS = ROOT / "nexus-assets" / "nexus-latam-map.js"
OUT_DIR = Path("/opt/cursor/artifacts/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def write_fixture(actors_path: Path, map_js_path: Path, html_path: Path) -> None:
    actors = json.loads(actors_path.read_text(encoding="utf-8"))
    map_js = map_js_path.read_text(encoding="utf-8")
    html = textwrap.dedent(
        f"""
        <!DOCTYPE html>
        <html><head>
          <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
          <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
          <style>html,body,#eco-leaflet-map{{margin:0;height:100vh;width:100vw}}</style>
        </head>
        <body>
          <div id="eco-leaflet-map"></div>
          <script>{map_js}</script>
          <script>
            const actors = {json.dumps(actors, ensure_ascii=False)};
            window.addEventListener('load', () => {{
              NexusLatamMap.mountEcosystemMap('eco-leaflet-map', actors, () => {{}});
            }});
          </script>
        </body></html>
        """
    )
    html_path.write_text(html, encoding="utf-8")


def shot(label: str, html: Path, center: tuple[float, float], zoom: int, out: Path) -> None:
    lat, lng = center
    js = f"""
    (async () => {{
      const m = document.getElementById('eco-leaflet-map')._nexusEcoMap;
      if (m) m.setView([{lat}, {lng}], {zoom});
      await new Promise(r => setTimeout(r, 1200));
    }})();
    """
    subprocess.run(
        [
            "chromium",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--window-size=1280,800",
            f"--screenshot={out}",
            "--run-all-compositor-stages-before-draw",
            f"file://{html}",
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )


def main() -> None:
    import sys

    tag = sys.argv[1] if len(sys.argv) > 1 else "after"
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "map.html"
        write_fixture(ACTORS, MAP_JS, html)
        views = [
            ("peru", (-9.5, -76.0), 6),
            ("colombia", (4.6, -74.1), 6),
            ("el-salvador", (13.7, -89.2), 8),
        ]
        for name, center, zoom in views:
            out = OUT_DIR / f"ecosystem-{tag}-{name}.png"
            shot(name, html, center, zoom, out)
            print(out)


if __name__ == "__main__":
    main()
