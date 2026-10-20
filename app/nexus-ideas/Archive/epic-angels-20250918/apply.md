# Apply Epic Angels filter to production

**Status:** Draft built locally — **HITL required before restart** (do not apply until Gideon approves).

## Pre-check (production still on old build)

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://nexus.cleantechhub.net/ideas
# expect 200
```

## Build (already run in this ticket)

```bash
cd /opt/nexus-idea-browser
npm run build
cp -r .next/static .next/standalone/.next/static
```

## Apply (requires sudo / HITL)

```bash
sudo systemctl restart nexus-ideas.service
sudo systemctl status nexus-ideas.service --no-pager
```

Service unit: `/etc/systemd/system/nexus-ideas.service`  
- WorkingDirectory: `/opt/nexus-idea-browser`  
- ExecStart: `node .next/standalone/server.js`  
- Port: **3010** (Caddy proxies `/ideas*` → 3010)

## Post-apply verification

```bash
# Base page
curl -sS -o /dev/null -w 'ideas: %{http_code}\n' https://nexus.cleantechhub.net/ideas

# Epic filter page (HTML shell)
curl -sS -o /dev/null -w 'ideas?epic=1: %{http_code}\n' 'https://nexus.cleantechhub.net/ideas?epic=1'

# API still healthy
curl -sS 'https://nexus.cleantechhub.net/ideas/api/ideas?count=3' | head -c 200
```

Manual: open sidebar → **Special → Epic Angels** pill; URL should gain `?epic=1`; card grid shows ~14 curated matches (see curated.json).

## Local preview (this ticket — port 3011, no prod impact)

```bash
cd /opt/nexus-idea-browser
npm run build
cp -r .next/static .next/standalone/.next/static
PORT=3011 node .next/standalone/server.js
# http://127.0.0.1:3011/ideas?epic=1
```

## Files changed

| File | Change |
|------|--------|
| `src/data/epic-angels-curated.json` | Allowlist (17 entries) |
| `src/lib/epicAngels.ts` | Normalize + match helpers |
| `src/types/idea.ts` | `IdeaFilter.epic` |
| `src/hooks/useIdeaFilter.ts` | `epic=1` URL param |
| `src/components/FilterSidebar.tsx` | Special / Epic Angels pill |
| `src/components/IdeaCard.tsx` | Epic badge when filter active |
| `src/app/page.tsx` | Paginated fetch + client filter |

## Rollback

```bash
# Restore from Archive backup if saved, or revert files manually, then:
cd /opt/nexus-idea-browser && npm run build && cp -r .next/static .next/standalone/.next/static
sudo systemctl restart nexus-ideas.service
```
