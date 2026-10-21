"""Runtime paths for Peru water open-data DB (VPS layout)."""
from __future__ import annotations

import os
from pathlib import Path

DB_PATH = Path(os.environ.get("PERU_WATER_DB", "/opt/peru-water/peru_water.db"))
RAW_DIR = Path(os.environ.get("PERU_WATER_RAW", "/opt/peru-water/raw"))
REPO_ROOT = Path(__file__).resolve().parents[2]

# Disk budget guardrails
MAX_RAW_BYTES = int(os.environ.get("PERU_WATER_MAX_RAW_BYTES", str(2 * 1024**3 - 200 * 1024**2)))
SENAMHI_MAX_ROWS = int(os.environ.get("PERU_WATER_SENAMHI_MAX_ROWS", "250000"))
ANA_FAJA_MAX_ROWS = int(os.environ.get("PERU_WATER_ANA_FAJA_MAX_ROWS", "75000"))
ENAPRES_MAX_ROWS = int(os.environ.get("PERU_WATER_ENAPRES_MAX_ROWS", "200000"))

REQUEST_DELAY_SEC = float(os.environ.get("PERU_WATER_REQUEST_DELAY", "1.0"))
USER_AGENT = os.environ.get(
    "PERU_WATER_USER_AGENT",
    "CleantechHUB-PeruWaterDB/1.0 (+https://github.com/gideonblaauw-creator/cth-nexus; research)",
)
