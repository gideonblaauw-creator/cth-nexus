# IMD Peru CTH alumni archive — change log (2026-09-24)

Agent lane: Nexus read-only curation → Archive write only (no git, no PR, no deploy).

## Summary

Created HITL curated set for **IMD (Lausanne)** coaching list: Peru-based startups with **verified CTH program** participation.

| Metric | Count |
|--------|------:|
| **Curated** | 17 |
| **Shareable** | 16 |
| **Hold** | 1 |

## Composition

- **16 × CLP 2026** — Odoo 18 `res.partner`, `country_id=Peru`, `x_clp_cohort=CLP 2026`, `x_program_status=activo` (2026-09-24 XML-RPC pull via `/opt/sustenttia/v2/.env`).
- **1 × Hub Perú** — **Cirkula** (BookStack Idea Browser page 2952; program evidence from Epic Angels archive + Hub Perú portfolio chapter; **not** in Odoo CLP 2026 PE set).

## Exclusions (by design)

- **~101** Nexus catalog pages tagged `country=Peru` were **not** bulk-imported — no Odoo/Hub/REIN/CLP program tag → excluded per criteria.
- Older Hub Perú / REIN / GIZ alumni **not** added without a second verified program source (BookStack Hub portfolio search hit HTTP 429 during run).

## Hold

| Startup | Reason |
|---------|--------|
| HardTech | Page live (BookStack 834 → **HardTech · Clean Industry**); **`shareable: false`** until HITL promote — not on `?imd_pe=1` |

### H4 gap — HardTech (2026-09-24)

- Renamed BookStack page **834** from long CLP headline to **HardTech · Clean Industry** (`hardtech-clean-industry`); tags app_id 6404, founder, CLP26 Peru chapter.
- Odoo partner **492** re-verified (`x_startup_name` HardTech, CLP 2026, Peru).
- Archive `curated.json`: `nexus_url` → `https://nexus.cleantechhub.net/ideas/hardtech-clean-industry`; stage/taxonomy filled.
- Detail: `Archive/imd-peru-cth-20260924/h4-hardtech.md`
- Cleared Next.js fetch cache only (no `nexus-ideas.service` restart).

## Sources touched (read-only)

- Odoo XML-RPC
- Nexus API `http://127.0.0.1:3010/ideas/api/ideas`
- BookStack page 2952 (Cirkula tags)
- `/opt/nexus-idea-browser/src/data/epic-angels-curated.json`
- `/opt/nexus-idea-browser/Archive/epic-angels-20250918/*`

## Writes

Only: `/opt/nexus-idea-browser/Archive/imd-peru-cth-20260924/` (`criteria.md`, `curated.json`, `CHANGES.md`).
