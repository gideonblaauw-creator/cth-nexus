# Odoo CA2 — CLP26 company & founder import drafts

**Status:** DRAFT for human review only. These CSVs must not be imported without Gideon's approval and a dedupe pass against existing `res.partner` records (founder contacts may already exist — e.g. CurubaTech contact id 522).

**Scope:** Eight CLP26 startups from pitch decks. No live Odoo, Moodle, or Drive writes were performed to produce this package.

## Files

| File | Purpose |
|------|---------|
| `odoo-CA2-companies.csv` | One `res.partner` company row per startup |
| `odoo-CA2-founders.csv` | One placeholder contact per startup (`TBD (LinkedIn)`) |
| `odoo-CA2-README.md` | Gaps, flags, and HITL checklist |

## Global assumptions & verify-before-import

| Item | Draft choice | Action before import |
|------|----------------|----------------------|
| `country_id` | Odoo external IDs `base.cr`, `base.sv`, `base.gt` | Confirm these resolve in your Odoo 18 database |
| `industry_id` | Left empty | Map manually if required |
| `category_id` | `CLP26,<CT1 code>` per brief | Ensure tag/category records `CLP26` and each `CT-*` exist or will be created on import |
| Pitch video / YouTube | Not in CSV (per brief) | Add later only from @cleantechhub273 if applicable |
| CT2 taxonomy | Not in company CSV columns | Documented in comments only via CT1 label; ct2 codes are in source JSON for reference |

## Per-startup gaps and flags

### siloe-garden — Siloe Garden Eco Sanctuary

| Field | Status |
|-------|--------|
| Website | Missing (not in deck JSON) |
| VAT, street, city, phone | Missing (not printed in deck excerpts) |
| Email | Missing |
| **Flags** | Wiki taxonomy `CT-AF-008` vs deck **CT-AF-009** (DISAGREE). CT2 **CT-AF-005** (Reforestation / REDD+) not written to CSV columns — confirm if needed elsewhere. Deck `page_count` unknown. |

### agrismart — Agrismart

| Field | Status |
|-------|--------|
| Website | **Present:** `https://agrismartsv.com` (printed in deck) |
| VAT, street, city, phone, email | Missing |
| **Flags** | Wiki `CT-AF-007` vs deck **CT-IC-005** (DISAGREE). CT2 **CT-WW-004** in source data only. |

### nutrichar — NUTRICHAR

| Field | Status |
|-------|--------|
| Website | Missing — source JSON had `gmail.com` (invalid domain, not used) |
| VAT, street, city, phone, email | Missing |
| **Flags** | Wiki `CT-AF-012` vs deck **CT-AF-010** (DISAGREE). CT2 **CT-AF-008** in source only. Pricing/deal slide text in deck is partially garbled in excerpts — numbers in deck not copied into Odoo fields. |

### smartdrive — SMARTDRIVE

| Field | Status |
|-------|--------|
| Website | Missing |
| VAT, street, city, phone, email | Missing |
| **Flags** | CT2 empty in brief table. Wiki and deck agree on **CT-TR-001**. |

### q-mind — Q-Mind

| Field | Status |
|-------|--------|
| Website | Missing — source JSON `gmail.com` ignored |
| Email | **Present:** `team.qmind@gmail.com` (printed in deck excerpt) |
| VAT, street, city, phone | Missing |
| **Flags** | CT2 **CT-IC-004** in source only. Wiki and deck agree on **CT-EN-001**. |

### crysalia-studio — Crysalia Studio

| Field | Status |
|-------|--------|
| Website | Missing |
| VAT, street, city, phone, email | Missing |
| **Flags** | Wiki `CT-IN-004` vs deck **CT-IN-003** (DISAGREE). CT2 **CT-WA-003** in source only. |

### finca-aguilas-verdes — Águilas Verdes

| Field | Status |
|-------|--------|
| Website | Missing |
| VAT, street, city, phone, email | Missing |
| **Flags** | Display name **Águilas Verdes** vs slug `finca-aguilas-verdes`. Wiki slug/page title references “Finca Ganadera”. Deck market figures contain OCR noise — not imported as structured fields. Wiki and deck agree on **CT-AF-004**. |

### pina-kakaw — Piña and Kakaw

| Field | Status |
|-------|--------|
| Website | Missing |
| VAT, street, city, phone, email | Missing |
| **Flags** | Wiki **CT-AF-009** vs deck **CT-EX-038** (DISAGREE). CT2 **CT-AF-009** (Bioeconomy & NbS) in source — distinct from CT1; confirm taxonomy tagging policy. |

## HITL checklist (before any import)

- [ ] Gideon approved import of these eight companies and placeholder founders
- [ ] Dedupe search in Odoo for company names and domains (especially **agrismartsv.com**)
- [ ] Dedupe founder contacts (LinkedIn pass replaces `TBD (LinkedIn)` rows — do not import placeholders as final contacts without review)
- [ ] Resolve wiki vs deck taxonomy disagreements (five startups flagged above)
- [ ] Confirm `CLP26` and each `CT-*` category/tag exists in Odoo
- [ ] Validate `country_id` external IDs in target database
- [ ] Optional: attach deck links using Drive file ids in comments (already embedded)
- [ ] YouTube left empty until verified on @cleantechhub273 only (never cleantechhubcolombia1668)

## CT2 reference (not in CSV columns; from brief)

| Slug | CT1 | CT2 |
|------|-----|-----|
| siloe-garden | CT-AF-009 | CT-AF-005 |
| agrismart | CT-IC-005 | CT-WW-004 |
| nutrichar | CT-AF-010 | CT-AF-008 |
| smartdrive | CT-TR-001 | *(empty)* |
| q-mind | CT-EN-001 | CT-IC-004 |
| crysalia-studio | CT-IN-003 | CT-WA-003 |
| finca-aguilas-verdes | CT-AF-004 | CT-AF-003 |
| pina-kakaw | CT-EX-038 | CT-AF-009 |
