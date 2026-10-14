# Odoo CO2 — CLP26 company + founder import drafts (DRAFT / HITL)

**Status:** CSV drafts only. **No Odoo import has been run.** Requires Gideon's approval before any import.

**Files:**

| File | Purpose |
|------|---------|
| `odoo-CO2-companies.csv` | `res.partner` company rows (7 startups) |
| `odoo-CO2-founders.csv` | Placeholder contact rows (`TBD (LinkedIn)`) linked via `parent_id/id` |

**Branch:** `cursor/clp26-odoo-co2` → PR base `cursor/epic-apc-nexus-cards-4292`

---

## Gaps and flags by startup

### circuito-cero (Circuito Cero)

| Gap / flag | Detail |
|------------|--------|
| Website | Missing in deck JSON (empty) |
| Corporate fields | vat, street, city, email, phone not in deck — left empty |
| `industry_id` | Left empty — Odoo industry mapping not specified in brief |
| `country_id` | Set to `base.co` (Colombia external id) — **verify in target Odoo DB** |
| Taxonomy | ct1 `CT-WA-003`; wiki agrees with deck |
| ct2 | None in brief table |
| Deck | Drive id `13mR0c4dkDRq1TVYAo8e0N1vgfo_EyFru`; local PDF path in JSON not present in repo |
| Pitch video | YouTube left empty per HITL rules |

### clean-sim (Clean Sim by IMIC)

| Gap / flag | Detail |
|------------|--------|
| Website | `Lectureseries.tech` from deck JSON — **confirm URL scheme / spelling (HITL)** |
| Corporate fields | All empty (not in deck) |
| `industry_id` | Empty (mapping TBD) |
| Taxonomy wiki vs deck | **DISAGREE:** wiki `CT-WA-005` vs deck/brief ct1 `CT-WA-003` — CSV uses brief ct1 |
| ct2 | None |
| Deck | Drive id `1AZScp4HQ8DDmHqegDvdKbOf0YpR0UMZD` |

### climatik (CLIMATIK Climate Transition Platform)

| Gap / flag | Detail |
|------------|--------|
| Website | Missing |
| Corporate fields | All empty |
| `industry_id` | Empty |
| Taxonomy wiki vs deck | **DISAGREE:** wiki `CT-AF-010` vs deck ct1 `CT-XS-004` — CSV uses brief ct1 |
| ct2 | `CT-XS-003` (Green Finance) in brief — **not in `category_id` column** (ct1 only per spec); note for Odoo tagging |
| Deck | Drive id `1ne50os0mNJRMjC6bBTGeBLwu1Ubj3Hu7` |

### communitylab (communitylab S.A.S)

| Gap / flag | Detail |
|------------|--------|
| Website | `communitylab.co` (deck JSON) |
| Corporate fields | All empty |
| `industry_id` | Empty |
| **Duplicate risk** | Flag in source JSON: **already in `epic-angels-shareable.json`** — **update existing partner, do not duplicate** |
| Taxonomy wiki vs deck | **DISAGREE:** wiki `CT-XS-008` vs deck ct1 `CT-IN-004` — CSV uses brief ct1 |
| ct2 | `CT-WA-003` (secondary taxonomy — not in `category_id`) |
| Deck | Drive id `17-r1ja_35K3QrKbLr-jwvV1FGfyJDts_` |
| Name casing | Brief uses `communitylab S.A.S`; shareable list uses `CommunityLab` — reconcile on import |

### construyendo-redes-de-paz (Construyendo Redes de Paz)

| Gap / flag | Detail |
|------------|--------|
| Website | Missing |
| Corporate fields | All empty |
| `industry_id` | Empty |
| Taxonomy wiki vs deck | **DISAGREE:** wiki `CT-AF-005` vs deck ct1 `CT-AF-002` — CSV uses brief ct1 |
| ct2 | `CT-IC-003` (Supply Chain Traceability) — not in `category_id` |
| Deck | Drive id `1UE0fZvM5jY1yGfrJTgun-m5r4n-02BAG` |

### dantium (DANTIUM)

| Gap / flag | Detail |
|------------|--------|
| Website | Missing |
| Corporate fields | All empty |
| `industry_id` | Empty |
| Taxonomy wiki vs deck | **DISAGREE:** wiki `CT-BU-001` vs deck ct1 `CT-WA-003` — CSV uses brief ct1 |
| ct2 | `CT-EN-006` (Distributed Generation) — not in `category_id` |
| Deck | Drive id `1U-YYierLCPrYKDel6Lj2wiNdampgLxL5` |

### e-wai (e.WAI)

| Gap / flag | Detail |
|------------|--------|
| Website | Missing in deck JSON (empty) — **other repo files list `e-ray.lat/e-wai`; not used here (deck-only rule)** |
| Corporate fields | All empty |
| `industry_id` | Empty |
| Existing nexus data | Source flag: existing card ct1 `CT-WW-003` agrees with deck |
| **Cross-source note** | `epic-angels-shareable.json` lists different website/theme/stage — reconcile before import |
| ct2 | `CT-IC-004` (Climate Data Platforms) — not in `category_id` |
| Deck | Drive id `10Xi9AAFKp5Eu-UGIgnvSrZH9afJuRnn5` |

---

## Global flags

- **`country_id`:** All rows use `base.co`. Confirm this matches Odoo 18 external IDs on the target instance.
- **`industry_id`:** Intentionally blank; no Odoo industry mapping was provided in the brief.
- **`category_id`:** Format `CLP26,<ct1>` only; secondary ct2 codes are documented above but not imported in this column.
- **Founders:** All contact rows are placeholders; no names, emails, or phones from decks/Odoo/Moodle/Drive.
- **Dedupe:** Before import, search existing `res.partner` records (e.g. CurubaTech-related contact id **522** cited in brief — founder contacts may already exist). Merge or link rather than duplicate.
- **Pitch videos:** YouTube not populated; when added, use **@cleantechhub273** only (never cleantechhubcolombia1668).

---

## HITL checklist (before any Odoo import)

- [ ] Gideon approval obtained
- [ ] Dedupe pass against live Odoo partners (companies + founder contacts)
- [ ] Confirm `base.co` and partner tag/category records `CLP26` + CT-* exist in Odoo
- [ ] Resolve wiki vs deck taxonomy disagreements (7 rows; 5 with DISAGREE)
- [ ] Validate websites (`Lectureseries.tech`, `communitylab.co`) and add missing URLs where approved
- [ ] Map or leave `industry_id` per org convention
- [ ] For **communitylab**, choose update vs new record (shareable list entry exists)
- [ ] LinkedIn pass to replace `TBD (LinkedIn)` founder rows
- [ ] Import companies CSV first, then founders CSV
- [ ] Post-import spot-check: 7 companies + 7 placeholder contacts, categories applied

---

## Import column reference

**Companies:** `id`, `name`, `is_company`, `company_type`, `website`, `country_id`, `industry_id`, `category_id`, `comment`, `vat`, `street`, `city`, `email`, `phone`

**Founders:** `id`, `name`, `parent_id/id`, `function`, `email`, `phone`, `website`, `comment`

External ids: `__import__.clp26_<slug_with_underscores>` (companies); founder ids suffixed with `_founder` (draft convention — **confirm before import**).
