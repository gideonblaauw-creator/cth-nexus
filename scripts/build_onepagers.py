#!/usr/bin/env python3
"""Build Nexus startup one-pagers from JSON data + shared template."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
TEMPLATE_CSS = ROOT / "onepagers" / "template" / "styles.css"
OUT_REPO = ROOT / "onepagers" / "sites"
OUT_MEDIA = ROOT / "onepagers" / "media"
OUT_ARCHIVE = Path("/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20")
DECK_SOURCE = Path("/opt/claude-files/Projects/Nexus/startup-decks-2026-08-20")


def asset_url(path: str, slug: str) -> str:
    """Resolve ./assets/... to /s/{slug}/assets/... (works without trailing slash)."""
    if not path or path.startswith(("http://", "https://", "/")):
        return path
    rel = path.removeprefix("./")
    return f"/s/{slug}/{rel}"


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def deck_section(d: dict, slug: str) -> str:
    deck = d.get("deck_pdf")
    if not deck:
        return ""
    local_pdf = deck.get("pdf_path") or f"/s/{slug}/deck.pdf"
    bg = asset_url(deck.get("bg", "./assets/bg-deck.jpg"), slug)
    iframe = (
        f'<div class="deck-frame-wrap">'
        f'<embed class="deck-frame" src="{local_pdf}#view=FitH&toolbar=1" '
        f'type="application/pdf" title="{d["name"]} pitch deck">'
        f"</div>"
    )
    fallback = (
        f'<div class="deck-fallback">{bi("Deck not loading?", "¿No carga el deck?")} '
        f'<a href="{local_pdf}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a></div>'
    )
    return (
        f'<div class="sec" style="position:relative;">'
        f'<div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
        f'<div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>'
        f'<div class="sec-header"><div class="sec-num">📄</div>'
        f'<div class="sec-title">{bi("Pitch Deck", "Pitch Deck")}</div><div class="sec-rule"></div></div>'
        f'<div class="deck-note">{bi("Full-size deck preview below. Numbers on this profile match the deck only.", "Vista previa del deck a tamaño completo. Los números en este perfil provienen solo del deck.")}</div>'
        f'<div class="deck-wrap"><div class="deck-panel">{iframe}{fallback}</div>'
        f'<div class="deck-actions">'
        f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a>'
        f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">{bi("Download PDF", "Descargar PDF")}</a>'
        f"</div></div></div><div class=\"accent-bar\"></div>"
    )
