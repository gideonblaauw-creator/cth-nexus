"""Public Nexus bundles must not contain Odoo private-tier fields."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_JSON_GLOBS = [
    ROOT / "static" / "ecosystem" / "data" / "actors.json",
    ROOT / "static" / "ecosystem" / "data" / "relations.json",
    ROOT / "static" / "ecosystem" / "data" / "actor_cards.json",
    ROOT / "static" / "ecosystem" / "data" / "policies.json",
    ROOT / "static" / "ecosystem" / "data" / "nexus-crosslinks.json",
]

PUBLIC_HTML_GLOBS = [
    ROOT / "static" / "ecosystem" / "index.html",
    ROOT / "site" / "nexus-www" / "nexus-homepage.html",
]

# Keys that must never appear in public Nexus JSON (Odoo CRM / deal tier).
FORBIDDEN_JSON_KEYS = frozenset(
    {
        "odoo_id",
        "primary_contact_email",
        "primary_contact_name",
        "primary_contact_linkedin",
        "owner_email",
        "owner_name",
        "owner_text",
        "touchpoint",
        "outcome",
        "consent_to_publish",
        "internal_record_id",
        "mail_message",
        "deal_notes",
    }
)

FORBIDDEN_KEY_PATTERN = re.compile(
    r'"(?:odoo_id|x_[a-z0-9_]+|primary_contact_[a-z]+|owner_email)"\s*:',
    re.I,
)


def _walk_keys(obj, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k in FORBIDDEN_JSON_KEYS or k == "internal":
                hits.append(p)
            hits.extend(_walk_keys(v, p))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            hits.extend(_walk_keys(item, f"{path}[{i}]"))
    return hits


def test_public_ecosystem_json_has_no_odoo_private_fields():
    for path in PUBLIC_JSON_GLOBS:
        if not path.is_file():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        bad = _walk_keys(doc)
        assert not bad, f"{path.relative_to(ROOT)} contains private keys: {bad[:10]}"


def test_public_html_has_no_odoo_private_field_names():
    for path in PUBLIC_HTML_GLOBS:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert "odoo_id" not in text
        assert "primary_contact_email" not in text
        assert "owner_email" not in text


def test_build_public_data_strips_nexus_internal():
    actors_path = ROOT / "static" / "ecosystem" / "data" / "actors.json"
    raw = json.loads(actors_path.read_text(encoding="utf-8"))
    raw_text = json.dumps(raw)
    assert FORBIDDEN_KEY_PATTERN.search(raw_text) is None
    assert '"internal"' not in raw_text
