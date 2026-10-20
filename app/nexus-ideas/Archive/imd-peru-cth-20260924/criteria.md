# IMD Peru — CTH alumni curated list (HITL)

**Audience:** IMD (Lausanne) internal human-in-the-loop coaching list — Peru-based startups with verified CleantechHUB program participation.

**Archive date:** 2026-09-24  
**Pattern:** Mirrors Epic Angels archive (`Archive/epic-angels-20250918/`) — criteria doc + `curated.json` + `CHANGES.md`; no live filter deploy in this pass.

## Inclusion (all required unless noted)

| Dimension | Rule |
|-----------|------|
| **Country** | **Peru (PE)** — HQ or primary market Peru. Dual-HQ unclear → mark fields `[PENDIENTE]` and `shareable: false`. |
| **Program** | **CTH alumni only:** CLP cohorts, REIN, GIZ Growth Services, Academy/CLP, Hub Perú programs, or other verified CTH program tag in Odoo/BookStack/Nexus. **Exclude** catalog ideas with Peru country tag but **no** program evidence. |
| **Sourcing** | Do **not** invent founders or websites. Unsourced values → `[PENDIENTE]`. |
| **Shareable fields** | No personal founder **emails** in rows marked `shareable: true`. Names from Odoo/BookStack are allowed. |

## Data sources (read-only for this curation)

1. **Odoo** `res.partner`: `x_startup_name`, `x_clp_cohort`, `x_program_status`, `country_id` = Peru — primary list for **CLP 2026 Peru** (16 partners, 2026-09-24 pull).
2. **Nexus Idea Browser** (`/opt/nexus-idea-browser/`, live API `127.0.0.1:3010`) — `nexus_url`, stage, `ct_taxonomy`, founder tags.
3. **BookStack** Idea Browser book 621 — country/stage/founder tags; Hub Perú portfolio chapter for **Cirkula** (page 2952).
4. **Epic curated reference** — `src/data/epic-angels-curated.json` (Cirkula PE + Hub Perú program verification).

## Shareable vs hold

| Flag | Meaning |
|------|---------|
| `shareable: true` | Safe for IMD internal share: PE country, verified program, `nexus_url` **or** explicit hold notes; no blocker fields `[PENDIENTE]` on URL/country/program. |
| `shareable: false` | **Hold** — missing Nexus match, unresolved HQ, or critical `[PENDIENTE]` (e.g. no idea page). |

## Matching logic (Nexus)

Same as Epic allowlist behavior (normalized startup name, BookStack slug, `app_id` / page id where available):

1. Odoo `x_startup_name` → Nexus `startup_name` (accent/punctuation insensitive).
2. Known renames documented in `notes` (e.g. **VIGIA** ↔ catalog **MUCHIK**, **PectiGrow** ↔ **BioPectinGrow**).

## Out of scope (this archive)

- No FilterSidebar / lib / deploy / production restart.
- No Google Drive links, PDF, or email to IMD.
- No git commit or PR.
