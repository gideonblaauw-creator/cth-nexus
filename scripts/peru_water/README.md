# Peru water open-data (light SQLite)

Private VPS dataset at `/opt/peru-water/peru_water.db` with raw downloads under `/opt/peru-water/raw/`. **Not exposed** via Caddy or any public HTTP endpoint.

## Schema (SQLite)

| Table | Purpose |
|-------|---------|
| `sources` | Catalog row per publisher dataset (status, license, `fetched_at`, `row_count`) |
| `raw_files` | SHA-256 of each downloaded blob under `raw/` |
| `stations` | Normalized monitoring / hydromet stations (codes, ubigeo, lat/lon) |
| `observations` | Time-series samples (SENAMHI; capped) |
| `utility_indicators` | SUNASS utility/tariff/emergency metrics; ANA faja segments (sampled) |
| `access_by_region` | Regional access proxies (SUNASS emergency coverage; INEI ENAPRES P307) |

## Refresh (idempotent)

From a **pushed** git branch checkout on the VPS:

```bash
sudo mkdir -p /opt/peru-water/raw
sudo chown -R "$USER" /opt/peru-water   # or run as deploy user with write access
cd /path/to/cth-nexus
python3 -m scripts.peru_water.refresh --db /opt/peru-water/peru_water.db --raw-dir /opt/peru-water/raw
```

Environment knobs:

| Variable | Default | Meaning |
|----------|---------|---------|
| `PERU_WATER_SENAMHI_MAX_ROWS` | `250000` | Cap hydromet observation inserts |
| `PERU_WATER_ANA_FAJA_MAX_ROWS` | `75000` | Cap ANA faja marginal CSV rows |
| `PERU_WATER_ENAPRES_MAX_ROWS` | `200000` | Cap ENAPRES microdata rows scanned |
| `PERU_WATER_REQUEST_DELAY` | `1.0` | Seconds between HTTP downloads |

## Proposed cron (not installed)

Weekly Sunday 04:15 America/Lima, after datosabiertos/SENAMHI typical updates:

```cron
15 4 * * 0 cd /opt/cth-nexus && /usr/bin/python3 -m scripts.peru_water.refresh >> /var/log/peru-water-refresh.log 2>&1
```

Use the actual deploy path and user; keep logs rotated.

## Sources

See `catalog.py` for URLs, licenses, and skipped viewer-only endpoints (SNIRH dashboard, GeoSNIRH timeout, SENAMHI portal HTML, MVCS WAF).

## Disk budget

Target &lt; 2 GB total. Large national CSVs are **sampled** (ANA fajas, SENAMHI series). Re-run refresh safely; downloads are reused when SHA matches path.
