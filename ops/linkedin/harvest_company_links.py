#!/usr/bin/env python3
"""Record LinkedIn company URLs only when the org's own site links to them.

Gideon's rule (22 Oct 2026): never fetch linkedin.com, never log in, never
scrape, never use a search engine. Company pages only (linkedin.com/company/),
not people. For each ecosystem actor, startup, and investor with a website,
fetch the homepage and at most one contact or about page on that same site.
Keep a URL only with linkedin_url, linkedin_cited_from, and linkedin_accessed.
Drop any stored company LinkedIn value that has no citing page.
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import ssl
import sys
import unicodedata
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, HTTPHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "ops" / "linkedin" / "company_links.csv"
CACHE_PATH = Path("/tmp/linkedin-page-cache.json")
ACCESSED = "2026-10-22"
WORKERS = 30
TIMEOUT = 10
MAX_BYTES = 1_200_000

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

SKIP_SLUGS = frozenset(
    {
        "linkedin",
        "wordpress",
        "elementor",
        "wix",
        "squarespace",
        "webflow",
        "shopify",
        "godaddy",
        "joomla",
        "drupal",
        "prestashop",
        "weebly",
        "jimdo",
        "carrd",
        "themeisle",
        "envato",
        "themeforest",
        "automattic",
        "hubspot",
        "mailchimp",
        "constant-contact",
        "google",
        "facebook",
        "instagram",
        "youtube",
        "tiktok",
        "whatsapp",
        "meta",
        "adobe",
        "microsoft",
        "apple",
    }
)

HREF_RE = re.compile(
    r"""href\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\s"'=<>`]+))""",
    re.I,
)
CONTACT_RE = re.compile(
    r"(contact|contacto|kontakt|contate|fale-conosco|get-in-touch|contact-us|contactenos|escr[ií]benos)",
    re.I,
)
ABOUT_RE = re.compile(
    r"(about-us|/about\b|\babout/|quienes-somos|quiénes-somos|/nosotros\b|acerca|sobre-nosotros|who-we-are|our-story|a-propos|/empresa\b)",
    re.I,
)
LINKEDIN_ROW_RE = re.compile(
    r"^(\|\s*LinkedIn\s*\|\s*)([^|\n]*?)(\s*\|)\s*$",
    re.M,
)
BULLET_LI_RE = re.compile(
    r"https?://(?:[\w.-]+\.)?linkedin\.com/company/",
    re.I,
)

class BlockedLinkedIn(Exception):
    """Raised instead of following a redirect onto linkedin.com."""


def is_blocked_host(host: str | None) -> bool:
    if not host:
        return False
    host = host.lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return (
        host == "linkedin.com"
        or host.endswith(".linkedin.com")
        or host == "lnkd.in"
        or host.endswith(".lnkd.in")
        or host == "licdn.com"
        or host.endswith(".licdn.com")
    )


def request_url(url: str) -> str:
    """ASCII request target. Does not follow or rewrite linkedin.com hosts."""
    parts = urlsplit(url)
    host = parts.hostname or ""
    try:
        host_ascii = host.encode("idna").decode("ascii")
    except Exception:
        host_ascii = host
    netloc = host_ascii
    if parts.port:
        netloc = f"{host_ascii}:{parts.port}"
    if parts.username:
        auth = parts.username
        if parts.password:
            auth += ":" + parts.password
        netloc = f"{auth}@{netloc}"
    path = quote(parts.path, safe="/%:@")
    query = quote(parts.query, safe="=&%:+")
    return urlunsplit((parts.scheme, netloc, path, query, ""))


class NoLinkedInRedirect(HTTPRedirectHandler):
    max_redirections = 12

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        loc = request_url(urljoin(req.full_url, newurl))
        if is_blocked_host(urlparse(loc).hostname):
            raise BlockedLinkedIn(loc)
        return super().redirect_request(req, fp, code, msg, headers, loc)


def _opener(verify: bool):
    ctx = ssl.create_default_context() if verify else ssl._create_unverified_context()
    return build_opener(HTTPHandler(), HTTPSHandler(context=ctx), NoLinkedInRedirect())


def site_host(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def same_site(a: str, b: str) -> bool:
    return bool(a and b and site_host(a) == site_host(b))


def normalize_website(raw: str | None) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text or text.upper() in {"PENDIENTE", "N/A", "NA", "NONE", "-", "NULL"}:
        return None
    if text.lower().startswith(("mailto:", "tel:", "javascript:")):
        return None
    if not re.match(r"https?://", text, re.I):
        text = "https://" + text.lstrip("/")
    parts = urlparse(text)
    if not parts.hostname or "." not in parts.hostname:
        return None
    if is_blocked_host(parts.hostname):
        return None
    return text


def canonical_company(slug: str) -> str | None:
    slug = unquote(slug or "").strip().strip("/")
    if not slug or any(ch in slug for ch in " ?#&"):
        return None
    if len(slug) > 120:
        return None
    encoded = quote(slug.lower(), safe="-_.~")
    if not encoded or encoded in {".", ".."}:
        return None
    return f"https://www.linkedin.com/company/{encoded}"


def slug_ok(url: str, name: str) -> bool:
    slug = url.rsplit("/", 1)[-1].lower()
    if slug not in SKIP_SLUGS:
        return True
    compact_name = re.sub(r"[^a-z0-9]+", "", name.lower())
    compact_slug = re.sub(r"[^a-z0-9]+", "", slug)
    return bool(compact_slug) and compact_slug in compact_name


def company_from_href(href: str, base: str) -> str | None:
    href = unescape(href.strip())
    if not href or href.lower().startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    absolute = urljoin(base, href)
    parts = urlparse(absolute)
    if not is_blocked_host(parts.hostname):
        return None
    # Path only. Query-string share links are not company pages.
    match = re.match(r"/company/([^/]+)", parts.path or "", re.I)
    if not match:
        return None
    return canonical_company(match.group(1))


def extract_hrefs(html: str) -> list[str]:
    found: list[str] = []
    for match in HREF_RE.finditer(html):
        href = next(g for g in match.groups() if g)
        found.append(unescape(href.strip()))
    return found


def company_links(html: str, base: str) -> list[tuple[str, int]]:
    ordered: list[tuple[str, int]] = []
    seen: set[str] = set()
    for match in HREF_RE.finditer(html):
        href = next(g for g in match.groups() if g)
        url = company_from_href(href, base)
        if not url or url in seen:
            continue
        seen.add(url)
        ordered.append((url, match.start()))
    return ordered


def choose_company(cands: list[tuple[str, int]], name: str, website: str, html_len: int) -> str | None:
    kept = [(url, pos) for url, pos in cands if slug_ok(url, name)]
    if not kept:
        return None
    host = site_host(website)
    host_token = host.split(".")[0] if host else ""
    name_tokens = set(re.findall(r"[a-z0-9]{3,}", name.lower()))

    def score(url: str, pos: int) -> tuple[int, int, int]:
        slug = unquote(url.rsplit("/", 1)[-1]).lower()
        slug_tokens = set(re.findall(r"[a-z0-9]{3,}", slug))
        points = 5 * len(slug_tokens & name_tokens)
        if host_token and len(host_token) >= 3 and (host_token in slug or slug in host_token):
            points += 8
        footer = 1 if html_len and pos > html_len * 0.55 else 0
        # Higher score wins; footer breaks ties; earlier position is the last tie-break
        # only when scores differ. At equal score, prefer the footer link.
        return (points, footer, -pos if points == 0 else -pos)

    kept.sort(key=lambda item: score(item[0], item[1]), reverse=True)
    return kept[0][0]


def pick_extra(hrefs: list[str], base: str) -> str | None:
    contact: list[str] = []
    about: list[str] = []
    for href in hrefs:
        if not href or href.lower().startswith(("mailto:", "tel:", "javascript:", "#", "data:")):
            continue
        absolute = urljoin(base, href)
        parts = urlparse(absolute)
        if parts.scheme not in {"http", "https"}:
            continue
        if is_blocked_host(parts.hostname) or not same_site(absolute, base):
            continue
        if parts.path.rstrip("/") in {"", "/"}:
            continue
        blob = (parts.path or "") + " " + (parts.query or "")
        if CONTACT_RE.search(blob):
            contact.append(absolute.split("#", 1)[0])
        elif ABOUT_RE.search(blob):
            about.append(absolute.split("#", 1)[0])

    def shortest(urls: list[str]) -> str | None:
        uniq = list(dict.fromkeys(urls))
        if not uniq:
            return None
        uniq.sort(key=lambda u: (urlparse(u).path.count("/"), len(u)))
        return uniq[0]

    return shortest(contact) or shortest(about)


def _decompress(data: bytes, headers) -> bytes:  # noqa: ANN001
    enc = (headers.get("Content-Encoding") or "").lower()
    if "gzip" in enc or data[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(data)
        except Exception:
            return data
    if "deflate" in enc:
        try:
            return zlib.decompress(data)
        except Exception:
            try:
                return zlib.decompress(data, -zlib.MAX_WBITS)
            except Exception:
                return data
    return data


def _decode(data: bytes, headers) -> str:  # noqa: ANN001
    charset = headers.get_content_charset()
    if not charset:
        match = re.search(br"charset=[\"']?([\w.-]+)", data[:2500], re.I)
        charset = match.group(1).decode("ascii", "ignore") if match else "utf-8"
    try:
        return data.decode(charset, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


def fetch_page(url: str) -> dict:
    """GET one page. Never opens a linkedin.com host."""
    req_url = request_url(url)
    host = urlparse(req_url).hostname
    if is_blocked_host(host):
        return {
            "requested": url,
            "final_url": None,
            "error": "blocked_linkedin",
            "company": [],
            "extra": None,
            "html_len": 0,
        }
    last_error = "fetch_failed"
    for verify in (True, False):
        opener = _opener(verify)
        req = Request(
            req_url,
            headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
            },
        )
        try:
            with opener.open(req, timeout=TIMEOUT) as resp:
                final = resp.geturl()
                if is_blocked_host(urlparse(final).hostname):
                    return {
                        "requested": url,
                        "final_url": None,
                        "error": "blocked_linkedin",
                        "company": [],
                        "extra": None,
                        "html_len": 0,
                    }
                status = getattr(resp, "status", 200) or 200
                raw = resp.read(MAX_BYTES)
                headers = resp.headers
            if status < 200 or status >= 300:
                last_error = f"http_{status}"
                break
            data = _decompress(raw, headers)
            ctype = (headers.get("Content-Type") or "").lower()
            if "html" not in ctype and "xml" not in ctype and "text" not in ctype:
                if b"href" not in data[:4000].lower():
                    return {
                        "requested": url,
                        "final_url": final,
                        "error": "not_html",
                        "company": [],
                        "extra": None,
                        "html_len": 0,
                    }
            html = _decode(data, headers)
            hrefs = extract_hrefs(html)
            companies = company_links(html, final)
            return {
                "requested": url,
                "final_url": final,
                "error": None,
                "company": companies,
                "extra": pick_extra(hrefs, final),
                "html_len": len(html),
            }
        except BlockedLinkedIn:
            return {
                "requested": url,
                "final_url": None,
                "error": "blocked_linkedin",
                "company": [],
                "extra": None,
                "html_len": 0,
            }
        except HTTPError as exc:
            last_error = f"http_{exc.code}"
            if exc.code in {400, 401, 403, 404, 410, 451}:
                break
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            last_error = "ssl" if "CERTIFICATE" in str(reason).upper() or "SSL" in str(reason).upper() else "connection"
            if verify and last_error == "ssl":
                continue
            break
        except TimeoutError:
            last_error = "timeout"
            break
        except Exception as exc:  # noqa: BLE001
            if type(exc).__name__ == "TimeoutError" or "timed out" in str(exc).lower():
                last_error = "timeout"
                break
            last_error = type(exc).__name__
            if verify:
                continue
            break
    return {
        "requested": url,
        "final_url": None,
        "error": last_error,
        "company": [],
        "extra": None,
        "html_len": 0,
    }


def slugify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "startup"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def collect_entities() -> list[dict]:
    entities: list[dict] = []
    actors = load_json(ROOT / "static/ecosystem/data/actors.json")
    for actor in actors:
        website = normalize_website(actor.get("website"))
        previous = (actor.get("linkedin") or "").strip()
        if not website and not previous:
            continue
        entities.append(
            {
                "entity_type": "ecosystem_actor",
                "dataset": "ecosystem_actor",
                "entity_id": actor["id"],
                "name": actor.get("name") or actor["id"],
                "website": website or "",
                "previous_linkedin": previous,
            }
        )

    portfolio = load_json(
        ROOT / "site/nexus-assets/previews/startups-redesign-20261016/portfolio-core.json"
    )["startups"]
    seen_slugs: dict[str, int] = {}
    for startup in portfolio:
        website = normalize_website(startup.get("w"))
        if not website:
            continue
        base = slugify(startup.get("n") or "startup")
        seen_slugs[base] = seen_slugs.get(base, 0) + 1
        entity_id = base if seen_slugs[base] == 1 else f"{base}-{seen_slugs[base]}"
        entities.append(
            {
                "entity_type": "startup",
                "dataset": "startup_portfolio",
                "entity_id": entity_id,
                "name": startup.get("n") or entity_id,
                "website": website,
                "previous_linkedin": (startup.get("linkedin_url") or startup.get("linkedin") or "").strip(),
                "match_name": startup.get("n"),
            }
        )

    for path in sorted((ROOT / "onepagers/data").glob("*.json")):
        doc = load_json(path)
        website = normalize_website(doc.get("website") if isinstance(doc.get("website"), str) else None)
        if not website:
            continue
        entities.append(
            {
                "entity_type": "startup",
                "dataset": "startup_onepager",
                "entity_id": doc.get("slug") or path.stem,
                "name": doc.get("name") or path.stem,
                "website": website,
                "previous_linkedin": (doc.get("linkedin_url") or "").strip(),
                "path": str(path.relative_to(ROOT)),
            }
        )

    investors = load_json(ROOT / "site/investors/data/investors.json")["investors"]
    for investor in investors:
        website = normalize_website(investor.get("website"))
        if not website:
            continue
        entities.append(
            {
                "entity_type": "investor",
                "dataset": "investor",
                "entity_id": str(investor.get("id")),
                "name": investor.get("name") or str(investor.get("id")),
                "website": website,
                "previous_linkedin": "",
            }
        )
    return entities


def load_cache() -> dict:
    if CACHE_PATH.is_file():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache), encoding="utf-8")


def fetch_many(urls: list[str], cache: dict) -> None:
    pending = [u for u in urls if u not in cache]
    if not pending:
        return
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(fetch_page, url): url for url in pending}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                cache[url] = fut.result()
            except Exception as exc:  # noqa: BLE001
                cache[url] = {
                    "requested": url,
                    "final_url": None,
                    "error": type(exc).__name__,
                    "company": [],
                    "extra": None,
                    "html_len": 0,
                }
            done += 1
            if done % 50 == 0 or done == len(pending):
                print(f"fetched {done}/{len(pending)}", flush=True)
                save_cache(cache)


def decide(entity: dict, cache: dict) -> dict:
    website = entity["website"]
    row = {
        "entity_type": entity["entity_type"],
        "dataset": entity["dataset"],
        "entity_id": entity["entity_id"],
        "name": entity["name"],
        "website": website,
        "status": "not_found",
        "linkedin_url": "",
        "linkedin_cited_from": "",
        "linkedin_accessed": "",
        "previous_linkedin": entity.get("previous_linkedin") or "",
        "note": "",
        "alt_linkedin_urls": "",
    }
    if not website:
        row["note"] = "no_website"
        return row
    home = cache.get(website)
    if not home:
        row["note"] = "not_fetched"
        return row
    cands = [(item[0], item[1]) for item in home.get("company") or []]
    html_len = home.get("html_len") or 0
    cited = home.get("final_url") or website
    note = home.get("error") or ""
    if not cands:
        extra = home.get("extra")
        if extra and extra != website and not is_blocked_host(urlparse(extra).hostname):
            second = cache.get(extra)
            if second:
                cands = [(item[0], item[1]) for item in second.get("company") or []]
                html_len = second.get("html_len") or 0
                if cands:
                    cited = second.get("final_url") or extra
                    note = ""
                elif not note:
                    note = second.get("error") or "no_company_href"
            else:
                note = note or "extra_not_fetched"
        elif not note:
            note = "no_company_href"
    chosen = choose_company(cands, entity["name"], website, html_len) if cands else None
    if chosen:
        if is_blocked_host(urlparse(cited).hostname):
            row["note"] = "citing_page_was_linkedin"
            return row
        alts = [url for url, _pos in cands if url != chosen]
        row.update(
            {
                "status": "found",
                "linkedin_url": chosen,
                "linkedin_cited_from": cited,
                "linkedin_accessed": ACCESSED,
                "note": note if note and note != "no_company_href" else "",
                "alt_linkedin_urls": " ".join(alts),
            }
        )
        return row
    row["note"] = note or "no_company_href"
    return row


def write_csv(rows: list[dict]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "entity_type",
        "dataset",
        "entity_id",
        "name",
        "website",
        "status",
        "linkedin_url",
        "linkedin_cited_from",
        "linkedin_accessed",
        "previous_linkedin",
        "removed",
        "note",
        "alt_linkedin_urls",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            removed = "yes" if row["previous_linkedin"] and not row["linkedin_url"] else "no"
            writer.writerow({**row, "removed": removed})


def _place_fields(record: dict, fields: dict, prefer: tuple[str, ...]) -> dict:
    """Insert citation fields beside the existing LinkedIn or website key."""
    old_keys = list(record.keys())
    for key in fields:
        record.pop(key, None)
    insert_at = len(record)
    for pref in prefer:
        if pref not in old_keys:
            continue
        insert_at = sum(1 for key in old_keys[: old_keys.index(pref)] if key in record)
        if pref in record:
            insert_at += 1
        break
    items = list(record.items())
    record.clear()
    record.update(items[:insert_at] + list(fields.items()) + items[insert_at:])
    return record


def _clear_linkedin(record: dict, keys: tuple[str, ...]) -> bool:
    changed = False
    for key in keys:
        if key in record:
            record.pop(key, None)
            changed = True
    return changed


ACTOR_KEYS = ("linkedin", "linkedin_url", "linkedin_cited_from", "linkedin_accessed")
CITATION_KEYS = ("linkedin_url", "linkedin_cited_from", "linkedin_accessed")


def apply_actor_record(record: dict, row: dict | None) -> None:
    if row and row["linkedin_url"]:
        _place_fields(
            record,
            {
                "linkedin": row["linkedin_url"],
                "linkedin_url": row["linkedin_url"],
                "linkedin_cited_from": row["linkedin_cited_from"],
                "linkedin_accessed": row["linkedin_accessed"],
            },
            ("linkedin", "website"),
        )
        return
    _clear_linkedin(record, ACTOR_KEYS)


def apply_citation_only(record: dict, row: dict | None, anchor: str) -> None:
    if row and row["linkedin_url"]:
        _place_fields(
            record,
            {
                "linkedin_url": row["linkedin_url"],
                "linkedin_cited_from": row["linkedin_cited_from"],
                "linkedin_accessed": row["linkedin_accessed"],
            },
            (anchor, "website", "w"),
        )
        return
    _clear_linkedin(record, CITATION_KEYS)


def dump_actors(path: Path, data) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, separators=(", ", ": ")) + "\n",
        encoding="utf-8",
    )


def dump_raw(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def apply_actors(rows: list[dict]) -> int:
    by_id = {row["entity_id"]: row for row in rows if row["dataset"] == "ecosystem_actor"}
    changed = 0
    for rel, dumper in (
        ("static/ecosystem/data/actors.json", dump_actors),
        ("static/ecosystem/data/actors.raw.json", dump_raw),
    ):
        path = ROOT / rel
        data = load_json(path)
        for record in data:
            row = by_id.get(record["id"])
            before = (
                record.get("linkedin"),
                record.get("linkedin_url"),
                record.get("linkedin_cited_from"),
                record.get("linkedin_accessed"),
            )
            if row is None and not record.get("linkedin"):
                continue
            apply_actor_record(record, row)
            after = (
                record.get("linkedin"),
                record.get("linkedin_url"),
                record.get("linkedin_cited_from"),
                record.get("linkedin_accessed"),
            )
            if before != after:
                changed += 1
        dumper(path, data)

    cards_path = ROOT / "static/ecosystem/data/actor_cards.json"
    bundle = load_json(cards_path)
    for card in bundle["cards"]:
        row = by_id.get(card["id"])
        if row is None and not card.get("linkedin"):
            continue
        apply_actor_record(card, row)
    cards_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return changed


def update_wiki(rows: list[dict]) -> int:
    by_id = {row["entity_id"]: row for row in rows if row["dataset"] == "ecosystem_actor"}
    wiki = ROOT / "docs/wiki/ecosystem-actors"
    changed = 0
    for path in wiki.glob("*/*.md"):
        if path.name.startswith("TEMPLATE"):
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^actor_id:\s*(\S+)\s*$", text, re.M)
        if not match:
            continue
        actor_id = match.group(1)
        row = by_id.get(actor_id)
        if row is None:
            continue
        original = text
        if row and row["linkedin_url"]:
            if LINKEDIN_ROW_RE.search(text):
                text = LINKEDIN_ROW_RE.sub(
                    lambda m, url=row["linkedin_url"]: f"{m.group(1)}{url}{m.group(3)}",
                    text,
                    count=1,
                )
            text = strip_linkedin_bullets(text)
            text = add_source(text, row["linkedin_cited_from"])
        else:
            if LINKEDIN_ROW_RE.search(text):
                text = LINKEDIN_ROW_RE.sub(
                    lambda m: f"{m.group(1)}PENDIENTE{m.group(3)}",
                    text,
                    count=1,
                )
            text = strip_linkedin_bullets(text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    audit = wiki / "audit.csv"
    if audit.is_file():
        update_audit(audit, by_id)
    return changed


def strip_linkedin_bullets(text: str) -> str:
    lines = text.splitlines(keepends=True)
    kept = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("-", "*")) and BULLET_LI_RE.search(line):
            continue
        kept.append(line)
    return "".join(kept)


def add_source(text: str, url: str) -> str:
    if not url or url in text:
        return text
    bare = url.rstrip("/")
    if bare in text or bare + "/" in text:
        return text
    line = f"- {url}\n"
    heading = re.search(r"^## Fuentes\s*\n", text, re.M)
    if not heading:
        if not text.endswith("\n"):
            text += "\n"
        return text + f"\n## Fuentes\n\n{line}"
    start = heading.end()
    nxt = re.search(r"^## ", text[start:], re.M)
    end = start + nxt.start() if nxt else len(text)
    section = text[start:end].rstrip() + "\n" + line
    if nxt and not section.endswith("\n\n"):
        section += "\n"
    return text[:start] + section + text[end:]


def update_audit(path: Path, by_id: dict[str, dict]) -> None:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    fields = reader.fieldnames or []
    rows = list(reader)
    if "enrich_linkedin" not in fields:
        return
    dirty = False
    for row in rows:
        hit = by_id.get(row.get("actor_id") or "")
        if not hit:
            continue
        new = "FILLED" if hit["linkedin_url"] else "PENDIENTE"
        if row.get("enrich_linkedin") != new:
            row["enrich_linkedin"] = new
            dirty = True
    if not dirty:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)


def apply_portfolio(rows: list[dict]) -> None:
    wanted = {
        (row["name"], site_host(row["website"])): row
        for row in rows
        if row["dataset"] == "startup_portfolio" and row["website"]
    }
    path = ROOT / "site/nexus-assets/previews/startups-redesign-20261016/portfolio-core.json"
    data = load_json(path)
    for startup in data["startups"]:
        website = normalize_website(startup.get("w"))
        if not website:
            continue
        row = wanted.get((startup.get("n"), site_host(website)))
        if row is None:
            continue
        apply_citation_only(startup, row if row["linkedin_url"] else None, "w")
    path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def _insert_onepager_citation(text: str, row: dict) -> str:
    if '"linkedin_url"' in text:
        return text
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    inserted = False
    for line in lines:
        if not inserted and re.search(r'"website"\s*:', line):
            ending = "\n" if line.endswith("\n") else ""
            body = line.rstrip("\r\n")
            if not body.rstrip().endswith(","):
                body = body.rstrip() + ","
            indent = re.match(r"(\s*)", body).group(1)
            out.append(body + ending)
            out.append(
                f'{indent}"linkedin_url": {json.dumps(row["linkedin_url"], ensure_ascii=False)},{ending}'
                f'{indent}"linkedin_cited_from": {json.dumps(row["linkedin_cited_from"], ensure_ascii=False)},{ending}'
                f'{indent}"linkedin_accessed": {json.dumps(row["linkedin_accessed"], ensure_ascii=False)},{ending}'
            )
            inserted = True
            continue
        out.append(line)
    if not inserted:
        return text
    new = "".join(out)
    try:
        json.loads(new)
    except json.JSONDecodeError:
        new = new.replace(
            f'"linkedin_accessed": {json.dumps(row["linkedin_accessed"], ensure_ascii=False)},',
            f'"linkedin_accessed": {json.dumps(row["linkedin_accessed"], ensure_ascii=False)}',
            1,
        )
        json.loads(new)
    return new


def apply_onepagers(rows: list[dict]) -> None:
    by_id = {row["entity_id"]: row for row in rows if row["dataset"] == "startup_onepager"}
    for path in sorted((ROOT / "onepagers/data").glob("*.json")):
        doc = load_json(path)
        slug = doc.get("slug") or path.stem
        row = by_id.get(slug)
        if not row or not row["linkedin_url"]:
            continue
        text = path.read_text(encoding="utf-8")
        new = _insert_onepager_citation(text, row)
        if new != text:
            path.write_text(new, encoding="utf-8")


def apply_investors(rows: list[dict]) -> None:
    by_id = {row["entity_id"]: row for row in rows if row["dataset"] == "investor"}
    path = ROOT / "site/investors/data/investors.json"
    data = load_json(path)
    for investor in data["investors"]:
        row = by_id.get(str(investor.get("id")))
        if row is None:
            continue
        apply_citation_only(investor, row if row["linkedin_url"] else None, "website")
    path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(", ", ": ")),
        encoding="utf-8",
    )


def self_check() -> None:
    html = """
    <a href="https://www.linkedin.com/in/someone">person</a>
    <a href="https://www.linkedin.com/company/elementor">theme</a>
    <a href="https://pe.linkedin.com/company/Bancoldex/">ok</a>
    <a href="/contacto">Contacto</a>
    <a href="https://other.example/contact">off</a>
    """
    base = "https://www.bancoldex.com/"
    links = company_links(html, base)
    assert [url for url, _ in links] == ["https://www.linkedin.com/company/elementor", "https://www.linkedin.com/company/bancoldex"]
    chosen = choose_company(links, "Bancóldex", base, len(html))
    assert chosen == "https://www.linkedin.com/company/bancoldex", chosen
    extra = pick_extra(extract_hrefs(html), base)
    assert extra == "https://www.bancoldex.com/contacto", extra
    assert company_from_href("https://www.linkedin.com/in/someone", base) is None
    assert is_blocked_host("www.linkedin.com")
    assert is_blocked_host("pe.linkedin.com")
    try:
        fetch_page("https://www.linkedin.com/company/bancoldex")
    except Exception as exc:  # noqa: BLE001
        raise AssertionError("blocked URL must not raise") from exc
    blocked = fetch_page("https://www.linkedin.com/company/bancoldex")
    assert blocked["error"] == "blocked_linkedin"
    assert blocked["company"] == []
    print("self-check ok", flush=True)


def main() -> int:
    self_check()
    entities = collect_entities()
    print(f"entities {len(entities)}", flush=True)
    cache = load_cache()
    homepages = sorted({e["website"] for e in entities if e["website"]})
    print(f"homepages {len(homepages)}", flush=True)
    fetch_many(homepages, cache)
    save_cache(cache)
    extras = []
    for url in homepages:
        page = cache.get(url) or {}
        if page.get("company"):
            continue
        extra = page.get("extra")
        if extra and extra not in cache and not is_blocked_host(urlparse(extra).hostname):
            extras.append(extra)
    extras = sorted(set(extras))
    print(f"extra pages {len(extras)}", flush=True)
    fetch_many(extras, cache)
    save_cache(cache)

    leaked = [
        url
        for url, page in cache.items()
        if is_blocked_host(urlparse(url).hostname)
        or is_blocked_host(urlparse(page.get("final_url") or "").hostname)
    ]
    if leaked:
        raise SystemExit(f"refusing to continue; linkedin hosts were fetched: {leaked[:5]}")

    rows = [decide(entity, cache) for entity in entities]
    rows.sort(key=lambda r: (r["entity_type"], r["dataset"], r["entity_id"]))
    write_csv(rows)
    apply_actors(rows)
    wiki_n = update_wiki(rows)
    apply_portfolio(rows)
    apply_onepagers(rows)
    apply_investors(rows)

    found = sum(1 for r in rows if r["status"] == "found")
    not_found = sum(1 for r in rows if r["status"] == "not_found" and r["website"])
    removed = sum(1 for r in rows if r["previous_linkedin"] and not r["linkedin_url"])
    print(
        json.dumps(
            {
                "found": found,
                "not_found": not_found,
                "removed": removed,
                "rows": len(rows),
                "wiki_files": wiki_n,
                "homepages": len(homepages),
                "extra_pages": len(extras),
            },
            indent=2,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
