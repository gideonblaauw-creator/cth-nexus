# startups-b location fixes

Batch **startups-b**: second alphabetical half of deduped `portfolio_startup` + `startup_onepager_s` rows in `ops/geo/location-gaps.csv`, plus **17** Epic and **16** IMD Peru curated ideas (city/country only).

Policy: street only when published as a business office on the company site or official registry; otherwise city or country. Sources are public company URLs or Nexus public pages — no personal contact data.

Base: `cursor/location-audit-ef81` (PR #86).

## Precision counts

- **address**: 9
- **city**: 43
- **country**: 92

**Total rows:** 144

## Unknowns / country-only without city (startups)

Portfolio or one-pager entities with no published city (country or program context only): `heliosave-clean-energy`, `hidrobank`, `hydroforge`, `i-can-jump`, `kigui` (country Mexico; metro not verified), `kimsa`, `kleantab`, `labgae`, `lazos.go`, `magmacol`, `melipapp`, `mitsidi`, `moviltronics`, `moviltronics-sas`, `mullblue`, `natoure`, `natupin`, `neo-fibers-sac`, `o&c-sas`, `o2reserve`, `parsons-kinetics`, `plasfacol`, `plastifuel`, `purest-fuels`, `reemade`, `renove.io`, `sanolivar`, `selvamar`, `semillatek`, `siembra-vertical`, `soluciones-ambientales-integrales-sas`, `suncolombia`, `tavi-technology`, `tecnologías-ecológicas-ecotec-sas`, `usalo-app`, `virtualel`, `xiclo`, `ydeas-team-sas`, `zircular`, plus Epic/IMD ideas marked country-only in CSV.

**Coords policy:** `city` and `country` rows always have empty `lat`/`lng` (no centroid pins). `lat`/`lng` appear only on `address` rows where Nominatim returned a street-level hit (`istmo-verde`, `istmo-verde-sa`, `novatio`, `two-glass`, `zhana-solutions`). If a street geocode would fall back to city level, use `precision=city`, keep `street_address` text, and leave coords blank.
