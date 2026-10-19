# Datathon portal — Marlene/CEE Vercel CTA tile

**Date:** 2026-09-14  
**bc-id:** t1307u  
**Status:** **READY FOR GIDEON HITL — apply only on explicit yes**

## Summary

Add an outbound **landing tile** on the existing Participant Portal at  
`https://datathon.data.cleantechhub.net/` (`/opt/datathon/static`) linking to the Academy Marlene/CEE demo:

| Field | Value |
|-------|-------|
| Live portal (after HITL) | https://datathon.data.cleantechhub.net/ |
| Vercel href (CTA target) | https://marlene-datathon-cth.vercel.app/ |
| Event | CCB Energy Cluster · Thu 17 Sep 2026 · [Luma](https://luma.com/kdvd65cv) |

**Thu fallback:** If HITL is not applied, use Vercel directly.

## Why this approach

| Option | Verdict |
|--------|---------|
| **CTA tile on datathon.data static portal** | ✅ Recommended — minimal change, no Caddy/docker/API, clear outbound link for event |
| Origo `/datathon/` mount | ❌ HOLD — Orchestrator/Gideon deferred |
| Replace datathon.data root | ❌ Breaks Participant Portal demo UI |
| Vercel reverse-proxy on VPS | ❌ Adds dependency; content stays on Vercel anyway |
| Restart datathon docker stack | ❌ Out of scope; stack Exited ~2 months |

## Verified facts (read-only, 2026-09-14)

- `https://datathon.data.cleantechhub.net/` serves static files from `/opt/datathon/static` (`index.html`, `portal.css`, `portal.js`).
- This is the **Participant Portal** demo — not the Marlene Academy deck.
- Marlene/CEE content lives on **https://marlene-datathon-cth.vercel.app/** (“Del diagnóstico al tablero en vivo”).
- **https://ccb-datathon-energia.vercel.app/** is recruitment landing only — not linked.
- Datathon docker compose (datathon-web/celery/db/redis) is **Exited**; do not restart.
- Caddy `/api/*` on datathon host routes to odoo-mcp `:8001`, not datathon-web — do not “fix”.
- **No changes** to origo.data, Caddy, DNS, or `/opt/origo-ui/`.

## Draft change

### HTML (`index.html`)

Insert after `<div class="content">`, before the Welcome panel:

```html
<section class="cee-demo-tile" aria-label="Clúster Energía Datathon demo">
  <div class="cee-demo-inner">
    <div class="cee-demo-copy">
      <span class="pill pill-gold"><span class="dot"></span>CCB Energy Cluster · 17 Sep 2026</span>
      <h2>Clúster Energía · Datathon demo</h2>
      <p class="cee-demo-lead">Recorrido Academy CleantechHUB / CEE Externado: <strong>del diagnóstico al tablero en vivo</strong>. Demo interactiva para el evento CCB Energy Cluster (Luma).</p>
      <p class="cee-demo-en"><em>From assessment report to live dashboard — Marlene / CEE datathon walkthrough (hosted on Vercel).</em></p>
    </div>
    <a class="btn btn-primary cee-demo-btn"
       href="https://marlene-datathon-cth.vercel.app/"
       target="_blank" rel="noopener noreferrer">
      <svg aria-hidden="true"><use href="#i-bolt"></use></svg>
      Abrir demo en vivo ↗
    </a>
  </div>
</section>
```

### CSS (`portal.css`)

Append `.cee-demo-tile` block (see `preview/portal.css` in this PR or VPS archive diff).

`portal.js` — **no change**.

Full preview: `preview/datathon-portal/` in this repo.

## HITL apply (Gideon only)

```bash
ARCHIVE="/opt/claude-files/Projects/CTH - Climate_Data_Platform/datathon-vercel-cta-2026-09-14"

sudo cp -a /opt/datathon/static /opt/datathon/static.bak-$(date +%Y%m%d)
sudo cp "$ARCHIVE/preview/index.html" /opt/datathon/static/index.html
sudo cp "$ARCHIVE/preview/portal.css" /opt/datathon/static/portal.css

curl -sS https://datathon.data.cleantechhub.net/ | grep -F 'marlene-datathon-cth.vercel.app'
curl -I https://datathon.data.cleantechhub.net/
```

**Do not** reload Caddy. Static `file_server` picks up files immediately.

## Rollback

```bash
sudo cp "$ARCHIVE/source/index.html" /opt/datathon/static/index.html
sudo cp "$ARCHIVE/source/portal.css" /opt/datathon/static/portal.css
```

## Risks

| Risk | Mitigation |
|------|------------|
| Tile clutters welcome view | Single compact band; ES+EN copy kept short |
| Broken external link | `rel=noopener`; Thu fallback = Vercel URL |
| Accidental docker/Caddy change | This plan touches **only** two static files |

## VPS archive (canonical draft pack)

```
/opt/claude-files/Projects/CTH - Climate_Data_Platform/datathon-vercel-cta-2026-09-14/
├── source/          # live snapshot
├── preview/         # draft with CTA
├── index.html.diff
├── portal.css.diff
└── README.md
```

## Production confirmation

**No production changes were applied** in preparing this plan. Live portal unchanged as of 2026-09-14.

**READY FOR GIDEON HITL — do not apply without explicit yes.**
