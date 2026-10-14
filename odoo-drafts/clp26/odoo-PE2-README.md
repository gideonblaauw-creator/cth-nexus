# Odoo PE2 import drafts (CLP26 Peru) — DRAFT / HITL

**Status:** CSV-only draft for human review. **Do not import into Odoo** until Gideon approves and existing `res.partner` records are deduplicated (e.g. CurubaTech contact 522 shows founder contacts may already exist).

**Branch path:** `odoo-drafts/clp26/`  
**Files:** `odoo-PE2-companies.csv`, `odoo-PE2-founders.csv`

## Startups covered (5)

| Slug | Company import id | Website | Corporate fields (vat/street/city/email/phone) |
|------|-------------------|---------|-----------------------------------------------|
| pezconfiable | `__import__.clp26_pezconfiable` | **Missing** (not in deck/JSON) | All empty (not printed in deck) |
| vigia | `__import__.clp26_vigia` | **Missing** | All empty |
| wayra-watt | `__import__.clp26_wayra_watt` | `wayrawatt.com` | All empty |
| windlever | `__import__.clp26_windlever` | **Missing** | All empty |
| yakusmart | `__import__.clp26_yakusmart` | `yakusmart.io` | All empty |

## Gaps and flags per startup

### PezConfiable
- **Missing website** (empty in source JSON).
- **Wiki vs deck taxonomy:** wiki suggests `CT-AF-006` (Agroforestry); deck/brief use **`CT-IC-003`** (Supply Chain Traceability) in `category_id` — **needs HITL** if wiki should drive Odoo tags.
- **CT-2 (reference only, not in CSV):** `CT-AF-012` Blue Carbon & Mangroves.
- **Stage (deck/JSON):** Private Beta — not mapped to an Odoo field in this draft.
- **Pitch video / YouTube:** left empty per brief (uploads on `@cleantechhub273` only when approved).
- **Founders:** placeholder only; deck names (e.g. team slide) **not** imported.

### VIGÍA (ex MUCHIK)
- **NO_WIKI_PAGE** (flag in source JSON).
- **Missing website.**
- **CT-2:** `CT-IC-004` Climate Data Platforms.
- **Corporate fields:** all empty.

### Wayra Watt
- **Website:** `wayrawatt.com` (no `https://` in source — confirm Odoo format).
- **Stage (JSON):** Sketches.
- **CT-2:** `CT-WA-003` Recycling & Materials Recovery.
- **Corporate fields:** all empty.

### WindLever
- **Missing website.**
- **Wiki vs deck taxonomy:** wiki `CT-EN-006` (Distributed Generation) vs deck **`CT-IC-005`** (Precision Ag & Smart Grid) in `category_id` — **needs HITL**.
- **CT-2:** `CT-EN-002` Wind Energy.
- **Stage (JSON):** Prototype.
- **Corporate fields:** all empty.

### YakuSmart
- **Website:** `yakusmart.io`.
- **Wiki vs deck taxonomy:** wiki `CT-WW-002` vs deck **`CT-WW-004`** (Water Efficiency & Circular Use) — **needs HITL**.
- **CT-2:** `CT-IC-005` Precision Ag & Smart Grid.
- **Stage (JSON):** Launched.
- **Corporate fields:** all empty.

## Global import flags (verify before load)

| Flag | Detail |
|------|--------|
| `country_id` | Set to `PE` for all rows. **Confirm** Odoo 18 import expects ISO code vs `base.pe` / display name. |
| `industry_id` | **Left empty** — no Odoo industry mapping provided in brief; map manually if required. |
| `category_id` | Format `CLP26,<ct1>` per brief. **Confirm** partner tags `CLP26` and taxonomy tags exist in target DB. Only `ct1` in CSV; `ct2` documented per startup above. |
| Founder placeholders | Name **`TBD (LinkedIn)`** only; comment fixed string per brief. |
| Dedupe | Search Odoo for existing company/contact names and websites before import. |
| Deck PDFs | Not in this repo snapshot (`climate-kic/decks/*.pdf` referenced in JSON but unavailable here); copy derived from brief `copy_draft` excerpts only. |

## HITL checklist

- [ ] Gideon approval to import at all
- [ ] Dedupe against existing `res.partner` (companies + contacts; note CurubaTech contact 522 precedent)
- [ ] Resolve wiki vs deck taxonomy disagreements (PezConfiable, WindLever, YakuSmart)
- [ ] Confirm `country_id`, `category_id`, and empty `industry_id` import behavior on Odoo 18 staging
- [ ] Confirm website URL normalization (`wayrawatt.com`, `yakusmart.io`)
- [ ] LinkedIn-only founder pass replaces `TBD (LinkedIn)` rows (no data from decks/Odoo/Moodle/Drive)
- [ ] YouTube / pitch video fields remain empty until `@cleantechhub273` uploads approved
- [ ] Import companies CSV first, then founders CSV (parent external ids)
- [ ] Post-import spot-check: 5 companies, 5 placeholder contacts, comments and taxonomy suffix present

## Source

Built from **odoo-PE2** cloud agent brief (Peru CLP26 slice). No Odoo API, XML-RPC, UI, or live system writes were performed.
