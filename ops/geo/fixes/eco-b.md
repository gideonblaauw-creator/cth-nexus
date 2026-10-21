# eco-b — ecosystem actor location fixes (batch 2/2)

Batch **eco-b**: suspect `ecosystem_actor` pins from `location-gaps.csv`, sorted by `id`, rows **69–136** (68 entities).

## Policy (this batch)

- `city` / `country` rows: **empty** `lat`/`lng` (no city-centroid pins).
- Verified `street_address` but geocode is city-level or unreliable: `precision=city`, **keep** `street_address`, **blank** coords.
- Global HQ outside catalogue country (Peru): note `hq_abroad` in `notes` when no Peru street pin applies (or parent org is foreign and only city/country is recorded).

## Method

- Street addresses from entity websites or official directories (gob.pe sedes, UN Peru, EU Delegation, etc.).
- No personal emails/phones; no internal Nexus URLs as `source_url`.
- Nominatim geocoding at ~1 req/s for `address` rows with street-level hits only.

## Precision counts

| precision | count |
|-----------|------:|
| address | 50 |
| city | 13 |
| country | 5 |
| unknown | 0 |

## Unknowns

- _(none)_

## City rows with retained street (geocode fallback)

- `pe-iica`, `pe-unalm-universidad-nacional-agraria-la-molina`, `pe-unmsm-universidad-nacional-mayor-de-san-marcos`, `pe-sistema-b`

## hq_abroad notes

- `pe-incofin`, `pe-mercy-corps-ventures`, `pe-oikocredit`, `pe-onu-habitat`, `pe-responsability`, `pe-root-capital`, `pe-wayra-peru`

## Remaining geocoder district warnings (address kept)

- `pe-kunan`: Nominatim Wanchaq vs Cusco label.
- `pe-sbs-superintendencia-de-banca-seguros-y-afp`: Nominatim San Isidro vs Lima label.
- `pe-serfor`: Nominatim San Isidro vs Magdalena del Mar label.
