# Odoo CA1 — CLP26 company & founder import drafts

**Status:** DRAFT ONLY — no Odoo import, API, or live-system writes until Gideon approves.

Files in this folder:

| File | Purpose |
|------|---------|
| `odoo-CA1-companies.csv` | `res.partner` companies (8 CLP26 startups) |
| `odoo-CA1-founders.csv` | Placeholder founder contacts (`TBD (LinkedIn)`) |

Deck PDFs were not present locally (`/workspace/climate-kic/decks/*.pdf` missing); company copy was rewritten from the brief’s `copy_draft` excerpts only.

---

## Gaps and flags by startup

### aura-cell — Aura Cell (GT)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty (not in brief JSON). |
| Corporate fields | vat, street, city, phone empty — not printed in deck excerpts. |
| `industry_id` | Left empty — Odoo industry mapping not specified in brief. |
| `country_id` | Set to `GT` — confirm against your Odoo `res.country` import convention (code vs name vs external id). |
| Taxonomy | Deck **CT-BU-005** (ct2 **CT-EN-007**); wiki lists **CT-EN-007** — **wiki vs deck DISAGREE** (ct1 from table used in `category_id`). |
| ct2 | Not stored on company row (column not in schema); secondary code **CT-EN-007** Energy Efficiency Buildings. |

### autogenerado-629 — MUKAN (GT)

| Gap / flag | Detail |
|------------|--------|
| **NAME** | Moodle slug `autogenerado-629`; deck brand **MUKAN** used as `name`. Import id remains `__import__.clp26_autogenerado_629`. |
| Website | Empty. |
| Corporate fields | All empty in excerpts. |
| `industry_id` | Empty. |
| `country_id` | `GT` — verify format. |
| Taxonomy | Deck **CT-IN-003** (ct2 **CT-AF-009**); wiki **CT-IN-004** — **DISAGREE**. |

### ecomuna — Ecomuna (CR)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty. |
| Corporate fields | All empty in excerpts. |
| `industry_id` | Empty. |
| `country_id` | `CR` — verify format. |
| Taxonomy | Deck **CT-IN-003**; wiki **CT-XS-004** — **DISAGREE**. |
| ct2 | Empty in startup table. |

### fazzty — Fazzty (CR)

| Gap / flag | Detail |
|------------|--------|
| Website | **Left empty** — brief JSON had `imarcgroup.com/latin` (market-research source in deck, not startup site). |
| Corporate fields | All empty. |
| `industry_id` | Empty. |
| `country_id` | `CR` — verify format. |
| Taxonomy | Deck/wiki agree on **CT-TR-001** (ct2 **CT-TR-005**). |
| Wiki page | Title path includes “not-assigned-unknown”; ct1 is assigned in source table. |

### gmoves — GMOVES (GT)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty. |
| Corporate fields | All empty (team names on deck slides **not** imported per HITL). |
| `industry_id` | Empty. |
| `country_id` | `GT` — verify format. |
| Taxonomy | Deck **CT-WA-003** (ct2 **CT-AF-001**); wiki **CT-AF-009** — **DISAGREE**. |

### ingenicrop — Ingenicrop (GT)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty. |
| Email | **info@ingenicrop.ai** — present in deck excerpt (company contact, not founder row). |
| Phone, vat, street, city | Empty in excerpts. |
| `industry_id` | Empty. |
| `country_id` | `GT` — verify format. |
| Taxonomy | Deck/wiki agree **CT-AF-007** (ct2 **CT-IC-005**). |
| Founders | Team names on deck **not** imported; founder CSV remains TBD (LinkedIn). |

### nrk — NRK (GT)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty (deck mentions @NRK__OFICIAL — social handle, not imported as website). |
| Corporate fields | All empty. |
| `industry_id` | Empty. |
| `country_id` | `GT` — verify format. |
| Taxonomy | Deck **CT-EX-038** (ct2 **CT-WA-003**); wiki **CT-IN-004** — **DISAGREE**. |

### plastic-free-planet — Plastic Free Planet (CR)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty. |
| Corporate fields | All empty. |
| `industry_id` | Empty. |
| `country_id` | `CR` — verify format. |
| Taxonomy | Deck/wiki agree **CT-WA-003**; ct2 empty in table. |

---

## Global flags

- **`category_id` format:** Values are `CLP26,<ct1>` (e.g. `CLP26,CT-BU-005`). Confirm tag/category records exist in Odoo before import.
- **`industry_id`:** Unmapped for all rows — needs Odoo-side taxonomy link if required.
- **YouTube / pitch video:** Not in CSV columns; leave empty when added elsewhere; use **@cleantechhub273** only (never cleantechhubcolombia1668).
- **Dedupe:** Before import, search existing `res.partner` for name/website duplicates. Example from brief: **CurubaTech** contact **522** shows founder contacts may already exist — same check needed for these eight companies and any future founder imports from LinkedIn.

---

## HITL checklist (before any Odoo import)

- [ ] Gideon approval on draft CSV content and naming (especially **MUKAN** vs Moodle slug).
- [ ] Dedupe pass against live Odoo partners (companies + contacts).
- [ ] Confirm `country_id` import format (`GT` / `CR` vs full country name / external id).
- [ ] Confirm `CLP26` and each `CT-*` tag exists; create missing tags if policy allows.
- [ ] Resolve **wiki vs deck** taxonomy disagreements (or document accepted ct1 for CRM).
- [ ] Map `industry_id` if mandatory on company records.
- [ ] Re-read deck PDFs when available to validate copy and any printed vat/street/city/phone/email.
- [ ] Founder import **only** after LinkedIn sourcing — do not fill from decks, Moodle, or Odoo.
- [ ] Import companies first, then founder placeholders (or skip founder import until real names).
- [ ] Post-import spot-check: 8 companies, 8 TBD contacts, categories applied.

---

*Generated for Climate Launchpad 2026 (CLP26) Odoo CA1 — CSV draft only.*
