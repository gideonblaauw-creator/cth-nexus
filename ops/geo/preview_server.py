#!/usr/bin/env python3
"""Local static router for ecosystem + HubMap Playwright previews (port 8797)."""
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PreviewHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean = path.split("?", 1)[0].split("#", 1)[0]
        if clean.startswith("/ecosystem"):
            rel = clean[len("/ecosystem") :] or "/index.html"
            return str(ROOT / "static" / "ecosystem" / rel.lstrip("/"))
        if clean.startswith("/nexus-assets/"):
            return str(ROOT / "site" / "nexus-assets" / clean[len("/nexus-assets/") :])
        if clean.startswith("/hubs/"):
            return str(ROOT / "site" / "cth-static" / "hubs" / clean[len("/hubs/") :])
        return str(ROOT / clean.lstrip("/"))

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> None:
    host, port = "127.0.0.1", 8797
    httpd = ThreadingHTTPServer((host, port), PreviewHandler)
    print(f"Preview server http://{host}:{port}/ecosystem/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
