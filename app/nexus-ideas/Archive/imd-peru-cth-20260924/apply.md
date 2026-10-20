# Apply IMD Peru filter (mirror Epic Angels)

**Status:** Applied to production static assets (2026-09-24). No service restart.

## Surface

Epic Angels and IMD Peru filters live on **Startup Portfolio** (static HTML), not the Next.js Idea Browser `/ideas` app.

- Epic: `https://nexus.cleantechhub.net/p/startup-portfolio?epic=1`
- IMD: `https://nexus.cleantechhub.net/p/startup-portfolio?imd_pe=1`

Special row pills in `deploy/startup-portfolio.html` (not `FilterSidebar.tsx` on Ideas).

## CHANGES

| File | Change |
|------|--------|
| `Archive/imd-peru-cth-20260924/curated.json` | SoT (unchanged); 16 shareable, 1 hold (HardTech) |
| `src/data/imd-peru-curated.json` | Shareable allowlist (16) for lib / JSON export |
| `src/lib/imdPeru.ts` | Match helpers (mirrors `epicAngels.ts`) |
| `deploy/imd-peru-shareable.json` | Public bundle for startup portfolio fetch |
| `deploy/startup-portfolio.html` | Special pill **IMD · Perú · CTH programs**, `?imd_pe=1`, load/render path |
| Epic cache buster | `epic-angels-shareable.json?v=20260924-imd-sync` (was `20260921-cirkula18`) |

## Deploy steps taken

```bash
# Source tree (Lane B)
cd /opt/nexus-idea-browser

# Production static (same path Epic uses — Caddy file_server, no pm2)
cp deploy/startup-portfolio.html /var/www/nexus/startup-portfolio.html
cp deploy/imd-peru-shareable.json /var/www/nexus-assets/imd-peru-shareable.json

# Optional parity copy for cth-nexus deploy mirror
cp deploy/startup-portfolio.html /home/debian/cth-nexus/deploy/startup-portfolio.html
```

No `systemctl restart nexus-ideas.service` — Idea Browser service unchanged; portfolio is static.

## Verification

```bash
curl -sS -o /dev/null -w 'imd: %{http_code}\n' 'https://nexus.cleantechhub.net/p/startup-portfolio?imd_pe=1'
curl -sS -o /dev/null -w 'epic: %{http_code}\n' 'https://nexus.cleantechhub.net/p/startup-portfolio?epic=1'
curl -sS 'https://nexus.cleantechhub.net/nexus-assets/imd-peru-shareable.json?v=20260924-imd16' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['count'])"
```

Expect IMD JSON `count` = **16**. Grid count matches after client fetch (HardTech excluded).

## Rollback

```bash
cp /var/www/nexus/startup-portfolio.html.bak-* /var/www/nexus/startup-portfolio.html  # if backup taken
rm /var/www/nexus-assets/imd-peru-shareable.json
# Restore prior startup-portfolio from git/cth-nexus/deploy backup
```
