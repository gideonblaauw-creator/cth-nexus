# startups-b location fixes

Batch **startups-b**: second alphabetical half of deduped `portfolio_startup` + `startup_onepager_s` rows in `ops/geo/location-gaps.csv`, plus **17** Epic and **16** IMD Peru curated ideas (city/country only).

Policy: street only when published as a business office on the company site or official registry; otherwise city or country. Sources are public company URLs or Nexus public pages — no personal contact data.

Base: `cursor/location-audit-ef81` (PR #86).

## Precision counts (final)

- **address**: 7
- **city**: 45
- **country**: 92

**Total rows:** 144

## `possible_duplicate` column

Portfolio grid slug vs `/s/` or accent-variant slug for the same company. **18 rows** flagged (9 pairs), e.g. `istmo-verde` ↔ `istmo-verde-sa`, `linko-workers` ↔ `linko-workers-sas`, `habitat-a-vibe-company` ↔ `habitat-a-vibe-company-sas`, `hunter-tecnologia` ↔ `hunter-tecnología`, `monte-jazmin` ↔ `monte-jazmín`, `moviltronics` ↔ `moviltronics-sas`, `nuevas-tecnologias-fisicoquimicas` ↔ `nuevas-tecnologías-fisicoquímicas`, `simbiotic` ↔ `simbiotic-sas`, `suncolombia` ↔ `suncolombia-sas`.

## Coords policy

- `city` and `country` rows: empty `lat`/`lng`.
- `address` rows: coords only after street-level Nominatim (structured or free-text). No city-centroid pins.
- `plasticos-ambientales` and `proplanet-sas`: published street kept, `precision=city` (OSM had no street hit).
- `linko-workers` / `linko-workers-sas`: structured Nominatim street-level coords.

Street-level coords today: `istmo-verde`, `istmo-verde-sa`, `linko-workers`, `linko-workers-sas`, `novatio`, `two-glass`, `zhana-solutions`.

## Unknowns / country-only without city (startups)

Portfolio or one-pager entities with no published city (country or program context only): see CSV `precision=country` startup rows; Epic/IMD ideas mostly country-only Peru/Colombia.
