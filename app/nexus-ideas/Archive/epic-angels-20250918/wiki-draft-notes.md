# Wiki draft notes — Epic Angels follow-up (2025-09-18)

## Pages created (BookStack Idea Browser, book 621)

| Startup | Page ID | URL |
|---------|---------|-----|
| **Chum Chum** | 2950 | https://wiki.cleantechhub.net/books/idea-browser/page/chum-chum-food-agriculture |
| **Cirkula** | 2952 | https://wiki.cleantechhub.net/books/idea-browser/page/cirkula-food-agriculture |
| **NUX** | 2953 | https://wiki.cleantechhub.net/books/idea-browser/page/nux-not-assigned-unknown |

### Chapters used
- `REIN Network — Portfolio` (Chum Chum)
- `Hub Perú — Portfolio` (Cirkula)
- `CLP26 Colombia` (NUX)

## Founder sourcing (no invented names)

| Startup | Founder on page | Source |
|---------|-----------------|--------|
| Chum Chum | Verónica Macías | REIN Hubs Website Handoff (`/opt/claude-files/Projects/REIN Hubs (1)/REIN_HUBS_WEBSITE_HANDOFF.md`) |
| Cirkula | [PENDIENTE] | Hub Perú wiki 183/206/211 + investor portal page 15 — no name in Odoo or wiki |
| NUX | [PENDIENTE] | CLP26 end-report mention only — not in Odoo `res.partner` or `clp26_colombia_ideas.json` |

## Odoo pull summary

- **Model:** `res.partner` (no `initiative` model on this Odoo 18 instance)
- **Fields used:** `name`, `x_startup_name`, `x_clp_cohort`, `x_program_status`, `function`, `title`
- **CLP 2026 partners:** 95 records with startup names
- **Chum / Cirkula / NUX:** not in Odoo

## Founder tag backfill

- ~360 idea pages gained `founder` BookStack tag (from `## Founder` markdown or Odoo)
- Epic curated Colombia pages backfilled manually after bulk run (11 pages)

## HITL

Production `nexus-ideas.service` **not restarted**. Apply when Gideon approves — see `apply.md`.
