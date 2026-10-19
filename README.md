# cth-nexus

Lane A home for Nexus startup one-pagers served at `https://nexus.cleantechhub.net/s/{slug}`.

## Structure

- `onepagers/template/styles.css` — shared CTH design system
- `onepagers/data/{slug}.json` — deck-faithful content per startup
- `scripts/build_onepagers.py` — JSON → HTML builder
- `scripts/build_clp26_slice_onepagers.py` — CLP26 slice JSON → `/s/{slug}` one-pagers
- `onepagers/sites/{slug}/index.html` — built output (also mirrored to Archive drafts)
- `pages/p/startup-portfolio/index.html` — portfolio grid (loads `nexus-assets/clp26-national-shareable.json`)
- `nexus-assets/clp26-national-shareable.json` — CLP26 national startup cards for the portfolio

## Build

```bash
python3 scripts/build_onepagers.py
python3 scripts/build_clp26_slice_onepagers.py
```

CLP26 slice one-pagers (metadata + single-slide deck viewer):

```bash
python3 scripts/build_clp26_slice_onepagers.py
```

Startup portfolio grid (`/p/startup-portfolio`):

- `pages/p/startup-portfolio/index.html` — portfolio UI (includes One-pager buttons)
- `nexus-assets/clp26-semi-shareable.json` — CLP26 semi cards merged into the main grid

Outputs to `onepagers/sites/{slug}/index.html` and `/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20/{slug}/index.html`.

### CLP26 Peru slice one-pagers

Slice JSON lives in `onepagers/data/clp26-slices/{slug}.json`; deck PDFs in `onepagers/decks/{slug}.pdf`.

```bash
python3 scripts/build_clp26_slice_onepagers.py
```

Writes `onepagers/sites/{slug}/index.html` and `onepagers/sites/{slug}/deck.pdf` (served at `/s/{slug}` and `/s/{slug}/deck.pdf`).

Portfolio grid + IMD Peru card data (deploy separately to Nexus):

- `pages/p/startup-portfolio.html` — portfolio page with **One-pager** buttons on cards and detail modal
- `nexus-assets/imd-peru-shareable.json` — CLP26 Peru card fields for YakuSmart, VIGIA, PezConfiable (slice-driven)

## Caddy (production — Gideon approval required)

Live pages are served from `/opt/nexus-onepagers/{slug}/index.html` via:

```
handle_path /s/* {
  root * /opt/nexus-onepagers
  try_files {path}/index.html {path}
  file_server
}
```

**Do not copy into `/opt/nexus-onepagers/` until approved** — Caddy serves immediately with no reload.

## Suggested live slugs

| Startup | Slug | Draft preview |
|---------|------|---------------|
| Curuba | `curuba` | `/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20/curuba/index.html` |
| bio·analytics | `bio-analytics` | `.../bio-analytics/index.html` |
| Cacelio | `cacelio` | `.../cacelio/index.html` |
| CommunityLab | `communitylab` | `.../communitylab/index.html` |
| Green T | `green-t` | `.../green-t/index.html` |
| TERRA IO | `terra-io` | `.../terra-io/index.html` |
