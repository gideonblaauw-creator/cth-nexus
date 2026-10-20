#!/usr/bin/env python3
"""Build GITHUB_COMMIT_MULTIPLE_FILES payload JSON for Composio."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BRANCH = "cursor/nexus-startup-onepagers-5adf"
OWNER = "gideonblaauw-creator"
REPO = "cth-nexus"


def upsert(path: Path, repo_root: Path) -> dict:
    rel = path.relative_to(repo_root).as_posix()
    content = path.read_text(encoding="utf-8")
    return {"path": rel, "content": content, "encoding": "utf-8"}


def default_paths(slug: str) -> list[Path]:
    return [
        ROOT / "onepagers" / "data" / f"{slug}.json",
        ROOT / "onepagers" / "sites" / slug / "index.html",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", help="Startup slug (adds data JSON + site HTML)")
    parser.add_argument(
        "--paths",
        nargs="+",
        help="Explicit repo-relative or absolute file paths to upsert",
    )
    parser.add_argument("--message", required=True, help="Git commit message")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--repo", default=REPO)
    args = parser.parse_args()

    paths: list[Path] = []
    if args.slug:
        paths.extend(default_paths(args.slug))
    if args.paths:
        for p in args.paths:
            path = Path(p)
            if not path.is_absolute():
                path = ROOT / path
            paths.append(path)

    if not paths:
        parser.error("Provide --slug and/or --paths")

    upserts = []
    for path in paths:
        if not path.is_file():
            print(f"Missing file: {path}", file=sys.stderr)
            return 1
        upserts.append(upsert(path, ROOT))

    payload = {
        "owner": args.owner,
        "repo": args.repo,
        "branch": args.branch,
        "message": args.message,
        "upserts": upserts,
    }
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
