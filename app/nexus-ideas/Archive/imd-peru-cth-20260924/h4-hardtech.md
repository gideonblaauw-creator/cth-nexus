# H4 gap — HardTech (CLP 2026 Peru)

**Date:** 2026-09-24  
**Lane:** B VPS (BookStack write + Archive SoT; no git/PR on this host)

## Odoo `res.partner` (XML-RPC via `/opt/odoo-mcp/.env`)

| Field | Value |
|-------|--------|
| id | 492 |
| name (contact) | Alejandro Suarez Alvites |
| x_startup_name | HardTech |
| x_clp_cohort | CLP 2026 |
| x_program_status | activo |
| country_id | Peru |
| website | (empty) |

No additional founder/website fields on partner record. Email on contact **not** used on public pages.

## BookStack

| Item | Value |
|------|--------|
| Page id | **834** (existing CLP26 Peru chapter page, renamed) |
| Title | HardTech · Clean Industry |
| Slug | `hardtech-clean-industry` |
| Chapter | CLP26 — Peru (625) |
| app_id tag | 6404 |
| ct_taxonomy | CT-IN-003 |
| stage | Prototype |
| founder tag | Alejandro Suarez Alvites |

Prior catalog title was the long CLP application headline (*Processing of single crystal silicon carbide…*). Same app_id 6404; content from CLP application export (`/opt/idea-browser/ideas.json`) + Odoo verified tags. No Drive links.

## Nexus URLs (verification)

| URL | HTTP |
|-----|-----:|
| `https://nexus.cleantechhub.net/ideas?q=HardTech` | 200 |
| `https://nexus.cleantechhub.net/ideas/api/ideas?q=HardTech` | 200 (total 1) |
| `https://nexus.cleantechhub.net/ideas/api/ideas/834` | 200 |
| `https://wiki.cleantechhub.net/books/idea-browser/page/hardtech-clean-industry` | 200 |
| `https://nexus.cleantechhub.net/ideas/hardtech-clean-industry` | **404** (Next app has no per-slug route; same as other curated `nexus_url` slug paths) |

Catalog cache: cleared Next.js `fetch-cache` under `.next/standalone` so search reflects rename without `nexus-ideas.service` restart.

## Archive / IMD

- `curated.json`: `nexus_url` set; `stage` Prototype; `ct_taxonomy` CT-IN-003; **`shareable` remains false**
- **Not** added to `deploy/imd-peru-shareable.json` or live `?imd_pe=1` (count still **16**)

## Fields filled vs [PENDIENTE]

| Field | Status |
|-------|--------|
| startup | HardTech (Odoo + page title) |
| founder | Alejandro Suarez Alvites (Odoo) |
| country / program | PE / CLP 2026 (Odoo) |
| stage | Prototype (CLP application + page tag) |
| ct_taxonomy | CT-IN-003 (page tag) |
| website | empty (Odoo website false; not promoted from application Google Sites URL) |
| elevator pitch / problem / solution | from CLP app_id 6404 (not invented) |

## Blockers / follow-up

- **Slug path 404:** optional future Next.js route or redirect from `/ideas/{slug}` → catalog with drawer open.
- **shareable:** HITL — Gideon to flip `shareable` and regenerate IMD bundle when ready.
