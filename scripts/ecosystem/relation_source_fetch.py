"""Shared fetch + verbatim quote helpers for ecosystem relation verification."""
from __future__ import annotations

import io
import re
import ssl
import time
import urllib.error
import urllib.request
from http.client import IncompleteRead
from typing import Any

import certifi
from bs4 import BeautifulSoup

UA = "CleantechHUB-Nexus-Ecosystem/1.0 (ops@cleantechhub.net)"
CTX = ssl.create_default_context(cafile=certifi.where())


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def collapse_for_match(s: str) -> str:
    return norm_ws(s).lower()


def quote_in_body(evidence: str, body: str) -> bool:
    if not evidence:
        return False
    return collapse_for_match(evidence) in collapse_for_match(body)


def fetch_body(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_err: Exception | None = None
    data = b""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60, context=CTX) as resp:
                data = resp.read()
            last_err = None
            break
        except (urllib.error.URLError, TimeoutError, OSError, IncompleteRead) as exc:
            last_err = exc
            time.sleep(1.5 * (attempt + 1))
    if last_err is not None:
        raise last_err
    if url.lower().endswith(".pdf") or data[:4] == b"%PDF":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    soup = BeautifulSoup(data, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)


ORG_PREFIX_STOPWORDS = frozenset(
    {
        "grupo",
        "programa",
        "ministerio",
        "superintendencia",
        "autoridad",
        "fundación",
        "fundacion",
        "policy",
    }
)


def name_tokens(label: str) -> list[str]:
    label = re.sub(r"[^\w\sáéíóúñüÁÉÍÓÚÑÜ&–-]", " ", label, flags=re.I)
    parts = [p for p in label.split() if len(p) > 2]
    while len(parts) > 1 and parts[0].lower() in ORG_PREFIX_STOPWORDS:
        parts = parts[1:]
    return parts


def actor_name_variants(name: str) -> list[str]:
    """Shorter display names that often appear in source pages."""
    if not name:
        return []
    variants = [name.strip()]
    for sep in ("–", "-", "("):
        if sep in name:
            variants.append(name.split(sep)[0].strip())
    if "(" in name:
        inner = name.split("(", 1)[1].rstrip(")").strip()
        if inner:
            variants.append(inner)
    # de-dupe preserving order
    out: list[str] = []
    for v in variants:
        if v and v not in out:
            out.append(v)
    return out


def label_matches_text(text: str, label: str) -> bool:
    if not label:
        return False
    tl = collapse_for_match(text)
    tl_compact = tl.replace(" ", "")
    for variant in actor_name_variants(label):
        vc = collapse_for_match(variant).replace(" ", "")
        if len(vc) >= 4 and vc in tl_compact:
            return True
        tokens = name_tokens(variant)
        if not tokens:
            continue
        hits = sum(1 for t in tokens if collapse_for_match(t) in tl)
        need = 2 if len(tokens) >= 2 else 1
        if hits >= need:
            return True
    return False


def names_in_text(text: str, *labels: str) -> bool:
    for label in labels:
        if label and not label_matches_text(text, label):
            return False
    return bool(labels)


CHALLENGE_TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "challenge:PE-2-agua": (
        "agua",
        "hídric",
        "hidric",
        "riego",
        "cuenca",
        "residual",
        "saneamiento",
    ),
    "challenge:PE-1-bosques": (
        "bosque",
        "amazón",
        "amazon",
        "forest",
        "conservación",
        "conservacion",
        "biodiversidad",
    ),
}


def challenge_topic_in_evidence(challenge_id: str, evidence: str) -> bool:
    ev = collapse_for_match(evidence)
    keys = CHALLENGE_TOPIC_KEYWORDS.get(challenge_id, ())
    if not keys:
        return True
    return any(k in ev for k in keys)


def challenge_topic(challenge_id: str, story: dict[str, Any]) -> str:
    meta = (story.get("challenges") or {}).get(challenge_id) or {}
    en = meta.get("label", {}).get("en") or ""
    es = meta.get("label", {}).get("es") or ""
    return en or es or challenge_id
