# Odoo CO1 import drafts (CLP26 Colombia batch 1)

**Status:** DRAFT — no Odoo import has been run. These CSVs are for human review only.

**Branch:** `cursor/clp26-odoo-co1` → base `cursor/epic-apc-nexus-cards-4292`

## Files

| File | Rows | Purpose |
|------|------|---------|
| `odoo-CO1-companies.csv` | 7 | `res.partner` companies (`is_company=True`) |
| `odoo-CO1-founders.csv` | 7 | Placeholder child contacts (`TBD (LinkedIn)`) |

## Gaps and flags (per startup)

### agrodata-connect — AgroData Connect

- **Website:** Empty. Brief JSON had `gmail.com` (not treated as a printed company website in the deck excerpt).
- **Corporate fields:** vat, street, city, email, phone — not present in deck excerpts; left empty.
- **industry_id:** Empty (no Odoo industry mapping in brief).
- **country_id:** `base.co` (Colombia external id — confirm in target Odoo DB).
- **Stage (info only):** Ideation (not imported to CSV).

### agrolider — AGROLIDER

- **Website:** Missing in deck excerpt.
- **Corporate fields:** All empty.
- **Taxonomy note:** Wiki lists CT-IC-005; deck/brief ct1 is **CT-AF-007** (used in `category_id`). **Wiki vs deck DISAGREE** — ct1 from brief table retained.
- **Stage:** Prototype.

### airthnova — AirthNova

- **Website:** Missing in deck excerpt.
- **Corporate fields:** All empty.
- **Taxonomy confidence:** Medium (per brief JSON).
- **Stage:** Ideation.

### amazoniko — Amazóniko

- **Website:** Missing in brief JSON deck excerpt (left empty; do not pull from Nexus/onepager without deck proof).
- **Corporate fields:** All empty.
- **Taxonomy note:** **FLAG** — existing Nexus card ct1 may be CT-IC-003; deck/brief ct1 is **CT-WA-003** (used here). Reconcile before import.
- **Wiki vs deck:** DISAGREE (wiki CT-IC-003, deck CT-WA-003).
- **Stage:** Launched.

### artexlab — ArtexLab

- **Website:** Missing in deck excerpt.
- **Corporate fields:** All empty.
- **Taxonomy note:** Wiki CT-WA-004 vs deck/brief ct1 **CT-WA-003** — **DISAGREE**; brief table ct1 used.
- **Stage:** Ideation.

### bio-analytics — bio.analytics

- **Website:** Missing in deck excerpt (`Visit us!` in deck text without URL in excerpt).
- **Corporate fields:** All empty.
- **Stage:** Launched.

### cacelio — Cacelio

- **Website:** Empty. Brief JSON had `gmail.com` (not used as website).
- **Corporate fields:** All empty.
- **Founder names on deck slides:** Ignored for import (LinkedIn-only policy); placeholders only.
- **Stage:** Prototype.

## Global assumptions (verify before import)

1. **`country_id`:** Set to `base.co` for all rows. Confirm Colombia resolves correctly in Odoo 18.
2. **`category_id`:** Format `CLP26,<ct1>` — requires tag/category names **CLP26** and ct1 code (e.g. `CT-IC-005`) to exist or be creatable on import.
3. **`industry_id`:** Left blank — map manually if required.
4. **Pitch video / YouTube:** Not in these CSVs; leave empty until @cleantechhub273 links are confirmed.
5. **Deck PDFs:** Not available in this workspace run; copy derived from brief `copy_draft` excerpts only.

## HITL checklist (Gideon / ops)

- [ ] **Approval:** Gideon sign-off before any Odoo import.
- [ ] **Dedupe:** Search existing `res.partner` for company names and fuzzy matches (e.g. CurubaTech contact 522 shows founder contacts may already exist — repeat check for these seven).
- [ ] **Taxonomy:** Resolve wiki vs deck flags (agrolider, amazoniko, artexlab) and Nexus card ct1 for Amazóniko.
- [ ] **Websites:** Fill only from verified deck or LinkedIn; do not use Moodle/Odoo/Drive metadata.
- [ ] **Founders:** Replace `TBD (LinkedIn)` rows after LinkedIn sourcing; never from deck team slides.
- [ ] **Categories:** Ensure `CLP26` and each ct1 tag exist in Odoo.
- [ ] **Test import:** Dry-run on staging or import simulator if available.
- [ ] **Post-import:** Link to Nexus cards / wiki URLs manually if needed.

## Import order

1. `odoo-CO1-companies.csv`
2. `odoo-CO1-founders.csv` (depends on company `id` / `parent_id/id`)
