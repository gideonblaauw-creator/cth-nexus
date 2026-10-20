import time
import logging
import re

from api.handlers.bookstack import BookStackClient
from api.mentoring.models import Startup, SessionStatus, MODULES, COUNTRY_FLAGS

log = logging.getLogger("cth-mentor-api.mentoring")

_cache = {"startups": None, "ts": 0}
CACHE_TTL = 300  # 5 minutes

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = BookStackClient()
    return _client


def _extract_tag(tags, name):
    for t in tags:
        if t.get("name", "").lower() == name.lower():
            return t.get("value", "")
    return ""


def _first_sentence(html):
    text = re.sub(r"<[^>]+>", "", html or "")
    text = re.sub(r"\s+", " ", text).strip()
    match = re.match(r"^(.{40,}?[.!?])\s", text)
    if match:
        return match.group(1)
    return text[:200] + ("..." if len(text) > 200 else "")


def _build_sessions():
    return [
        SessionStatus(
            module_number=m["number"],
            name=m["name"],
            status="needs_mentor",
        ).to_dict()
        for m in MODULES
    ]


def _page_to_startup(page_data):
    tags = page_data.get("tags", [])
    country = _extract_tag(tags, "country") or "Unknown"
    name = page_data.get("name", "")
    description_html = page_data.get("html", "") or page_data.get("description", "")

    return Startup(
        page_id=page_data["id"],
        name=name,
        country=country,
        flag=COUNTRY_FLAGS.get(country, ""),
        category=_extract_tag(tags, "category") or _extract_tag(tags, "ct_taxonomy") or "",
        stage=_extract_tag(tags, "stage") or "",
        description=description_html,
        oneliner=_first_sentence(description_html),
        wiki_url=f"https://wiki.cleantechhub.net/books/idea-browser/page/{page_data.get('slug', '')}",
        app_id=_extract_tag(tags, "app_id") or "",
        founder=_extract_tag(tags, "founder") or "",
        sessions=_build_sessions(),
        matched_mentors=[],
        needs_mentor=list(range(1, 9)),
    )


def get_selected_startups(force_refresh=False):
    now = time.time()
    if not force_refresh and _cache["startups"] is not None and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["startups"]

    client = _get_client()
    log.info("Fetching selected CLP26 startups from BookStack")

    try:
        pages = client.list_pages_by_tag("selected", "clp26")
    except Exception:
        log.exception("Failed to fetch startups from BookStack")
        if _cache["startups"] is not None:
            return _cache["startups"]
        return []

    startups = []
    for page_summary in pages:
        try:
            page_detail = client.get_page(page_summary["id"])
            startups.append(_page_to_startup(page_detail))
        except Exception:
            log.warning("Failed to fetch page %s", page_summary.get("id"))

    startups.sort(key=lambda s: (s.country, s.name))

    _cache["startups"] = startups
    _cache["ts"] = now
    log.info("Cached %d selected startups", len(startups))
    return startups


def get_startup_detail(page_id):
    client = _get_client()
    try:
        page = client.get_page(page_id)
    except Exception:
        log.exception("Failed to fetch page %s", page_id)
        return None

    tags = page.get("tags", [])
    is_selected = any(
        t.get("name") == "selected" and t.get("value") == "clp26"
        for t in tags
    )
    if not is_selected:
        return None

    return _page_to_startup(page)


def get_homework(module_number):
    client = _get_client()
    try:
        pages = client.list_pages_by_tag("module", str(module_number))
        if pages:
            page = client.get_page(pages[0]["id"])
            return {
                "module": module_number,
                "title": page.get("name", ""),
                "html": page.get("html", ""),
                "url": f"https://wiki.cleantechhub.net/books/clp26-workbook/page/{page.get('slug', '')}",
            }
    except Exception:
        log.warning("Homework for module %d not found", module_number)
    return None
