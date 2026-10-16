#!/usr/bin/env python3
"""Merge CLP26 mentor/juror additions into live Nexus roster files on the VPS.

Reads data/clp26/nexus_roster_additions.json, backs up targets, then appends
new MENTORS entries to mentor-directory index.html and rows to
CTH_Master_Mentors.xlsx. Skips duplicates (by id, normalized name, or LinkedIn URL).

The live index.html uses a JavaScript object-literal array (unquoted keys), not JSON.
Existing array text is left byte-for-byte unchanged; new objects are appended before
the closing ``]`` in the same style.

Requires: pip install openpyxl

Default VPS paths (override with flags):
  /opt/cth-nexus/static/mentor-directory/index.html
  /opt/cth-nexus/data/CTH_Master_Mentors.xlsx
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ADDITIONS = ROOT / "data/clp26/nexus_roster_additions.json"
DEFAULT_HTML = Path("/opt/cth-nexus/static/mentor-directory/index.html")
DEFAULT_XLSX = Path("/opt/cth-nexus/data/CTH_Master_Mentors.xlsx")

MENTORS_MARKER = re.compile(r"const\s+MENTORS\s*=\s*\[", re.MULTILINE)

# Tolerant scans of JS object literals inside the MENTORS array body.
_RE_ID = re.compile(r'\bid\s*:\s*"((?:\\.|[^"\\])*)"')
_RE_NAME = re.compile(r'\bname\s*:\s*"((?:\\.|[^"\\])*)"')
_RE_LINKEDIN = re.compile(r'\blinkedin\s*:\s*"((?:\\.|[^"\\])*)"')


def norm_name(name: str) -> str:
    s = name.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)


def norm_linkedin(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = u.rstrip("/")
    return u


def js_unquote(s: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == "n":
                out.append("\n")
            elif nxt == "r":
                out.append("\r")
            elif nxt in ('"', "\\"):
                out.append(nxt)
            else:
                out.append(nxt)
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def js_quote(s: str) -> str:
    """Double-quoted JS string literal (unquoted object keys)."""
    out: list[str] = ['"']
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def load_additions(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    additions = list(data.get("additions") or [])
    validate_additions(additions)
    return additions


def validate_additions(additions: list[dict]) -> None:
    """Reject roster entries with no linkedin_url (Nexus policy)."""
    missing = [
        f"{e.get('id') or '?'} ({e.get('name') or 'unknown'})"
        for e in additions
        if not (e.get("linkedin_url") or "").strip()
    ]
    if missing:
        print(
            "Refusing to apply: every entry must have linkedin_url. Missing:\n  "
            + "\n  ".join(missing),
            file=sys.stderr,
        )
        raise SystemExit(2)


def backup_file(path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, dest)
    return dest


def find_mentors_array_bounds(html: str) -> tuple[int, int]:
    """Return (index of '[', index of matching ']') for the MENTORS array."""
    m = MENTORS_MARKER.search(html)
    if not m:
        raise ValueError("Could not find `const MENTORS = [` in index.html")
    start = m.end() - 1  # points at '['
    depth = 0
    i = start
    in_string: str | None = None
    escape = False
    while i < len(html):
        ch = html[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
            i += 1
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return start, i
        i += 1
    raise ValueError("Unclosed MENTORS array in index.html")


def parse_mentors_array_body(array_body: str) -> tuple[set[str], set[str], set[str]]:
    """Extract id / name / linkedin keys from existing JS object literals."""
    ids = {js_unquote(m.group(1)) for m in _RE_ID.finditer(array_body)}
    names = {norm_name(js_unquote(m.group(1))) for m in _RE_NAME.finditer(array_body)}
    links = {
        norm_linkedin(js_unquote(m.group(1)))
        for m in _RE_LINKEDIN.finditer(array_body)
        if m.group(1).strip()
    }
    return ids, names, links


def format_mentor_object_js(entry: dict) -> str:
    """Single mentor object in live Nexus style: {id:"…",name:"…",linkedin:"…",desc:"…"}."""
    li = (entry.get("linkedin_url") or entry.get("linkedin") or "").strip()
    desc = entry.get("desc") or ""
    parts = [
        f"id:{js_quote(entry['id'])}",
        f"name:{js_quote(entry['name'])}",
        f"linkedin:{js_quote(li)}",
        f"desc:{js_quote(desc)}",
    ]
    photo = (entry.get("photo") or "").strip()
    if photo:
        parts.append(f"photo:{js_quote(photo)}")
    return "{" + ",".join(parts) + "}"


def merge_html(html_path: Path, additions: list[dict], dry_run: bool) -> tuple[int, int]:
    html = html_path.read_text(encoding="utf-8")
    open_bracket, close_bracket = find_mentors_array_bounds(html)
    array_body = html[open_bracket + 1 : close_bracket]
    ids, names, links = parse_mentors_array_body(array_body)

    to_append: list[str] = []
    added = 0
    skipped = 0
    for entry in additions:
        if not (entry.get("linkedin_url") or "").strip():
            skipped += 1
            continue
        mid = entry.get("id")
        name_k = norm_name(entry.get("name", ""))
        link_k = norm_linkedin(entry.get("linkedin") or entry.get("linkedin_url"))
        if mid in ids or name_k in names or (link_k and link_k in links):
            skipped += 1
            continue
        to_append.append(format_mentor_object_js(entry))
        ids.add(mid)
        names.add(name_k)
        if link_k:
            links.add(link_k)
        added += 1

    if added and not dry_run:
        prefix = html[:close_bracket]
        suffix = html[close_bracket:]
        needs_comma = bool(array_body.strip())
        insert = ("," if needs_comma else "") + ",".join(to_append)
        html_path.write_text(prefix + insert + suffix, encoding="utf-8")

    return added, skipped


def merge_xlsx(xlsx_path: Path, additions: list[dict], dry_run: bool) -> tuple[int, int]:
    try:
        import openpyxl
    except ImportError:
        print("openpyxl is required: pip install openpyxl", file=sys.stderr)
        raise

    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    headers = {str(ws.cell(1, c).value or "").strip(): c for c in range(1, ws.max_column + 1)}

    def col(name: str) -> int | None:
        return headers.get(name)

    id_col = col("ID") or 1
    existing_ids: set[str] = set()
    existing_names: set[str] = set()
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row, id_col).value
        if val:
            existing_ids.add(str(val).strip())
        name_col = col("Full Name")
        if name_col:
            n = ws.cell(row, name_col).value
            if n:
                existing_names.add(norm_name(str(n)))

    added = 0
    skipped = 0
    roles_note = lambda e: ", ".join(e.get("clp26_roles") or [])

    for entry in additions:
        if not (entry.get("linkedin_url") or "").strip():
            skipped += 1
            continue
        mid = entry.get("id")
        name_k = norm_name(entry.get("name", ""))
        if mid in existing_ids or name_k in existing_names:
            skipped += 1
            continue

        row_idx = ws.max_row + 1
        ws.cell(row_idx, id_col, mid)

        if (c := col("Full Name")):
            ws.cell(row_idx, c, entry.get("name"))
        if (c := col("Email")):
            ws.cell(row_idx, c, entry.get("email") or "")
        if (c := col("Current Company")):
            ws.cell(row_idx, c, entry.get("organisation") or entry.get("company") or "")
        if (c := col("Expertise Area")):
            ws.cell(row_idx, c, entry.get("expertise") or "")
        if (c := col("Programs")):
            ws.cell(row_idx, c, "CLP26")
        if (c := col("First Program Year")):
            ws.cell(row_idx, c, "2026")
        if (c := col("Mentor Status")):
            ws.cell(row_idx, c, entry.get("status") or "Active")
        if (c := col("Habeas Data Signed")):
            ws.cell(row_idx, c, "Unknown")
        if (c := col("Nexus Claimed")):
            ws.cell(row_idx, c, "No")
        if (c := col("LMS Enrolled")):
            ws.cell(row_idx, c, "No")
        if (c := col("LinkedIn URL")) and entry.get("linkedin_url"):
            ws.cell(row_idx, c, entry["linkedin_url"])
        if (c := col("Notes")):
            country = entry.get("country") or ""
            ws.cell(
                row_idx,
                c,
                f"CLP26 {roles_note(entry)}".strip()
                + (f"; country={country}" if country else ""),
            )

        existing_ids.add(mid)
        existing_names.add(name_k)
        added += 1

    if added and not dry_run:
        wb.save(xlsx_path)

    return added, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--additions",
        type=Path,
        default=DEFAULT_ADDITIONS,
        help="Path to nexus_roster_additions.json",
    )
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report counts only; do not write files or create backups",
    )
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Do not create .bak-* copies before writing (not recommended)",
    )
    args = parser.parse_args()

    if not args.additions.is_file():
        print(f"Additions file not found: {args.additions}", file=sys.stderr)
        return 1

    additions = load_additions(args.additions)
    if not additions:
        print("No additions to apply.")
        return 0

    for label, path in (("HTML", args.html), ("XLSX", args.xlsx)):
        if not path.is_file():
            print(f"{label} target not found: {path}", file=sys.stderr)
            return 1

    if not args.dry_run and not args.skip_backup:
        html_bak = backup_file(args.html)
        xlsx_bak = backup_file(args.xlsx)
        print(f"Backed up HTML -> {html_bak}")
        print(f"Backed up XLSX -> {xlsx_bak}")

    html_added, html_skipped = merge_html(args.html, additions, args.dry_run)
    xlsx_added, xlsx_skipped = merge_xlsx(args.xlsx, additions, args.dry_run)

    mode = "dry-run" if args.dry_run else "applied"
    print(
        f"{mode}: HTML added {html_added}, skipped {html_skipped}; "
        f"XLSX added {xlsx_added}, skipped {xlsx_skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
