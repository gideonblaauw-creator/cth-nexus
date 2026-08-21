# cth-nexus

Lane A home for Nexus startup one-pagers served at `https://nexus.cleantechhub.net/s/{slug}`.

## Structure

- `onepagers/template/styles.css` — shared CTH design system
- `onepagers/data/{slug}.json` — deck-faithful content per startup
- `scripts/build_onepagers.py` — JSON → HTML builder
- `onepagers/sites/{slug}/index.html` — built output (also mirrored to Archive drafts)

## Build

```bash
python3 scripts/build_onepagers.py
```

Outputs to `onepagers/sites/{slug}/index.html` and `/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20/{slug}/index.html`.

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
