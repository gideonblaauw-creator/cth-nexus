# Odoo CO4 import drafts (CLP26) — DRAFT / HITL

**Status:** CSV-only draft for human review. **Do not import into Odoo** until Gideon approves and a dedupe pass is run against existing `res.partner` records (founder contacts may already exist — e.g. CurubaTech contact id 522).

**Target:** Odoo 18 `res.partner` import  
**Files:** `odoo-CO4-companies.csv`, `odoo-CO4-founders.csv`

---

## Gaps and flags by startup

### `proyecto-impacto-ambiental` — Proyecto emprendedor con impacto ambiental

| Item | Status |
|------|--------|
| Website | Missing (empty in source JSON) |
| VAT / street / city / email / phone | Empty (not printed in deck excerpts provided) |
| Deck | Drive id `1j2zlPXFyUPZJqj_zhvvgO2MA66ZQAb_e` |
| Taxonomy ct1 / ct2 | `CT-EN-010` (Biomass & Biogas) / `CT-WW-002` (Organic Waste & Composting) — ct2 not in company CSV columns; confirm mapping in Odoo |
| **FLAG** | Deck header text references **República Dominicana**; source table lists country **CO** — `country_id` set to `base.co` per table; verify before import |
| **FLAG** | Deck excerpts mention product mix variants (e.g. 40/35/25 vs 70/30 in problem slide) — comment uses deal-line facts only |
| Founders | Placeholder only (`TBD (LinkedIn)`) |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/proyecto-emprendedor-con-impacto-ambiental-clean-energy

---

### `sie-waka` — SIÉ WAKA

| Item | Status |
|------|--------|
| Website | Missing |
| VAT / street / city / email / phone | Empty |
| Deck | Drive id `1aoVRX80JvOK8shJQQUXF9kIKSkN0gGrB` |
| Taxonomy ct1 / ct2 | `CT-WW-001` (Water Access & Treatment) / `CT-IC-001` (Satellite & Deforestation Monitoring) |
| **FLAG** | **Wiki vs deck taxonomy disagree:** wiki `CT-WW-003` vs deck/table `CT-WW-001` — CSV uses table ct1 per brief |
| **FLAG** | Sparse deck OCR in source JSON — company comment is minimal; enrich from full deck PDF at HITL |
| Founders | Placeholder only |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/sie-waka-water

---

### `terra-io` — Terra IO

| Item | Status |
|------|--------|
| Website | Missing |
| VAT / street / city / email / phone | Empty |
| Deck | Drive id `1zLssjXlPVroBKkAian6FHOERDNfXBunp` |
| Taxonomy ct1 / ct2 | `CT-IC-005` (Precision Ag & Smart Grid) / `CT-AF-007` (Precision Agri Data) — wiki agrees with deck |
| **FLAG** | Deck market/beachhead text references **Jalisco, México** — country still **CO** in source table |
| Founders | Placeholder only |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/terra-io-food-agriculture

---

### `sekpos` — SEKPOS

| Item | Status |
|------|--------|
| Website | Missing |
| VAT / street / city / email / phone | Empty |
| Deck | **NO DECK** in Drive — no Drive file id |
| Taxonomy | **Taxonomy pending** — table ct1 `UNASSIGNED (unknown)`; `category_id` left empty; wiki-only hint `CT-IC-004` **not** used as ct1 (do not invent) |
| Company comment | No deck-backed description possible |
| Founders | Placeholder only |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/sekpos-clean-industry

Source flags: `NO_DECK`, `TAXONOMY_UNKNOWN`

---

## Import assumptions (verify in Odoo)

- `country_id`: `base.co` (Colombia external id — confirm matches your Odoo database).
- `industry_id`: left empty (no mapping provided in brief).
- `category_id`: program tag format `"CLP26,<ct1>"` where ct1 is assigned; empty for SEKPOS pending taxonomy.
- External ids: `__import__.clp26_<slug_with_underscores>` for companies; founder rows use `__import__.clp26_<slug>_founder`.
- YouTube / pitch video fields: not in these CSVs; leave empty when added elsewhere (`@cleantechhub273` only — never `cleantechhubcolombia1668`).

---

## HITL checklist (before any Odoo import)

- [ ] Gideon approval to import CLP26 batch
- [ ] Dedupe search in Odoo for company names and `__import__.clp26_*` ids
- [ ] Dedupe founder contacts (LinkedIn pass still required; check existing contacts e.g. CurubaTech id 522 pattern)
- [ ] Resolve **SIÉ WAKA** wiki vs deck ct1 (`CT-WW-003` vs `CT-WW-001`)
- [ ] Resolve **SEKPOS** taxonomy and obtain deck or approved wiki-only copy
- [ ] Confirm **country CO** vs deck geography (Proyecto impacto ambiental / Terra IO market slides)
- [ ] Confirm `CLP26,<ct1>` category tags exist in Odoo
- [ ] Review company `comment` paragraphs against full deck PDFs in Drive
- [ ] LinkedIn-only founder enrichment; replace `TBD (LinkedIn)` rows
- [ ] No import from this PR until all blockers cleared

---

*Generated as draft CSV only — no Odoo API, UI, or live system writes.*
