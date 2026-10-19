"""SHACL validation service for cth:FieldDataQuality shapes.
Runs on port 8012. Called by the ingest endpoint before writing to origo.db.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="CTH SHACL Validator", version="1.1")

AGRO_CLASSES = (
    "bosque_fragmentado",
    "agroforesteria",
    "cafe_sombra",
    "sistemas_agroforestales",
    "vegetacion_secundaria",
)


class FieldDataSubmission(BaseModel):
    gps_decimal_places: int
    ideam_raster_months_old: int
    iot_calibration_days_old: Optional[int] = None
    gps_lock_seconds: Optional[int] = None
    methodology_id: str
    ideam_land_cover_class: Optional[str] = None
    jrc_mapping_status: Optional[str] = None


SHAPES = {
    "cth:GpsPrecision": {
        "field": "gps_decimal_places",
        "min": 6,
        "message": "GPS precision must be ≥6 decimal places (EUDR Article 9 parcel identification)",
    },
    "cth:DeforestationDataVintage": {
        "field": "ideam_raster_months_old",
        "max": 24,
        "message": "IDEAM deforestation raster must be ≤24 months old",
    },
    "cth:IotCalibration": {
        "field": "iot_calibration_days_old",
        "max": 180,
        "message": "IoT sensor calibration certificate must be ≤180 days old",
        "optional": True,
    },
    "cth:AndeanGpsLock": {
        "field": "gps_lock_seconds",
        "min": 90,
        "message": "GPS lock wait must be ≥90 seconds per polygon vertex (Andean terrain multipath)",
        "optional": True,
    },
}


class ValidationIssue(BaseModel):
    shape: str
    severity: str
    message: str
    value: Optional[str | int] = None


class ValidationResult(BaseModel):
    valid: bool
    violations: list[dict]
    warnings: list[dict] = []
    shape_count: int = 5


def check_agroforestry(data: dict) -> list[dict]:
    issues = []
    land_cover = data.get("ideam_land_cover_class")
    jrc_status = data.get("jrc_mapping_status")

    if land_cover and land_cover in AGRO_CLASSES:
        issues.append({
            "shape": "origo:AgroforestryCanopyShape",
            "severity": "Warning",
            "message": "Land cover class indicates potential agroforestry system. "
                       "Manual canopy verification required before DDS submission. "
                       "See Origo agroforestry protocol.",
            "value": land_cover,
        })

    if jrc_status == "disputed":
        issues.append({
            "shape": "origo:AgroforestryCanopyShape/jrc",
            "severity": "Violation",
            "message": "JRC polygon status is disputed. Resolve boundary before DDS submission.",
            "value": jrc_status,
        })

    return issues


@app.post("/validate", response_model=ValidationResult)
def validate(submission: FieldDataSubmission):
    violations = []
    warnings = []
    data = submission.model_dump()

    for shape_id, shape in SHAPES.items():
        value = data.get(shape["field"])
        if value is None and shape.get("optional"):
            continue
        if value is None:
            violations.append({"shape": shape_id, "message": f"Missing required field: {shape['field']}"})
            continue
        if "min" in shape and value < shape["min"]:
            violations.append({"shape": shape_id, "message": shape["message"], "value": value})
        if "max" in shape and value > shape["max"]:
            violations.append({"shape": shape_id, "message": shape["message"], "value": value})

    agro_issues = check_agroforestry(data)
    for issue in agro_issues:
        if issue["severity"] == "Violation":
            violations.append(issue)
        else:
            warnings.append(issue)

    return ValidationResult(
        valid=len(violations) == 0,
        violations=violations,
        warnings=warnings,
        shape_count=5,
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "cth-shacl-validator", "shapes": 5}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8012)
