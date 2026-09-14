# Datathon portal — Marlene/CEE Vercel CTA tile (HITL draft)

**Date:** 2026-09-14  
**bc-id:** t1307u (Gideon GO)  
**Status:** **READY FOR GIDEON HITL — do not apply without explicit yes**

## Goal

Add a visible **outbound CTA card** on the existing Participant Portal at  
`https://datathon.data.cleantechhub.net/` (static files under `/opt/datathon/static`)  
that links to the Marlene/CEE Academy demo on Vercel:

**https://marlene-datathon-cth.vercel.app/**

Event context: **CCB Energy Cluster · Thu 17 Sep 2026** ([Luma](https://luma.com/kdvd65cv)).

## What this pack contains

| Path | Purpose |
|------|---------|
| `source/` | Snapshot of live `/opt/datathon/static` (2026-09-14, unchanged) |
| `preview/` | Draft with CTA tile applied (`index.html`, `portal.css`; `portal.js` unchanged) |
| `index.html.diff` | Unified diff for HTML |
| `portal.css.diff` | Unified diff for CSS |
| `README.md` | This file |

## Design

- **Placement:** Top of `.content`, before tab panels — visible on landing (Inicio tab active).
- **Behaviour:** External link only (`target="_blank"`, `rel="noopener noreferrer"`). No iframe, no Vercel reverse-proxy.
- **Branding:** Reuses existing CTH portal tokens (`--blue`, `--forest`, `.pill`, `.btn-primary`).
- **Copy:** ES primary + EN subtitle; references CCB Energy Cluster / CEE Externado / Marlene deck.

**Not in scope:** Origo mount, Caddy edits, datathon docker restart, Django/API changes.

## HITL apply steps (Gideon only)

```bash
# 1. Backup live static (optional but recommended)
sudo cp -a /opt/datathon/static /opt/datathon/static.bak-$(date +%Y%m%d)

# 2. Copy draft files
sudo cp preview/index.html /opt/datathon/static/index.html
sudo cp preview/portal.css /opt/datathon/static/portal.css
# portal.js unchanged — do not copy unless intentionally updated

# 3. Verify (no Caddy reload required — static file_root)
curl -sS https://datathon.data.cleantechhub.net/ | grep -F 'cee-demo-tile'
curl -sS https://datathon.data.cleantechhub.net/ | grep -F 'marlene-datathon-cth.vercel.app'
curl -I https://datathon.data.cleantechhub.net/
```

## Rollback

```bash
sudo cp source/index.html /opt/datathon/static/index.html
sudo cp source/portal.css /opt/datathon/static/portal.css
```

Or restore from `static.bak-*` if created.

## Verify checklist (after HITL)

- [ ] `https://datathon.data.cleantechhub.net/` loads without console errors
- [ ] Gold pill “CCB Energy Cluster · 17 Sep 2026” visible above welcome card
- [ ] “Abrir demo en vivo” opens `https://marlene-datathon-cth.vercel.app/` in new tab
- [ ] Existing portal tabs (Compute, LLM API, Submit, Leaderboard) still work
- [ ] `/api/*` and docker stack **not** touched (stack remains Exited; odoo-mcp on :8001 unchanged)

## Thu 17 Sep fallback

If HITL is not applied before the event, share the Vercel URL directly:  
**https://marlene-datathon-cth.vercel.app/**

Recruitment landing (separate product): https://ccb-datathon-energia.vercel.app/ — **not** linked from this tile.

## Production touch confirmation

**Zero live changes in this pack.** Live `/opt/datathon/static` was read-only snapshotted; preview lives only in this archive folder.
