# startups-a location fixes (batch A, first half)

Portfolio startups: **78** slugs (alphabetical first half of `location-gaps.csv`).

## Precision counts

| precision | count |
|-----------|------:|
| address | 9 |
| city | 39 |
| country | 13 |
| unknown | 17 |

## Coordinate policy

- **`city` / `country` / `unknown`:** `lat` and `lng` are always empty (no city-centroid pins).
- **`address`:** coordinates only when Nominatim returns a sub-city result (e.g. street/highway/building), not an administrative city boundary.
- If a published street geocodes only to **city level**, set `precision=city`, **blank** `lat`/`lng`, and **keep** `street_address` (see `entopro`).

## Address geocoding

Street rows geocoded via [Nominatim](https://nominatim.openstreetmap.org/) (1 req/s). Address precision without coordinates: `ciclorgánicos-(bio-abonos-gaia)` (rural finca; no street-level hit).

## Unknowns / missing source_url

- `agrotech` — precision=unknown, source_url=(empty)
- `arabidopsis` — precision=unknown, source_url=(empty)
- `bio360-jardines-verticales` — precision=unknown, source_url=(empty)
- `biofadi` — precision=unknown, source_url=(empty)
- `biofer` — precision=unknown, source_url=(empty)
- `biomasa` — precision=unknown, source_url=(empty)
- `claudia-osorio-arte-y-vidrio` — precision=unknown, source_url=(empty)
- `colombia-por-naturaleza` — precision=unknown, source_url=(empty)
- `compost-baladí-sas` — precision=unknown, source_url=(empty)
- `conexa-soluciones` — precision=unknown, source_url=(empty)
- `coolest-fins` — precision=unknown, source_url=(empty)
- `cropexpert` — precision=unknown, source_url=(empty)
- `cultivo-global-sas` — precision=unknown, source_url=(empty)
- `diservicol` — precision=unknown, source_url=(empty)
- `fruitable` — precision=unknown, source_url=(empty)
- `gestar-ingeniería-sas` — precision=unknown, source_url=(empty)
- `grupo-voltem-sas` — precision=unknown, source_url=(empty)

Artifact: [`startups-a.csv`](./startups-a.csv)
