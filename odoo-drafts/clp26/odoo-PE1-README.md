# Odoo PE1 import drafts (CLP26 Peru startups)

**Status:** DRAFT — CSV files only. No Odoo import has been run.

**Target:** Odoo 18 `res.partner` import via Gideon-approved process after dedupe review.

**Deck source:** Per-startup JSON in brief `odoo-PE1`; local PDF paths referenced there were **not present** in this workspace, so corporate contact fields were not cross-checked against PDF print.

---

## Files

| File | Rows | Purpose |
|------|------|---------|
| `odoo-PE1-companies.csv` | 6 | Company partners (`is_company=True`) |
| `odoo-PE1-founders.csv` | 6 | Placeholder founder contacts (`TBD (LinkedIn)`) |

---

## Gaps and flags by startup

### AgroLens (`__import__.clp26_agrolens`)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty (not in brief JSON) |
| Corporate fields | `vat`, `street`, `city`, `email`, `phone` left empty — not verified in deck PDF here |
| `industry_id` | Empty — no Odoo industry mapping supplied |
| `country_id` | Set to `PE` (ISO); confirm Odoo resolves `PE` vs `base.pe` on import |
| Taxonomy | CT1 **CT-AF-007** (Precision Agri Data); CT2 **CT-IC-005** in brief — CT2 not encoded in `category_id` (brief specifies `CLP26,<ct1>` only) |
| Wiki vs deck | **Agree** on CT-AF-007 |

### Andean Biofactories (`__import__.clp26_andean_biofactories`)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty |
| Corporate fields | All empty; not verified in deck PDF here |
| `industry_id` | Empty |
| `country_id` | `PE` — confirm on import |
| Taxonomy | CT1 **CT-AF-010**; CT2 **CT-AF-009** in brief (not in CSV category) |
| Wiki vs deck | **DISAGREE** — wiki CT-AF-007 vs deck CT-AF-010; CSV uses deck CT1 per brief |

### FIVRA (`__import__.clp26_fivra`)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty |
| Corporate fields | All empty |
| `industry_id` | Empty |
| `country_id` | `PE` — confirm on import |
| Taxonomy | CT1 **CT-IN-003**; CT2 empty in brief |
| Wiki vs deck | **DISAGREE** — wiki CT-IN-005 vs deck CT-IN-003; CSV uses deck CT1 |

### HardTech (`__import__.clp26_hardtech`)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty |
| Corporate fields | All empty |
| `industry_id` | Empty |
| `country_id` | `PE` — confirm on import |
| Taxonomy | **UNASSIGNED (low)** — `category_id` is `CLP26` only; comment says **Taxonomy pending** (no CT code invented). Brief notes **proposed** CT-IN-001 — **not** imported |
| Wiki vs deck | **DISAGREE** — wiki CT-IN-003 vs proposed deck CT-IN-001 |
| Brief flag | `LOW_CONFIDENCE_TAXONOMY` |

### Kallpa Greenz Leaders (`__import__.clp26_kallpa_greenz_leaders`)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty |
| Corporate fields | All empty |
| `industry_id` | Empty |
| `country_id` | `PE` — confirm on import |
| Taxonomy | **UNASSIGNED (low)** — `category_id` is `CLP26` only; **Taxonomy pending** in comment. Brief **proposed** CT-AF-010 — **not** imported as CT1 |
| Wiki vs deck | Wiki CT-AF-010 aligns with proposal but CT1 table says UNASSIGNED |
| Brief flag | `LOW_CONFIDENCE_TAXONOMY` |

### NanoHumi (`__import__.clp26_nanohumi`)

| Gap / flag | Detail |
|------------|--------|
| Website | Empty |
| Corporate fields | All empty |
| `industry_id` | Empty |
| `country_id` | `PE` — confirm on import |
| Taxonomy | CT1 **CT-AF-010**; CT2 **CT-AF-008** in brief (CT2 not in CSV category) |
| Wiki vs deck | **DISAGREE** — wiki CT-AF-012 vs deck CT-AF-010; CSV uses deck CT1 |

---

## Cross-cutting flags

- **Founders:** All rows are placeholders; no names, emails, or phones from decks, Drive, Moodle, or Odoo.
- **YouTube / pitch video:** Not included (per brief; use @cleantechhub273 only when added later).
- **Dedupe:** Before import, search existing `res.partner` records (e.g. CurubaTech — contact **522** shows founder contacts may already exist). Merge or skip duplicates.
- **Category tags:** Confirm Odoo has partner categories `CLP26` and each `CT-*` external ID before import.
- **Import IDs:** External IDs use prefix `__import__.clp26_*` for one-shot import; may be rewritten post-import.

---

## HITL checklist (human-in-the-loop)

- [ ] **Gideon approval** before any Odoo import or API/UI write
- [ ] **Dedupe pass** against live partners (name, website, VAT when available)
- [ ] **Resolve wiki vs deck taxonomy** for Andean Biofactories, FIVRA, HardTech, Kallpa Greenz Leaders, NanoHumi
- [ ] **Assign CT1** for HardTech and Kallpa Greenz Leaders (currently pending in CSV)
- [ ] **Verify `country_id`** format (`PE`) on a staging import
- [ ] **Optional:** map `industry_id` if program requires it
- [ ] **Scan deck PDFs** for printed email, phone, address, VAT — fill only if explicitly printed
- [ ] **LinkedIn pass** to replace founder `TBD (LinkedIn)` rows (do not use deck team slides)
- [ ] **Confirm CLP26 + CT-* tags** exist in Odoo
- [ ] **Post-import review** of comments and categories

---

## Drive deck links (reference)

| Startup | Drive file id |
|---------|----------------|
| AgroLens | `1SL-H4P4mSW4wIyNEitwjLQCma79_MyRZ` |
| Andean Biofactories | `137esrBbb4nMgiEfNTudV3TfX5_8epFG0` |
| FIVRA | `1XBoqfBw718P4SHTV_KG8fNcTV68UT5Oq` |
| HardTech | `1kuMsv2sFItitkiHVFccNUmFyW22FZQF3` |
| Kallpa Greenz Leaders | `18o0Kt5JIVowE-mbuBrJ9DByoRsNoIpL-` |
| NanoHumi | `1SyRZNWYEA3PDkzITHb39vpqxc89Ji01O` |
