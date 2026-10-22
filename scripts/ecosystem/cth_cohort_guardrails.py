"""Guardrails for proprietary CTH cohort evidence (Gideon decision 25, 22 Oct 2026).

A cth_cohort row may skip the live verbatim-quote fetch only when all three hold:
the programme is CTH-run, the row has no personal email, phone, or home address,
and any money or pilot outcome has consent_ref. Otherwise the row fails.
"""
from __future__ import annotations

import re
from typing import Any

EVIDENCE_TYPE_PUBLIC = "public_quote"
EVIDENCE_TYPE_COHORT = "cth_cohort"

MONEY_RELATION_TYPES = frozenset({"funding", "cofunds", "funds_layer"})
MONEY_KEYS = frozenset(
    {
        "amount",
        "money",
        "grant",
        "grant_amount",
        "funding_amount",
        "investment",
        "investment_amount",
        "ticket",
        "award",
        "award_amount",
    }
)
PILOT_KEYS = frozenset({"pilot", "pilot_outcome"})
TEXT_KEYS = frozenset({"evidence", "source_title", "note", "notes", "summary", "outcome"})

EMAIL_KEYS = frozenset({"email", "e-mail", "mail"})
PHONE_KEYS = frozenset({"phone", "telephone", "tel", "mobile", "celular", "whatsapp"})
ADDRESS_KEYS = frozenset(
    {
        "address",
        "home_address",
        "street",
        "street_address",
        "domicilio",
        "direccion",
        "dirección",
        "residencia",
    }
)
# Structural ids and the page URL are not contact details. source_url is scanned
# for an embedded email only.
SKIP_PII_KEYS = frozenset(
    {"source", "target", "type", "evidence_type", "programme", "source_url"}
)

EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE_PLUS_RE = re.compile(r"\+\s?\d[\d\s().-]{7,}\d")
PHONE_AREA_RE = re.compile(r"\(\d{2,4}\)\s*\d{3}")
PHONE_GROUP_RE = re.compile(r"\b\d{2,4}(?:[\s.-]\d{2,4}){1,4}\b")
HOME_RE = re.compile(
    r"(?i)(?:\b(?:calle|carrera|cra|avenida|avda|av|jiron|jirón|jr|pasaje)\.?\s+\d"
    r"|\b\d{1,5}\s+(?:calle|carrera|avenida|street|st\.?|avenue|ave\.?)\b"
    r"|\b(?:apto|apartamento|departamento)\s*\.?\s*\d"
    r"|\bhome address\b|\bdomicilio\b)"
)
MONEY_RE = re.compile(
    r"(?i)(?:(?:usd|us\$|eur|cop|pen|gbp)\s?\d|[$£€]\s?\d|s/\s?\d"
    r"|\b\d[\d.,]*\s*(?:usd|eur|dólares|dolares|soles)\b)"
)
PILOT_RE = re.compile(
    r"(?i)\bpilot(?:o| outcome)?\b|\bprueba piloto\b|\bresultado del piloto\b"
)


def evidence_type_of(row: dict[str, Any] | None, default: str = EVIDENCE_TYPE_PUBLIC) -> str:
    if not row:
        return default
    raw = row.get("evidence_type")
    if raw is None:
        return default
    if isinstance(raw, str) and not raw.strip():
        return default
    return str(raw).strip()


def programme_ids_from_config(config: dict[str, Any]) -> set[str]:
    found: set[str] = set()
    for item in config.get("programmes") or []:
        if isinstance(item, str) and item.strip():
            found.add(item.strip())
        elif isinstance(item, dict):
            pid = str(item.get("id") or "").strip()
            if pid:
                found.add(pid)
    for pid in config.get("programme_ids") or []:
        text = str(pid).strip()
        if text:
            found.add(text)
    return found


def _nonempty(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _looks_like_phone(text: str) -> bool:
    if PHONE_PLUS_RE.search(text) or PHONE_AREA_RE.search(text):
        return True
    for match in PHONE_GROUP_RE.finditer(text):
        start, end = match.span()
        left = start
        while left > 0 and text[left - 1] not in " \t\n,;:":
            left -= 1
        right = end
        while right < len(text) and text[right] not in " \t\n,;:":
            right += 1
        token = text[left:right].strip(".,")
        # Ids such as consent-2026-014 contain letters; ISO dates are not phone numbers.
        if re.search(r"[A-Za-z]", token) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", token):
            continue
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) < 7:
            continue
        parts = re.split(r"[\s.-]", match.group(0))
        last = parts[-1]
        if len(digits) < 10 and last.isdigit() and 1900 <= int(last) <= 2099:
            continue
        return True
    return False


def personal_contact_kinds(row: dict[str, Any]) -> list[str]:
    """Return 'email', 'phone', and/or 'home address' when the row carries them."""
    found: list[str] = []
    seen: set[str] = set()

    def add(kind: str) -> None:
        if kind not in seen:
            seen.add(kind)
            found.append(kind)

    def walk(value: Any, key: str | None) -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                walk(child, str(child_key))
            return
        if isinstance(value, list):
            for child in value:
                walk(child, key)
            return
        if not isinstance(value, str):
            return
        text = value.strip()
        if not text or key in SKIP_PII_KEYS:
            if key == "source_url" and text and EMAIL_RE.search(text):
                add("email")
            return
        key_norm = (key or "").casefold()
        if key_norm in EMAIL_KEYS or EMAIL_RE.search(text):
            add("email")
        if key_norm in PHONE_KEYS or _looks_like_phone(text):
            add("phone")
        if key_norm in ADDRESS_KEYS or HOME_RE.search(text):
            add("home address")

    walk(row, None)
    return found


def _text_needs_consent(text: str) -> bool:
    return bool(MONEY_RE.search(text) or PILOT_RE.search(text))


def payload_needs_consent(obj: dict[str, Any]) -> bool:
    if str(obj.get("type") or "") in MONEY_RELATION_TYPES:
        return True
    for key, value in obj.items():
        if key in MONEY_KEYS and _nonempty(value):
            return True
        if key in PILOT_KEYS and _nonempty(value):
            return True
        if key in TEXT_KEYS and isinstance(value, str) and _text_needs_consent(value):
            return True
    return False


def _ref(value: Any) -> str:
    return str(value or "").strip()


def missing_consent(row: dict[str, Any]) -> bool:
    """True when money or a pilot outcome is present without consent_ref."""
    row_ref = _ref(row.get("consent_ref"))
    if payload_needs_consent(row) and not row_ref:
        return True
    outcomes = row.get("outcomes")
    if not isinstance(outcomes, list):
        return False
    for item in outcomes:
        if isinstance(item, dict):
            if payload_needs_consent(item) and not (_ref(item.get("consent_ref")) or row_ref):
                return True
        elif isinstance(item, str) and _text_needs_consent(item) and not row_ref:
            return True
    return False


def programme_failure(row: dict[str, Any], programme_ids: set[str]) -> str | None:
    allowed = {pid.casefold() for pid in programme_ids}
    explicit = _ref(row.get("programme"))
    if explicit:
        if explicit.casefold() not in allowed:
            return f"programme {explicit!r} is not a CTH-run programme"
        return None
    endpoints = [_ref(row.get("source")), _ref(row.get("target"))]
    if any(endpoint.casefold() in allowed for endpoint in endpoints if endpoint):
        return None
    return "programme is not a CTH-run programme"


def cth_cohort_blockers(row: dict[str, Any], programme_ids: set[str]) -> list[str]:
    """Reasons the row may not skip the live quote fetch. Empty means the skip is allowed."""
    reasons: list[str] = []
    programme = programme_failure(row, programme_ids)
    if programme:
        reasons.append(programme)
    kinds = personal_contact_kinds(row)
    if kinds:
        reasons.append("row has personal " + ", ".join(kinds))
    if missing_consent(row):
        reasons.append("money or pilot outcome requires consent_ref")
    return reasons
