# Investor CRM HQ location fixes (batch: investors)

Generated: 2026-10-21. Source gaps: `ops/geo/location-gaps.csv` (529 `investor_crm` rows).

## Summary

| Metric | Count |
|--------|------:|
| Total rows | 529 |
| `precision=city` (HQ city + country verified) | 529 |
| `precision=unknown` | 0 |
| Gap tier `none` (no CRM country) | 404 |
| Gap tier `country-only` | 125 |

## Method

- HQ **city** and **country** taken from each fund's **official website** (contact/about/imprint or JSON-LD), shared domain cache, or **Wikidata P159** when the site had no parseable HQ.
- Investment geography (`geo_focus` / `geo_tags`) was **not** used as office location.
- No street addresses or coordinates in this batch (`street_address`, `lat`, `lng` left blank).

## Unknowns

None — all rows have verified HQ city + country.

## Apply

Review `ops/geo/fixes/investors.csv` before merging into Investors CRM / geo pipeline (no deploy in this PR).
