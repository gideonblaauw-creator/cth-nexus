# Epic Angels curated filter — criteria

Source: [Epic Angel Network](https://www.epicangelnetwork.com/) pitch copy (Sept 2025).

| Dimension | Epic Angels requirement | Nexus filter behavior |
|-----------|-------------------------|----------------------|
| Geography | Early-stage **APAC & LATAM** | Allowlist seeded from CLP26 Colombia + Hub/wiki mentions; LATAM-first |
| Verticals | All | No vertical restriction in filter |
| Stage | **Pre-seed / seed / Series A** | Not auto-filtered by stage; curated entries are early-stage CLP26 cohort |
| Leadership | **≥1 woman at C-level** required | `women_clevel_status`: `confirmed` or `PENDIENTE` per entry |
| Cheque | Up to **USD 250K**/company | Noted in fit_note where Hub data exceeds (e.g. Cirkula ~USD 450k) |

## URL param

- Shareable filter: `?epic=1`
- Example: `https://nexus.cleantechhub.net/ideas?epic=1`

## Matching logic

Client-side after full catalog fetch (BookStack max 100/page):

1. `app_id` exact match
2. `bookstack_page_id` exact match
3. `slug` in `bookstack_page_url`
4. Normalized `startup_name` / `aliases` (accent- and punctuation-insensitive)

## Live route

- **Next.js app (this filter):** `https://nexus.cleantechhub.net/ideas` → Caddy `reverse_proxy 127.0.0.1:3010`
- **Legacy static shell:** `https://nexus.cleantechhub.net/p/ideas` → `/var/www/nexus/idea-browser.html` (HumHub embed; not this build)
