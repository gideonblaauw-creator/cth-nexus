# eco-a — ecosystem_actor location fixes (batch 1/2)

Base branch: `cursor/location-audit-ef81` (PR #86). Suspect pins: first 68 of 136 `ecosystem_actor` rows in `location-gaps.csv`, sorted by `id`.

## Method

- Street addresses from each actor's public website or official institutional directory (gob.pe, embassies, multilateral country pages).
- Geocoding: Nominatim OpenStreetMap, 1 request/second, `User-Agent: CTH-Nexus-Geo-Audit/1.0`.
- City sanity-check noted in `notes` when Nominatim locality disagrees with source city.
- No personal emails, phone numbers, or internal-only URLs.

## Precision counts

| precision | count |
|-----------|------:|
| address | 57 |
| city | 6 |
| country | 5 |
| unknown | 0 |

## Unknown / no-pin entities

_None in this batch._

## Output

- [`eco-a.csv`](./eco-a.csv) — 68 rows
