# APC share list — verified websites only

**Rule:** Only startups with `shareable: true` (HTTP 200/3xx company site, not social/parking) go on the APC-facing list. **Do not email APC** until Gideon approves.

## Counts (2025-09-18)

| Metric | Value |
|--------|-------|
| Total curated | 17 |
| **APC shareable** | **3** |
| Internal only (`shareable: false`) | 14 |

## Shareable startups

| Startup | Verified URL | HTTP |
|---------|--------------|------|
| CurubaTech | https://curuba.tech/en/ | 200 |
| Amazóniko | https://www.amazoniko.com/ | 200 |
| e.WAI | https://e-ray.lat/e-wai/ | 200 |

## Not shareable (examples)

| Startup | Reason |
|---------|--------|
| AgroData Connect | linktr.ee (aggregator) |
| Cupainatá. Labranza Sagrada | Instagram only |
| Chum Chum, Cirkula, NUX | No website on record |
| 11 others | No website on BookStack / CLP26 |

## Files

- Machine list: `apc-share-list.json`
- Full verification log: `website-verification-report.json`
- Re-run: `python3 /opt/nexus-idea-browser/scripts/verify_epic_websites.py`

## Epic filter UI

- `?epic=1` shows **all 17** curated matches (internal + APC).
- Green **Verified site** badge = APC-shareable subset.
- Sidebar note shows shareable count.
