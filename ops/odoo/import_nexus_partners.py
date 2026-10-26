#!/usr/bin/env python3
"""Import Nexus ecosystem actors and investors into Odoo res.partner (companies only).

Dry run by default. Writes Odoo and Nexus only with --apply.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import xmlrpc.client
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[2]
ACTORS_RAW = REPO / "static" / "ecosystem" / "data" / "actors.raw.json"
INVESTORS = REPO / "site" / "investors" / "data" / "investors.json"
INVESTOR_ODOO_MAP = REPO / "ops" / "odoo" / "investor_odoo_ids.json"
PLAN_CSV = REPO / "ops" / "odoo" / "import_plan.csv"
SUMMARY_JSON = REPO / "ops" / "odoo" / "import_summary.json"

GENERIC_HOSTS = frozenset(
    {
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "twitter.com",
        "x.com",
        "linktr.ee",
        "youtube.com",
    }
)

COUNTRY_CODE = {
    "Peru": "PE",
    "Colombia": "CO",
    "El Salvador": "SV",
    "United States": "US",
    "Netherlands": "NL",
    "Germany": "DE",
    "France": "FR",
    "Spain": "ES",
    "United Kingdom": "GB",
    "Mexico": "MX",
    "México": "MX",
    "Brazil": "BR",
    "Chile": "CL",
    "Argentina": "AR",
    "Canada": "CA",
    "Switzerland": "CH",
    "Sweden": "SE",
    "Norway": "NO",
    "Denmark": "DK",
    "Belgium": "BE",
    "Italy": "IT",
    "Portugal": "PT",
    "India": "IN",
    "Singapore": "SG",
    "Australia": "AU",
    "Japan": "JP",
    "China": "CN",
    "South Africa": "ZA",
}

def host_key(url: str | None) -> str | None:
    if not url or not isinstance(url, str) or not url.strip():
        return None
    u = url.strip()
    if not u.startswith("http"):
        u = f"https://{u}"
    try:
        h = urlparse(u).netloc.lower().replace("www.", "")
        if not h or h in GENERIC_HOSTS:
            return None
        return h
    except Exception:
        return None


def norm_name(s: str | None) -> str:
    if not s:
        return ""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def load_odoo_env() -> dict[str, str]:
    keys = (
        "ODOO_URL",
        "ODOO_BASE_URL",
        "ODOO_DB",
        "ODOO_USERNAME",
        "ODOO_USER",
        "ODOO_PASSWORD",
    )
    env = {k: (os.environ.get(k) or "").strip() for k in keys}
    url = env["ODOO_URL"] or env["ODOO_BASE_URL"]
    user = env["ODOO_USERNAME"] or env["ODOO_USER"]
    if not url or not env["ODOO_DB"] or not user or not env["ODOO_PASSWORD"]:
        raise RuntimeError(
            "Missing Odoo credentials. Load via Infisical (cth-agents / prod): "
            "ODOO_URL or ODOO_BASE_URL, ODOO_DB, ODOO_USERNAME or ODOO_USER, ODOO_PASSWORD"
        )
    return {
        "url": url.rstrip("/"),
        "db": env["ODOO_DB"],
        "user": user,
        "password": env["ODOO_PASSWORD"],
    }


@dataclass
class NexusRow:
    nexus_id: str
    row_type: str  # actor | investor
    name: str
    website: str | None
    country: str | None
    existing_odoo_id: int | None


@dataclass
class PlanRow:
    nexus_id: str
    row_type: str
    name: str
    action: str  # create | update | skip
    matched_odoo_id: str
    reason: str


class OdooClient:
    def __init__(self, cfg: dict[str, str]) -> None:
        self.cfg = cfg
        common = xmlrpc.client.ServerProxy(
            f"{cfg['url']}/xmlrpc/2/common", allow_none=True
        )
        uid = common.authenticate(cfg["db"], cfg["user"], cfg["password"], {})
        if not uid:
            raise RuntimeError("Odoo authentication failed")
        self.uid = uid
        self.models = xmlrpc.client.ServerProxy(
            f"{cfg['url']}/xmlrpc/2/object", allow_none=True
        )
        self._country_cache: dict[str, int] = {}

    def execute(self, model: str, method: str, *args, **kwargs):
        return self.models.execute_kw(
            self.cfg["db"],
            self.uid,
            self.cfg["password"],
            model,
            method,
            list(args),
            kwargs,
        )

    def country_id(self, country_name: str | None) -> int | False:
        if not country_name:
            return False
        if country_name in self._country_cache:
            return self._country_cache[country_name]
        code = COUNTRY_CODE.get(country_name)
        if code:
            rec = self.execute(
                "res.country",
                "search_read",
                [[("code", "=", code)]],
                fields=["id"],
                limit=1,
            )
            if rec:
                cid = rec[0]["id"]
                self._country_cache[country_name] = cid
                return cid
        rec = self.execute(
            "res.country",
            "search_read",
            [[("name", "ilike", country_name)]],
            fields=["id"],
            limit=1,
        )
        if rec:
            cid = rec[0]["id"]
            self._country_cache[country_name] = cid
            return cid
        return False

    def fetch_company_partners(self) -> list[dict]:
        return self.execute(
            "res.partner",
            "search_read",
            [[("is_company", "=", True)]],
            fields=["id", "name", "website", "is_company"],
            limit=0,
        )

    def create_company(self, values: dict) -> int:
        # Odoo 18 XML-RPC create workaround (see app/cth-nexus/api/handlers/odoo.py)
        name = values.get("name") or "Nexus import"
        result = self.execute("res.partner", "name_create", name)
        partner_id = result[0]
        self.execute("res.partner", "write", [partner_id], values)
        return partner_id

    def write_partner(self, partner_id: int, values: dict) -> None:
        self.execute("res.partner", "write", [partner_id], values)


def load_nexus_rows() -> list[NexusRow]:
    rows: list[NexusRow] = []
    actors = json.loads(ACTORS_RAW.read_text(encoding="utf-8"))
    for a in actors:
        if a.get("type") != "org":
            continue
        internal = (a.get("nexus") or {}).get("internal") or {}
        existing = internal.get("odoo_id")
        rows.append(
            NexusRow(
                nexus_id=a["id"],
                row_type="actor",
                name=(a.get("name") or "").strip(),
                website=a.get("website"),
                country=a.get("country"),
                existing_odoo_id=int(existing) if existing else None,
            )
        )

    inv_doc = json.loads(INVESTORS.read_text(encoding="utf-8"))
    inv_map: dict[str, int] = {}
    if INVESTOR_ODOO_MAP.exists():
        inv_map = {
            str(k): int(v)
            for k, v in json.loads(INVESTOR_ODOO_MAP.read_text(encoding="utf-8")).items()
        }
    for inv in inv_doc.get("investors") or []:
        iid = inv.get("id")
        if iid is None:
            continue
        rows.append(
            NexusRow(
                nexus_id=f"investor-{iid}",
                row_type="investor",
                name=(inv.get("name") or "").strip(),
                website=inv.get("website"),
                country=inv.get("country") or (inv.get("geo_tags") or [None])[0],
                existing_odoo_id=inv_map.get(str(iid)),
            )
        )
    return rows


def build_partner_indexes(partners: list[dict]) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    by_host: dict[str, list[int]] = defaultdict(list)
    by_name: dict[str, list[int]] = defaultdict(list)
    for p in partners:
        pid = p["id"]
        hk = host_key(p.get("website"))
        if hk:
            by_host[hk].append(pid)
        nm = norm_name(p.get("name"))
        if nm:
            by_name[nm].append(pid)
    return by_host, by_name


def pick_match(
    row: NexusRow,
    by_host: dict[str, list[int]],
    by_name: dict[str, list[int]],
) -> tuple[int | None, str]:
    hk = host_key(row.website)
    if hk:
        ids = by_host.get(hk, [])
        if len(ids) == 1:
            return ids[0], "matched website domain"
        if len(ids) > 1:
            return None, f"ambiguous domain {hk} ({len(ids)} partners)"
    nm = norm_name(row.name)
    if nm:
        ids = by_name.get(nm, [])
        if len(ids) == 1:
            return ids[0], "matched normalized name"
        if len(ids) > 1:
            return None, f"ambiguous name ({len(ids)} partners)"
    return None, "no Odoo match"


def partner_values(row: NexusRow, odoo: OdooClient) -> dict:
    website = row.website or ""
    if website and not website.startswith("http"):
        website = f"https://{website}"
    vals: dict = {
        "name": row.name,
        "is_company": True,
        "company_type": "company",
    }
    if website:
        vals["website"] = website
    cid = odoo.country_id(row.country)
    if cid:
        vals["country_id"] = cid
    tag = f"Nexus {row.row_type} {row.nexus_id}"
    vals["comment"] = tag[:500]
    return vals


def plan_import(rows: list[NexusRow], partners: list[dict]) -> list[PlanRow]:
    by_host, by_name = build_partner_indexes(partners)
    partner_by_id = {p["id"]: p for p in partners}
    plan: list[PlanRow] = []
    for row in rows:
        if not row.name:
            plan.append(
                PlanRow(row.nexus_id, row.row_type, "", "skip", "", "missing name")
            )
            continue
        match_id, reason = pick_match(row, by_host, by_name)
        if match_id is None and reason.startswith("ambiguous"):
            plan.append(
                PlanRow(row.nexus_id, row.row_type, row.name, "skip", "", reason)
            )
            continue
        if match_id is None:
            plan.append(
                PlanRow(
                    row.nexus_id,
                    row.row_type,
                    row.name,
                    "create",
                    "",
                    reason,
                )
            )
            continue
        if row.existing_odoo_id == match_id:
            plan.append(
                PlanRow(
                    row.nexus_id,
                    row.row_type,
                    row.name,
                    "skip",
                    str(match_id),
                    "already linked",
                )
            )
            continue
        if row.existing_odoo_id and row.existing_odoo_id != match_id:
            plan.append(
                PlanRow(
                    row.nexus_id,
                    row.row_type,
                    row.name,
                    "skip",
                    str(match_id),
                    f"conflict: nexus has odoo_id {row.existing_odoo_id}, match {match_id}",
                )
            )
            continue
        partner = partner_by_id.get(match_id, {})
        if not partner.get("is_company"):
            plan.append(
                PlanRow(
                    row.nexus_id,
                    row.row_type,
                    row.name,
                    "skip",
                    str(match_id),
                    "matched partner is not a company",
                )
            )
            continue
        plan.append(
            PlanRow(
                row.nexus_id,
                row.row_type,
                row.name,
                "update",
                str(match_id),
                reason,
            )
        )
    return plan


def write_plan_csv(plan: list[PlanRow]) -> None:
    PLAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PLAN_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "nexus_id",
                "type",
                "name",
                "action",
                "matched_odoo_id",
                "reason",
            ]
        )
        for p in plan:
            w.writerow(
                [
                    p.nexus_id,
                    p.row_type,
                    p.name,
                    p.action,
                    p.matched_odoo_id,
                    p.reason,
                ]
            )


def summarize(plan: list[PlanRow]) -> dict:
    counts = {"create": 0, "update": 0, "skip": 0}
    ambiguous: list[str] = []
    for p in plan:
        counts[p.action] = counts.get(p.action, 0) + 1
        if p.action == "skip" and p.reason.startswith("ambiguous"):
            ambiguous.append(p.nexus_id)
    return {
        "total": len(plan),
        "create": counts["create"],
        "update": counts["update"],
        "skip": counts["skip"],
        "ambiguous_nexus_ids": ambiguous,
        "ambiguous_count": len(ambiguous),
    }


def apply_nexus_odoo_ids(plan: list[PlanRow]) -> None:
    actors = json.loads(ACTORS_RAW.read_text(encoding="utf-8"))
    inv_map: dict[str, int] = {}
    if INVESTOR_ODOO_MAP.exists():
        inv_map = {
            str(k): int(v)
            for k, v in json.loads(INVESTOR_ODOO_MAP.read_text(encoding="utf-8")).items()
        }

    actor_updates: dict[str, int] = {}
    for p in plan:
        if p.action not in ("create", "update") or not p.matched_odoo_id:
            continue
        oid = int(p.matched_odoo_id)
        if p.row_type == "actor":
            actor_updates[p.nexus_id] = oid
        elif p.row_type == "investor" and p.nexus_id.startswith("investor-"):
            inv_map[p.nexus_id.split("-", 1)[1]] = oid

    for a in actors:
        oid = actor_updates.get(a.get("id", ""))
        if not oid:
            continue
        nexus = dict(a.get("nexus") or {})
        internal = dict(nexus.get("internal") or {})
        internal["odoo_id"] = oid
        nexus["internal"] = internal
        a["nexus"] = nexus

    ACTORS_RAW.write_text(
        json.dumps(actors, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    INVESTOR_ODOO_MAP.parent.mkdir(parents=True, exist_ok=True)
    INVESTOR_ODOO_MAP.write_text(
        json.dumps(inv_map, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def apply_odoo(plan: list[PlanRow], odoo: OdooClient, rows_by_id: dict[str, NexusRow]) -> None:
    partners = odoo.fetch_company_partners()
    by_host, by_name = build_partner_indexes(partners)

    for p in plan:
        row = rows_by_id[p.nexus_id]
        if p.action == "skip":
            continue
        if p.action == "update":
            pid = int(p.matched_odoo_id)
            odoo.write_partner(pid, partner_values(row, odoo))
            continue
        if p.action == "create":
            match_id, _ = pick_match(row, by_host, by_name)
            if match_id:
                p.matched_odoo_id = str(match_id)
                p.action = "update"
                odoo.write_partner(match_id, partner_values(row, odoo))
                continue
            pid = odoo.create_company(partner_values(row, odoo))
            p.matched_odoo_id = str(pid)
            partners.append({"id": pid, "name": row.name, "website": row.website, "is_company": True})
            hk = host_key(row.website)
            if hk:
                by_host[hk].append(pid)
            nm = norm_name(row.name)
            if nm:
                by_name[nm].append(pid)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write to Odoo and internal Nexus odoo_id fields (requires sign-off).",
    )
    args = parser.parse_args()

    if not ACTORS_RAW.is_file():
        print(f"Missing {ACTORS_RAW}", file=sys.stderr)
        return 1
    if not INVESTORS.is_file():
        print(f"Missing {INVESTORS}", file=sys.stderr)
        return 1

    try:
        cfg = load_odoo_env()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 2

    rows = load_nexus_rows()
    rows_by_id = {r.nexus_id: r for r in rows}
    odoo = OdooClient(cfg)
    partners = odoo.fetch_company_partners()
    plan = plan_import(rows, partners)

    if args.apply:
        apply_odoo(plan, odoo, rows_by_id)
        apply_nexus_odoo_ids(plan)

    write_plan_csv(plan)
    summary = summarize(plan)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(
        f"Import plan: create={summary['create']} update={summary['update']} "
        f"skip={summary['skip']} ambiguous={summary['ambiguous_count']}"
    )
    print(f"Wrote {PLAN_CSV.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
