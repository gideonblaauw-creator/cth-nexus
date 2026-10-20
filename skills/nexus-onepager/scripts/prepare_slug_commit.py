#!/usr/bin/env python3
"""Build GITHUB_COMMIT_MULTIPLE_FILES payload including binary media (base64)."""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BRANCH = "cursor/nexus-startup-onepagers-5adf"
OWNER = "gideonblaauw-creator"
REPO = "cth-nexus"
TEXT_SUFFIXES = {".json", ".html", ".css", ".py", ".md", ".txt"}


def upsert_file(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return {"path": rel, "content": path.read_text(encoding="utf-8"), "encoding": "utf-8"}
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"path": rel, "content": data, "encoding": "base64"}


def slug_files(slug: str, include_pdf: bool = True) -> list[Path]:
    paths: list[Path] = [
        ROOT / "onepagers" / "data" / f"{slug}.json",
        ROOT / "onepagers" / "sites" / slug / "index.html",
    ]
    media = ROOT / "onepagers" / "media" / slug
    if media.is_dir():
        paths.extend(sorted(p for p in media.rglob("*") if p.is_file()))
    pdf = ROOT / "onepagers" / "sites" / slug / "deck.pdf"
    if include_pdf and pdf.is_file():
        paths.append(pdf)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args()

    upserts = []
    for path in slug_files(args.slug, include_pdf=not args.no_pdf):
        if not path.is_file():
            print(f"Missing: {path}", file=sys.stderr)
            return 1
        upserts.append(upsert_file(path))

    payload = {
        "owner": OWNER,
        "repo": REPO,
        "branch": args.branch,
        "message": args.message,
        "upserts": upserts,
    }
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
