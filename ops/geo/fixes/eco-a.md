# eco-a — ecosystem_actor location fixes (batch 1/2)

Base branch: `cursor/location-audit-ef81` (PR #86). Suspect pins: first 68 of 136 `ecosystem_actor` rows in `location-gaps.csv`, sorted by `id`.

## Method

- Street addresses from each actor's public website or official institutional directory (gob.pe, embassies, multilateral country pages).
- Geocoding: Nominatim structured → Nominatim freeform → Photon; 1 request/second between Nominatim calls.
- **Policy:** `city` / `country` precision rows have **empty** `lat`/`lng` (no centroid pins).
- Address rows without street-level geocode keep `street_address` but downgrade to `city` with blank coords.
- `hq_abroad` in `notes` when pin country ≠ catalogue country (international HQ).
- No personal emails, phone numbers, or internal-only URLs.

## Precision counts

| precision | count |
|-----------|------:|
| address | 44 |
| city | 19 |
| country | 5 |
| unknown | 0 |

## Country precision (no pin)

- `pe-acumen`
- `pe-alterfin`
- `pe-bei-banco-europeo-de-inversiones`
- `pe-blueorchard`
- `pe-finance-in-motion`

## City precision (no pin)

- `pe-accion-andina`
- `pe-actualidad-ambiental`
- `pe-afd`
- `pe-alive-ventures`
- `pe-asociacion-unacem`
- `pe-caja-maynas`
- `pe-camara-peruano-alemana-ahk`
- `pe-cerro-verde`
- `pe-endeavor-peru`
- `pe-fepcmac-federacion-de-cajas-municipales`
- `pe-forest-trends`
- `pe-gestion`
- `pe-gobierno-regional-de-amazonas`
- `pe-gobierno-regional-de-loreto`
- `pe-gobierno-regional-de-madre-de-dios`
- `pe-gobierno-regional-de-san-martin`
- `pe-gobierno-regional-de-ucayali`
- `pe-grade-grupo-de-analisis-para-el-desarrollo`
- `pe-hudbay`

## hq_abroad

- `co-cif-climate-investment-funds`
- `co-gcf-green-climate-fund`
- `pe-andes-amazon-fund`
- `pe-ecoenterprises-fund`
- `pe-forest-trends`

## Policy pass changed ids

- `co-bancoldex`
- `co-cif-climate-investment-funds`
- `co-gcf-green-climate-fund`
- `pe-accion-andina`
- `pe-actualidad-ambiental`
- `pe-afd`
- `pe-alive-ventures`
- `pe-amazonia-impact-ventures`
- `pe-andes-amazon-fund`
- `pe-arbio`
- `pe-asociacion-unacem`
- `pe-banco-mundial`
- `pe-bolsa-de-valores-de-lima`
- `pe-caf-banco-de-desarrollo-de-america-latina`
- `pe-caja-maynas`
- `pe-caja-piura`
- `pe-camara-peruano-alemana-ahk`
- `pe-cerro-verde`
- `pe-concytec-prociencia`
- `pe-ecoenterprises-fund`
- `pe-endeavor-peru`
- `pe-fepcmac-federacion-de-cajas-municipales`
- `pe-financiera-confianza`
- `pe-forest-trends`
- `pe-gestion`
- `pe-gobierno-regional-de-amazonas`
- `pe-gobierno-regional-de-loreto`
- `pe-gobierno-regional-de-madre-de-dios`
- `pe-gobierno-regional-de-san-martin`
- `pe-gobierno-regional-de-ucayali`
- `pe-grade-grupo-de-analisis-para-el-desarrollo`
- `pe-hub-udep-universidad-de-piura`
- `pe-hudbay`
- `pe-ifc`

## Output

- [`eco-a.csv`](./eco-a.csv) — 68 rows
