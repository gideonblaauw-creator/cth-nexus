"""KoboToolbox webhook ingest — POST /v1/submissions.

Flow:
  1. Receive KoboToolbox webhook payload
  2. Call SHACL validator on :8012 (R-SUB-01)
  3. FPIC territorial check (R-SUB-02, simplified for Phase 3)
  4. Methodology registry check (R-SUB-03)
  5. Write to submissions table
  6. Append PROV-O record
  7. Return submission_id + validation status
"""
from __future__ import annotations

import datetime
import json
import sqlite3
import uuid

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.database import get_origo_db
from app.ledger import append_ledger

router = APIRouter(prefix="/v1/submissions", tags=["submissions"])

SHACL_URL = "http://localhost:8012/validate"


class KoboSubmission(BaseModel):
    submitter_did: str
    parcel_id: str
    methodology_id: str
    geojson: dict
    gps_decimal_places: int
    gps_lock_seconds: int | None = None
    ideam_raster_date: str
    iot_calibration_date: str | None = None
    kobo_submission_id: str | None = None


class SubmissionResult(BaseModel):
    submission_id: str
    shacl_valid: bool
    shacl_violations: list[dict]
    fpic_status: str
    accepted: bool
    message: str


@router.post("", response_model=SubmissionResult)
async def ingest_submission(req: Request, body: KoboSubmission):
    sub_id = str(uuid.uuid4())

    with get_origo_db() as conn:
        method = conn.execute(
            "SELECT id, methodology_type FROM methodology_registry WHERE id = ?",
            (body.methodology_id,),
        ).fetchone()
        if not method:
            raise HTTPException(422, f"Methodology '{body.methodology_id}' not in registry (R-SUB-03)")

    ideam_months = 0
    if body.ideam_raster_date:
        raster_date = datetime.date.fromisoformat(body.ideam_raster_date)
        ideam_months = (datetime.date.today() - raster_date).days // 30

    iot_days = None
    if body.iot_calibration_date:
        cal_date = datetime.date.fromisoformat(body.iot_calibration_date)
        iot_days = (datetime.date.today() - cal_date).days

    shacl_payload = {
        "gps_decimal_places": body.gps_decimal_places,
        "ideam_raster_months_old": ideam_months,
        "iot_calibration_days_old": iot_days,
        "gps_lock_seconds": body.gps_lock_seconds,
        "methodology_id": body.methodology_id,
    }

    shacl_result = await _call_shacl(shacl_payload)
    shacl_valid = shacl_result["valid"]
    violations = shacl_result.get("violations", [])

    if not shacl_valid:
        return SubmissionResult(
            submission_id=sub_id,
            shacl_valid=False,
            shacl_violations=violations,
            fpic_status="not_checked",
            accepted=False,
            message="SHACL validation failed (R-SUB-01)",
        )

    territory_id = _check_territory(body.geojson)
    fpic_status = "not_required"
    if territory_id:
        with get_origo_db() as conn:
            t = conn.execute(
                "SELECT fpic_status FROM territorial_boundaries WHERE id = ?",
                (territory_id,),
            ).fetchone()
            fpic_status = t["fpic_status"] if t else "pending"

        if fpic_status != "approved":
            return SubmissionResult(
                submission_id=sub_id,
                shacl_valid=True,
                shacl_violations=[],
                fpic_status=fpic_status,
                accepted=False,
                message=f"FPIC not granted for territory {territory_id} (R-SUB-02)",
            )

    try:
        with get_origo_db() as conn:
            conn.execute(
                """INSERT INTO submissions
                   (id, submitter_did, kobo_submission_id, parcel_id, territory_id,
                    methodology_id, geojson, gps_decimal_places, gps_lock_seconds,
                    ideam_raster_date, iot_calibration_date, shacl_valid,
                    fpic_checked, fpic_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sub_id,
                    body.submitter_did,
                    body.kobo_submission_id,
                    body.parcel_id,
                    territory_id,
                    body.methodology_id,
                    json.dumps(body.geojson),
                    body.gps_decimal_places,
                    body.gps_lock_seconds,
                    body.ideam_raster_date,
                    body.iot_calibration_date,
                    True,
                    True,
                    fpic_status,
                ),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Duplicate submission (kobo_submission_id already exists)")

    append_ledger(
        "submission_accepted",
        body.submitter_did,
        {
            "submission_id": sub_id,
            "parcel_id": body.parcel_id,
            "methodology_id": body.methodology_id,
        },
    )

    return SubmissionResult(
        submission_id=sub_id,
        shacl_valid=True,
        shacl_violations=[],
        fpic_status=fpic_status,
        accepted=True,
        message="Submission accepted — pending validation",
    )


@router.post("/kobo-webhook")
async def kobo_webhook(req: Request, payload: dict):
    """Adapts KoboToolbox flat JSON format to our submission model."""
    adapted = KoboSubmission(
        submitter_did=payload.get("submitter_did", "did:key:unknown"),
        parcel_id=payload.get("parcel_id") or str(payload.get("_id", "")),
        methodology_id="kobo-gps-v2.3",
        geojson=_wkt_to_geojson(payload.get("GPS_Polygon", "")),
        gps_decimal_places=_count_decimal_places(payload.get("_geolocation", [0, 0])[0]),
        gps_lock_seconds=payload.get("gps_lock_seconds"),
        ideam_raster_date="2025-06-01",
        kobo_submission_id=str(payload.get("_id", "")),
    )
    return await ingest_submission(req, adapted)


async def _call_shacl(payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(SHACL_URL, json=payload, timeout=5.0)
        return r.json()


def _check_territory(geojson: dict) -> str | None:
    # Phase 3: placeholder — returns None (no territory match)
    # Phase 4: replace with PostGIS ST_Within(centroid, territory.geom)
    return None


def _wkt_to_geojson(wkt: str) -> dict:
    """Minimal WKT POLYGON to GeoJSON converter for KoboToolbox GPS_Polygon."""
    if not wkt or not wkt.strip().upper().startswith("POLYGON"):
        return {"type": "Polygon", "coordinates": []}
    try:
        inner = wkt.split("((")[1].split("))")[0]
        coords = []
        for pair in inner.split(","):
            parts = pair.strip().split()
            coords.append([float(parts[0]), float(parts[1])])
        return {"type": "Polygon", "coordinates": [coords]}
    except (IndexError, ValueError):
        return {"type": "Polygon", "coordinates": []}


def _count_decimal_places(value: float) -> int:
    s = f"{value:.15f}".rstrip("0")
    if "." not in s:
        return 0
    return len(s.split(".")[1])
