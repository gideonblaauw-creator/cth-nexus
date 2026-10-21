# eco-b — ecosystem actor location fixes (batch 2/2)

Batch **eco-b**: suspect `ecosystem_actor` pins from `location-gaps.csv`, sorted by `id`, rows **69–136** (68 entities).

## Method

- Verified street addresses from entity websites or official directories (gob.pe, UN Peru, EU Delegation, etc.).
- If no street: `city`, `country`, or `unknown` with **no** lat/lng.
- `address` rows geocoded with Nominatim (1 req/s, normalized street tokens); city sanity-checked against Nominatim `address` fields where possible.

## Precision counts

| precision | count |
|-----------|------:|
| address | 53 |
| city | 10 |
| country | 5 |
| unknown | 0 |

## Unknowns

- _(none)_

## Geocoder city warnings

- `pe-iica`: Nominatim district Pachacámac vs expected La Molina (Av. La Molina corridor).
- `pe-kunan`: Nominatim Wanchaq vs expected Cusco (Av. Tullumayo).
- `pe-sbs-superintendencia-de-banca-seguros-y-afp`: Nominatim San Isidro vs Sede Central label Lima.
- `pe-serfor`: Nominatim San Isidro vs expected Magdalena del Mar (Javier Prado Oeste).
- `pe-unalm-universidad-nacional-agraria-la-molina`: Nominatim Pachacámac vs expected La Molina.
- `pe-unmsm-universidad-nacional-mayor-de-san-marcos`: Nominatim Los Olivos vs expected Lima (Ciudad Universitaria).

## Notes

- `pe-sistema-b`: official street on Sistema B Perú page; no Nominatim hit — recorded as `city` only (Miraflores).
- `pe-wayra-peru`: no Lima hub on [Wayra spaces](https://wayra.com/es/spaces) after 2020 regionalization — `city` Lima.
- International HQs without Peru street (`pe-incofin`, `pe-mercy-corps-ventures`, `pe-oikocredit`, `pe-onu-habitat`, `pe-responsability`): `country` Peru.
