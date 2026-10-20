# Startup Portfolio UI audit — 2026-10-16

Production page: [Startup Portfolio](https://nexus.cleantechhub.net/p/startup-portfolio)  
Source: `/var/www/nexus/startup-portfolio.html` (not modified in this exercise)

Screenshot: `screenshot-current-production.png` (viewport capture of live page)

---

## Global navigation (site-level, not portfolio filters)

| Item | Type |
|------|------|
| Inicio, Ideas, **Startups**, Mentores, Inversores*, Funders* | Nav tabs (6; 2 gated) |
| EN / ES | Language toggle (2) |

\*Gated links; not part of portfolio filtering logic.

---

## Production portfolio controls (the “messy” layer)

### Stats bar (display only, 4 cells)

- Total startups  
- With website  
- Showing (filtered count)  
- Programs (fixed “8”)

### Row 1 — “Special” curated lists (3 mutually exclusive modes + chrome)

| Control | Kind | URL when active |
|---------|------|-----------------|
| Epic Angels | Pill toggle | `?epic=1` |
| IMD · Perú · CTH programs | Pill toggle | `?imd_pe=1` |
| CLP26 · ClimateLaunchpad 2026 | Pill toggle | `?clp26=1` |
| Epic stat pill | Context label (18 APC-shareable) | — |
| IMD stat pill | Context label (16 shareable) | — |
| CLP stat pill | Context label (53 CLP26) | — |
| epicangelnetwork.com ↗ | External link | — |

**Behavior:** Epic, IMD, and CLP26 replace the main dataset (not intersected with program/theme/stage pills). Epic vs IMD vs CLP26 are mutually exclusive. Active special mode disables “Web only” default.

### Row 2 — Search + program

| Control | Count | Notes |
|---------|-------|-------|
| Search input | 1 | Name only in portfolio mode; name + founder in special modes |
| Program pills | 9 | All + CLAC21–25, CLP, CLP20, CLP25 (single-select) |
| Web only | 1 toggle | Default ON; hides startups without `w` |

### Row 3 — Theme + stage (single row, two label groups)

| Control | Count | Notes |
|---------|-------|-------|
| Theme pills | 4 | All + CE / BIO / EN (single-select) |
| Stage pills | 6 | All + Pre-Seed, Seed, Pre-A, Series A, Series B+ (single-select) |

### Totals (production)

| Category | Count |
|----------|------:|
| Filter **rows** (excl. search) | 3 |
| Clickable filter **pills/buttons** (excl. stats, lang, nav) | **28** |
| Special URL filters | **3** (`epic`, `imd_pe`, `clp26`) |
| Toggles (web only) | 1 |
| Search fields | 1 |
| Language controls | 2 |

---

## Card fields (production grid)

| Field | Where |
|-------|--------|
| Program color bar | Top edge |
| Startup name | Header |
| Country flag | Header |
| Description (3-line clamp) | Body |
| Epic Angels badge | Footer (special lists) |
| IMD · Perú badge | Footer (special lists) |
| Program badge | Footer |
| Theme badge (CE/BIO/EN) | Footer |
| Stage badge | Footer |
| CT taxonomy badge(s) | Footer (0–2; links to wiki) |
| Nexus ↗ | Footer (when slug/path) |
| One-pager | Footer (when present) |
| Visit website / “No site yet” | Footer |
| **Modal** (click card) | CT nodes, YouTube, extra actions |

---

## Redundancy & clutter (findings)

1. **Three dense pill rows** before the grid — high scan cost on mobile; labels repeat (“All / Todo” ×3).  
2. **Theme (CE/BIO/EN) vs CT taxonomy** — overlapping mental models; cards often show both theme pill and CT node.  
3. **Program** appears twice visually (top color bar + program badge).  
4. **Special lists** share a row with external link and inline stat pills — crowded partner-facing strip.  
5. **Stats bar** duplicates information available in result line (“Showing”).  
6. **No country or CT-sector filter** in production despite flags and CT badges on cards.  
7. **Single-select pills** for program/theme/stage — cannot combine e.g. CLAC24 + CLAC25 without “All”.

---

## Preview options — control counts

Assumes same data + URL special modes preserved in all previews.

| Surface | Production | Option A | Option B | Option C |
|---------|----------:|---------:|---------:|---------:|
| Always-visible primary controls | ~29 | **2** (search + Filters) | **1** search + sidebar facets | **2** (search + More filters) + **4** segment buttons |
| Filter pill/facet buttons (max exposed at once) | 28 | 0 until drawer (then ~40 multi-select facets) | ~40 in sidebar | 4 segments + popover facets |
| Active-filter chips | 0 | Yes | Yes | Yes (non-segment) |
| Multi-select program/theme/stage | No | Yes | Yes | Yes |
| Country filter | No | Yes (drawer) | Yes (sidebar) | Yes (popover) |
| CT sector filter | No | Yes (drawer) | Yes (sidebar) | Yes (popover) |
| URL `?epic=1` / `?imd_pe=1` / `?clp26=1` | Yes | Yes | Yes | Yes |

---

## Preview files

| File | URL |
|------|-----|
| Option A | https://nexus.cleantechhub.net/nexus-assets/previews/startups-redesign-20261016/option-a.html |
| Option B | https://nexus.cleantechhub.net/nexus-assets/previews/startups-redesign-20261016/option-b.html |
| Option C | https://nexus.cleantechhub.net/nexus-assets/previews/startups-redesign-20261016/option-c.html |

All previews: `noindex`, CleantechHUB palette via `preview-base.css`, real data from `portfolio-core.json` + live `/nexus-assets/*.json` shareable lists.
