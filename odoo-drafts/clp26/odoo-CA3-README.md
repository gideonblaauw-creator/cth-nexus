# Odoo CA3 import drafts (CLP26) — DRAFT / HITL

**Status:** CSV-only draft for human review. **Do not import into Odoo** until Gideon approves and a dedupe pass is run against existing `res.partner` records (founder contacts may already exist — e.g. CurubaTech contact id 522).

**Target:** Odoo 18 `res.partner` import  
**Files:** `odoo-CA3-companies.csv`, `odoo-CA3-founders.csv`

---

## Gaps and flags by startup

### `agrivoltaic-dragon-fruit` — AgriVoltaic Dragón fruit

| Item | Status |
|------|--------|
| Website | Missing (empty in source JSON) |
| VAT / street / city / email / phone | Empty (no deck; not printed in any provided source) |
| Deck | **NO DECK** in Drive — no Drive file id |
| Taxonomy ct1 / ct2 | **Taxonomy pending** — table ct1 `UNASSIGNED (unknown)`; `category_id` left empty; wiki-only hint `CT-AF-007` **not** used as ct1 |
| Company comment | No deck-backed description possible |
| Stage (source JSON only, not in CSV) | Private Beta — not copied into comment (no deck text) |
| Founders | Placeholder only (`TBD (LinkedIn)`) |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/agrivoltaic-dragon-fruit-food-agriculture

Source flags: `NO_DECK`, `TAXONOMY_UNKNOWN`

---

### `drainalert` — DrainAlert

| Item | Status |
|------|--------|
| Website | Missing |
| VAT / street / city / email / phone | Empty |
| Deck | **NO DECK** in Drive |
| Taxonomy | **Taxonomy pending** — wiki-only hint `CT-BU-004` not imported as ct1 |
| Company comment | No deck-backed description possible |
| Stage (source JSON only) | Ideation |
| Founders | Placeholder only |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/drainalert-clean-industry

Source flags: `NO_DECK`, `TAXONOMY_UNKNOWN`

---

### `nutri-fruits` — Nutri Fruits

| Item | Status |
|------|--------|
| Website | Missing |
| VAT / street / city / email / phone | Empty |
| Deck | **NO DECK** in Drive |
| Taxonomy | **Taxonomy pending** — wiki-only hint `CT-AF-009` not imported as ct1 |
| Company comment | No deck-backed description possible |
| Stage (source JSON only) | Launched |
| Founders | Placeholder only |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/nutri-fruits-food-agriculture

Source flags: `NO_DECK`, `TAXONOMY_UNKNOWN`

---

### `ecolandia` — Ecolandia

| Item | Status |
|------|--------|
| Website | Missing |
| VAT / street / city / email / phone | Empty |
| Deck | **NO DECK** in Drive |
| Taxonomy | **Taxonomy pending** — wiki-only hint `CT-AF-012` not imported as ct1 |
| Company comment | No deck-backed description possible |
| Stage (source JSON only) | Launched |
| Founders | Placeholder only |

Wiki: https://wiki.cleantechhub.net/books/idea-browser/page/ecolandia-food-agriculture

Source flags: `NO_DECK`, `TAXONOMY_UNKNOWN`

---

### `karbonloop` — KarbonLoop

| Item | Status |
|------|--------|
| Website | Missing |
| Country | **Unknown** — `country_id` left empty in CSV |
| VAT / street / city / email / phone | Empty |
| Deck | **NO DECK** in Drive |
| Wiki | **NO_WIKI_PAGE** (no wiki URL in source) |
| Taxonomy | **Taxonomy pending** |
| Company comment | No deck-backed description possible |
| **FLAG** | Not found in Moodle export folders or Idea Browser (per source JSON) |
| Founders | Placeholder only |

Source flags: `NO_DECK`, `TAXONOMY_UNKNOWN`, `NO_WIKI_PAGE`, country unknown

---

### `agrosintex` — Agrosintex

| Item | Status |
|------|--------|
| Website | Missing |
| Country | **Unknown** — `country_id` left empty |
| VAT / street / city / email / phone | Empty |
| Deck | **NO DECK** in Drive |
| Wiki | **NO_WIKI_PAGE** |
| Taxonomy | **Taxonomy pending** |
| Company comment | No deck-backed description possible |
| **FLAG** | Not found in Moodle export folders or Idea Browser (per source JSON) |
| Founders | Placeholder only |

Source flags: `NO_DECK`, `TAXONOMY_UNKNOWN`, `NO_WIKI_PAGE`, country unknown

---

## Batch-level flags

- **All six startups:** no pitch deck in Drive — no deck Drive ids, no deck-derived company descriptions, no invented claims or numbers.
- **All six:** ct1 UNASSIGNED in source table — `category_id` empty; assign taxonomy at HITL before import.
- **Four El Salvador rows:** `country_id` = `base.sv` per source table (confirm external id in your Odoo database).
- **Two rows (KarbonLoop, Agrosintex):** country and wiki page unknown — require manual discovery before import.

---

## Import assumptions (verify in Odoo)

- `country_id`: `base.sv` where country is SV; empty where country is unknown.
- `industry_id`: left empty (no mapping provided in brief).
- `category_id`: program tag format `"CLP26,<ct1>"` when ct1 is assigned; empty while taxonomy pending.
- External ids: `__import__.clp26_<slug_with_underscores>` for companies; founder rows use `__import__.clp26_<slug>_founder`.
- YouTube / pitch video fields: not in these CSVs; leave empty when added elsewhere (`@cleantechhub273` only — never `cleantechhubcolombia1668`).

---

## HITL checklist (before any Odoo import)

- [ ] Gideon approval to import CLP26 CA3 batch
- [ ] Dedupe search in Odoo for company names and `__import__.clp26_*` ids
- [ ] Dedupe founder contacts (LinkedIn pass still required; check existing contacts e.g. CurubaTech id 522 pattern)
- [ ] Obtain decks or approved wiki/Moodle copy for all six; enrich company `comment` from deck facts only
- [ ] Assign official ct1/ct2 for each startup (do not import wiki-only hints as ct1 without approval)
- [ ] Resolve **KarbonLoop** and **Agrosintex** country, wiki/Idea Browser presence, and program eligibility
- [ ] Confirm `base.sv` and any future country external ids match Odoo
- [ ] Confirm `CLP26,<ct1>` category tags exist in Odoo once taxonomy is set
- [ ] LinkedIn-only founder enrichment; replace `TBD (LinkedIn)` rows
- [ ] No import from this PR until all blockers cleared

---

*Generated as draft CSV only — no Odoo API, UI, or live system writes.*
