from __future__ import annotations

import hashlib
import json
import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.database import get_origo_db
from app.services.rate_limiter import limiter

router = APIRouter(prefix="/public/eudr", tags=["public-eudr"])

IDEAM_API_BASE = os.getenv("IDEAM_API_BASE", "https://datos.ideam.gov.co/api")
IDEAM_API_KEY = os.getenv("IDEAM_API_KEY")
JRC_API_BASE = os.getenv("JRC_API_BASE", "https://api.globalforestwatch.org/v3")


# ── Pydantic models ─────────────────────────────────────────────────────────────

class PolygonRequest(BaseModel):
    geometry: dict
    commodity: Optional[str] = None
    source_country: Optional[str] = "CO"


class RiskScreenerResponse(BaseModel):
    deforestation_flag: bool
    deforestation_ha: float
    ideam_land_cover_class: Optional[str]
    jrc_mapping_status: str
    agroforestry_risk: str
    risk_summary: str
    next_step: str
    disclaimer: str


class CommodityNode(BaseModel):
    id: str
    name: str
    hs_codes: list[str]
    eudr_covered: bool
    enforcement_date_large: str
    enforcement_date_small: str
    country_risk_class: Optional[str]


# ── TRACK A: Risk Screener ───────────────────────────────────────────────────────

@router.post("/risk-screen")
@limiter.limit("10/day")
async def risk_screen(request: Request, payload: PolygonRequest):
    """
    Free EUDR deforestation risk screening.
    Submit a GeoJSON geometry — returns deforestation and JRC flags.
    Rate limit: 10/day per IP. No DDS generated.
    """
    geometry = payload.geometry
    if geometry.get("type") not in ("Polygon", "MultiPolygon", "Point"):
        raise HTTPException(400, "geometry.type must be Polygon, MultiPolygon, or Point")

    ideam_result = await _query_ideam(geometry)
    deforestation_ha = ideam_result.get("deforestation_ha", 0.0)
    land_cover_class = ideam_result.get("land_cover_class")
    deforestation_flag = deforestation_ha > 0
    jrc_status = await _query_jrc(geometry)
    agro_risk = _agroforestry_risk(land_cover_class)
    _log_screen(deforestation_flag, jrc_status, request.client.host)

    if deforestation_flag:
        summary = f"Deforestation detected: {deforestation_ha:.2f} ha in IDEAM monitoring period (2020-2026)."
        next_cta = "This lot cannot be used in a DDS without remediation. Contact Origo: data.cleantechhub.net/contact"
    elif jrc_status == "disputed":
        summary = "Polygon boundary is disputed in EU JRC reference layer. Manual verification required."
        next_cta = "Origo's certifying agents can resolve disputed boundaries: data.cleantechhub.net/contact"
    else:
        summary = "No deforestation detected in this polygon for the EUDR monitoring period."
        next_cta = "Generate a verified TRACES-ready DDS: data.cleantechhub.net — Starter from €75/DDS"

    return RiskScreenerResponse(
        deforestation_flag=deforestation_flag,
        deforestation_ha=deforestation_ha,
        ideam_land_cover_class=land_cover_class,
        jrc_mapping_status=jrc_status,
        agroforestry_risk=agro_risk,
        risk_summary=summary,
        next_step=next_cta,
        disclaimer=(
            "This screening is indicative only and does not constitute a verified EUDR "
            "Due Diligence Statement. Formal DDS submission requires plot-level verification "
            "by a certified Origo agent. Regulation: EU 2023/1115 + EU 2023/1731."
        ),
    )


async def _query_ideam(geometry: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{IDEAM_API_BASE}/deforestation/intersect",
                headers={"Authorization": f"Bearer {IDEAM_API_KEY}"},
                json={"geometry": geometry, "period": "2020-01-01/2026-01-01"},
            )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {"deforestation_ha": 0.0, "land_cover_class": None}


async def _query_jrc(geometry: dict) -> str:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{JRC_API_BASE}/analysis/loss", json={"geojson": geometry}
            )
        if resp.status_code == 200:
            data = resp.json()
            return "mapped" if data.get("polygon_id") else "no_jrc_match"
    except Exception:
        pass
    return "no_jrc_match"


def _agroforestry_risk(land_cover_class: Optional[str]) -> str:
    if not land_cover_class:
        return "unknown"
    agro_classes = (
        "bosque_fragmentado",
        "agroforesteria",
        "cafe_sombra",
        "sistemas_agroforestales",
        "vegetacion_secundaria",
    )
    if any(c in land_cover_class.lower() for c in agro_classes):
        return "high"
    return "low"


def _log_screen(flagged: bool, jrc_status: str, ip: str) -> None:
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
    try:
        with get_origo_db() as conn:
            conn.execute(
                "INSERT INTO screener_logs (ip_hash, flagged, jrc_status) VALUES (?, ?, ?)",
                (ip_hash, int(flagged), jrc_status),
            )
            conn.commit()
    except Exception:
        pass


# ── TRACK B: Taxonomy endpoints ──────────────────────────────────────────────────

@router.get("/commodities")
@limiter.limit("100/day")
async def list_eudr_commodities(request: Request):
    """
    List all EUDR-covered commodities with HS codes and enforcement dates.
    Rate limit: 100/day per IP.
    Source: Origo Taxonomy synced from EU 2023/1115 Annex I.
    """
    with get_origo_db() as conn:
        rows = conn.execute(
            "SELECT id, label_short, metadata FROM taxonomy_nodes "
            "WHERE json_extract(metadata, '$.eudr_covered') = 'true' "
            "ORDER BY label_short"
        ).fetchall()

    commodities = []
    for row in rows:
        meta = json.loads(row["metadata"] or "{}")
        commodities.append(
            {
                "id": row["id"],
                "name": row["label_short"],
                "hs_codes": meta.get("hs_codes", []),
                "eudr_covered": True,
                "enforcement_date_large": "2026-12-30",
                "enforcement_date_small": "2027-06-30",
                "country_risk_class": meta.get("country_risk_class"),
            }
        )

    return {
        "data": commodities,
        "count": len(commodities),
        "source": "Origo Taxonomy · data.cleantechhub.net",
        "regulation": "EU 2023/1115",
    }


@router.get("/commodities/{commodity}/hs-codes")
@limiter.limit("100/day")
async def get_hs_codes(request: Request, commodity: str):
    """
    HS codes for a specific EUDR commodity.
    Example: GET /public/eudr/commodities/coffee/hs-codes
    Rate limit: 100/day per IP.
    """
    with get_origo_db() as conn:
        row = conn.execute(
            "SELECT id, label_short, metadata FROM taxonomy_nodes "
            "WHERE LOWER(label_short) = LOWER(?) "
            "AND json_extract(metadata, '$.eudr_covered') = 'true'",
            (commodity,),
        ).fetchone()

    if not row:
        raise HTTPException(404, f"Commodity '{commodity}' not found in EUDR taxonomy")

    meta = json.loads(row["metadata"] or "{}")
    return {
        "commodity": row["label_short"],
        "hs_codes": meta.get("hs_codes", []),
        "eudr_covered": True,
        "notes": meta.get("hs_notes", ""),
        "source": "EU 2023/1115 + Origo Taxonomy",
    }


@router.get("/countries")
@limiter.limit("100/day")
async def list_country_risk_classes(request: Request):
    """
    EU EUDR country risk classification.
    Static until EU Commission publishes Art. 29 benchmark list (expected Q4 2026).
    Rate limit: 100/day per IP.
    """
    countries = [
        {
            "country": "Colombia",
            "iso": "CO",
            "risk_class": "standard",
            "key_commodities": ["coffee", "cocoa", "cattle", "palm_oil"],
            "notes": "Standard risk. IDEAM monitoring available via Origo.",
        },
        {
            "country": "Brazil",
            "iso": "BR",
            "risk_class": "standard",
            "key_commodities": ["coffee", "cocoa", "cattle", "soy"],
            "notes": "Standard risk pending EU benchmark publication.",
        },
        {
            "country": "Indonesia",
            "iso": "ID",
            "risk_class": "standard",
            "key_commodities": ["palm_oil", "rubber", "cocoa"],
            "notes": "Standard risk. High plantation-forest overlap.",
        },
        {
            "country": "Peru",
            "iso": "PE",
            "risk_class": "standard",
            "key_commodities": ["coffee", "cocoa"],
            "notes": "Standard risk. Origo expanding via REIN Hubs 2027.",
        },
    ]
    return {
        "data": countries,
        "as_of": "2026-05-28",
        "note": "EU Commission benchmark list pending publication (Art. 29). Origo will update on publication.",
        "source": "EU 2023/1115 + Origo Taxonomy",
    }
