# Odoo CO3 import drafts (CLP26 Colombia) — DRAFT ONLY

**Status:** CSV drafts for human review. **No Odoo import has been run.** Nothing in this folder writes to Odoo, Moodle, Drive, or any live system.

**Files**

| File | Purpose |
|------|---------|
| `odoo-CO3-companies.csv` | `res.partner` company rows (7 startups) |
| `odoo-CO3-founders.csv` | Placeholder contact rows (`TBD (LinkedIn)`) linked to each company |

**Import prerequisites (HITL)**

- [ ] **Gideon approval** before any import to Odoo 18.
- [ ] **Dedupe check** against existing `res.partner` records (search by name, website, VAT). Brief example: CurubaTech contact id 522 suggests founder/company rows may already exist — do not duplicate.
- [ ] Confirm **`country_id`** external id (`base.co` for Colombia) matches this Odoo database.
- [ ] Confirm **`category_id`** tags exist: program tag `CLP26` and taxonomy tags `CT-*` as used in the CSV (`CLP26,CT-xx-xxx` format).
- [ ] Map or leave blank **`industry_id`** (left empty in draft; no mapping supplied in brief).
- [ ] Review **`comment`** copy against each deck PDF on Drive; excerpts were cleaned from `copy_draft` text only.
- [ ] **Founders:** import only after LinkedIn sourcing; deck team slides were **not** used. Placeholder names stay `TBD (LinkedIn)`.
- [ ] **YouTube / video URL:** not in these CSVs; leave empty until @cleantechhub273 links are confirmed (never cleantechhubcolombia1668).

---

## Gaps and flags per startup

### El Ocámbulo (`el-ocambulo`)

| Field | Status |
|-------|--------|
| Website | **Missing** (not in deck JSON) |
| VAT / street / city / email / phone | **Empty** (not taken from live systems) |
| Corporate address | **Unknown** |
| Taxonomy | Deck **CT-AF-009** (Bioeconomy & NbS); wiki lists **CT-AF-010** — **DISAGREE** (using deck ct1 per brief) |
| ct2 | CT-WA-002 (Organic Waste & Composting) — not repeated in company `comment` (ct1 only per template) |
| Stage (info) | Launched |
| Deck | Drive id `12rS4mpXFukjMqSKGLRhhcCoNH2CxlLnt` |

### Green Textile Solutions (`green-textile-solutions`)

| Field | Status |
|-------|--------|
| Website | **Missing** |
| VAT / street / city / email / phone | **Empty** |
| Taxonomy | Deck/wiki **agree** CT-WA-003; ct2 CT-IN-003 |
| Stage | Launched |
| Deck | Drive id `1SZd3Sb05WfJp0aakJ895ALVGzshfiSjB` |

### HoneyB (`honeyb`)

| Field | Status |
|-------|--------|
| Website | **Missing** |
| VAT / street / city / email / phone | **Empty** |
| Taxonomy | Deck **CT-IN-003**; wiki **CT-AF-009** — **DISAGREE** |
| ct2 | **Empty** in brief table (no second code) |
| Stage | Ideation |
| Deck | Drive id `1aHABMXFbh3dSBUHHt8zY0_ClgQMM_LsF` |

### KUO (SIGR) (`kuo`)

| Field | Status |
|-------|--------|
| Website | **Missing in deck** — JSON had `gmail.com`; **not imported** (not a company website) |
| VAT / street / city / email / phone | **Empty** (deck team slide names ignored for founders) |
| Taxonomy | Deck/wiki **agree** CT-WA-003; ct2 CT-IC-004 |
| Stage | Prototype |
| Deck | Drive id `1om8X0SfmujUKCIMS6HWixrYRIjfMBgCd` |

### Modular Agrosolutions (`modular-agrosolutions`)

| Field | Status |
|-------|--------|
| Website | **Set** from deck text: `https://www.modtech.site/ma` (deck shows `WWW.MODTECH.SITE/MA`) |
| VAT / street / city / email / phone | **Empty** |
| Taxonomy | Deck **CT-IC-003**; wiki **CT-IC-005** — **DISAGREE** |
| ct2 | CT-AF-007 (Precision Agri Data) |
| Stage | Prototype |
| Deck | Drive id `1m5F4NSnNsKDQSi4Bx2fjzOihfe7gvPxK` |
| Note | Deck slide credits **Cristian Contreras** — **not** used in founder CSV (LinkedIn-only rule) |

### NextGen Nutrition (Petfly) (`nextgen-nutrition`)

| Field | Status |
|-------|--------|
| Website | **Missing** |
| VAT / street / city / email / phone | **Empty** |
| Taxonomy | Deck **CT-AF-009**; wiki **CT-AF-012** — **DISAGREE** |
| ct2 | CT-WA-002 |
| Stage | Launched |
| Deck | Drive id `1xtJEOklpgJ9SVcZT0ro8iwU_b9nNkg8R` |
| Note | Deck mentions founders on team slide — **not** imported to founder CSV |

### Planta Comunitaria WPC (`planta-comunitaria-wpc`)

| Field | Status |
|-------|--------|
| Website | **Missing** |
| VAT / street / city / email / phone | **Empty** |
| Taxonomy | Deck **CT-WA-003** (primary); wiki emphasizes **CT-BU-001** — **DISAGREE** (ct2 in table is CT-BU-001 Sustainable Construction) |
| Stage | Prototype |
| Deck | Drive id `10BmZsNrMIfwjcncBr9TkZ2AfWz6w3PJw` |
| Location | Circasia, Quindío referenced in wiki slug/title — **not** written to `city` (not verified as printed corporate address in deck excerpt) |

---

## Global flags

1. **Local deck PDFs** referenced in brief (`/workspace/climate-kic/decks/*.pdf`) are **not present** in this workspace; copy relies on brief `copy_draft` excerpts only.
2. **`industry_id`** column is empty for all rows — Odoo industry mapping **pending**.
3. **`page_count`** for decks was `-` / null in brief — no page validation performed.
4. Founder row **`id`** values use suffix `_founder_01` (convention not specified in brief — confirm before import).
5. Import order: **companies first**, then **founders** (parent external ids).

---

## Wiki references (for HITL cross-check)

| Startup | Wiki |
|---------|------|
| El Ocámbulo | https://wiki.cleantechhub.net/books/idea-browser/page/el-ocambulo-food-agriculture |
| Green Textile Solutions | https://wiki.cleantechhub.net/books/idea-browser/page/green-textile-solutions-air-environment |
| HoneyB | https://wiki.cleantechhub.net/books/idea-browser/page/honeyb-clean-industry |
| KUO | https://wiki.cleantechhub.net/books/idea-browser/page/kuo-air-environment |
| Modular Agrosolutions | https://wiki.cleantechhub.net/books/idea-browser/page/modular-agrosolutions-food-agriculture |
| NextGen Nutrition | https://wiki.cleantechhub.net/books/idea-browser/page/nextgen-nutrition-petfly-food-agriculture |
| Planta Comunitaria WPC | https://wiki.cleantechhub.net/books/idea-browser/page/implementacion-de-una-planta-comunitaria-de-transformacion-de-residuos-plasticos-en-madera-plastica-wpc-para-el-fortalecimiento-de-la-economia-circular-en-circasia-quindio-air-environment |
