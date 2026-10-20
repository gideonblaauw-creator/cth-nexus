#!/usr/bin/env python3
"""Split repo files into GITHUB_COMMIT_MULTIPLE_FILES batch JSON files."""
import base64
import json
import os
import sys

ROOT = os.environ.get("SNAPSHOT_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/nexus-snapshot-batches"
MAX_BATCH_BYTES = 70_000
OWNER, REPO, BRANCH = "gideonblaauw-creator", "cth-nexus", "main"
EXCLUDE_PREFIXES = tuple(sys.argv[2:]) if len(sys.argv) > 2 else ()

PREFIXES = ["site/", "app/", "scripts/snapshot-live-nexus.sh", "scripts/make_github_batches.py", "ops/snapshot-exclusions.txt"]

def iter_files():
    for prefix in PREFIXES:
        if prefix.endswith(".py") or prefix.endswith(".sh") or prefix.endswith(".txt"):
            p = os.path.join(ROOT, prefix)
            if os.path.isfile(p):
                yield prefix
            continue
        base = os.path.join(ROOT, prefix.rstrip("/"))
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for name in filenames:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ROOT).replace("\\", "/")
                if any(rel.startswith(ex) for ex in EXCLUDE_PREFIXES):
                    continue
                yield rel

def file_upsert(path):
    full = os.path.join(ROOT, path)
    with open(full, "rb") as f:
        data = f.read()
    try:
        text = data.decode("utf-8")
        return {"path": path, "content": text, "encoding": "utf-8", "_bytes": len(data)}
    except UnicodeDecodeError:
        return {
            "path": path,
            "content": base64.b64encode(data).decode(),
            "encoding": "base64",
            "_bytes": len(data),
        }

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    upserts = [file_upsert(p) for p in sorted(iter_files())]
    batches = []
    current = []
    size = 0
    for u in upserts:
        b = u.pop("_bytes")
        if b > MAX_BATCH_BYTES and not current:
            batches.append([u])
            continue
        if current and size + b > MAX_BATCH_BYTES:
            batches.append(current)
            current = []
            size = 0
        current.append(u)
        size += b
    if current:
        batches.append(current)
    manifest = []
    for i, batch in enumerate(batches):
        name = f"batch_{i:04d}.json"
        payload = {
            "owner": OWNER,
            "repo": REPO,
            "branch": BRANCH,
            "message": f"Snapshot: live Nexus roots 2026-10-19 (part {i + 1}/{len(batches)})",
            "upserts": batch,
        }
        path = os.path.join(OUT_DIR, name)
        with open(path, "w") as f:
            json.dump(payload, f)
        manifest.append({"file": name, "count": len(batch), "path": path})
    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump({"total_files": len(upserts), "batch_count": len(batches), "batches": manifest}, f, indent=2)
    print(json.dumps({"total_files": len(upserts), "batch_count": len(batches), "out_dir": OUT_DIR}))

if __name__ == "__main__":
    main()
