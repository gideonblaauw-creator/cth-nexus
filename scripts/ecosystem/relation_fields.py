"""Shape rules for ecosystem graph relations.

theme_match is not a field or edge type on relations.json (Gideon, 22 Oct 2026).
Writers call strip_theme_match so a later generate or sync cannot put it back.
Dropping the field does not change public or hidden edge counts.
"""
from __future__ import annotations


def strip_theme_match(relations: list) -> list:
    kept: list = []
    for rel in relations:
        if isinstance(rel, dict) and rel.get("type") == "theme_match":
            continue
        if isinstance(rel, dict) and "theme_match" in rel:
            rel = {k: v for k, v in rel.items() if k != "theme_match"}
        kept.append(rel)
    return kept
