# Nexus location audit (read-only)

Generated: **2026-10-21** from repo bundles (`static/ecosystem/data/actors.json` post [#63](https://github.com/gideonblaauw-creator/cth-nexus/pull/63) / [#79](https://github.com/gideonblaauw-creator/cth-nexus/pull/79) geocoding policy).

## Policy (audit baseline)

Map pins should appear **only** at a **verified street address** sourced from the entity's own website or an official directory. Otherwise treat as **location unknown** (country badge / text only).

Under this strict rule, `precision: city` pins, Nominatim/Photon name+city queries, Wikidata city coordinates, HQ fallbacks, and country-capital hub coordinates count as **suspect** even when lat/lng exist.

## Summary

| Entity type | Total | Verified address + coords (strict) | Address precision + coords | City-only (plotted) | Country-only | None | Suspect / guessed pins |
|-------------|------:|-----------------------------------:|-----------------------------:|--------------------:|-------------:|-----:|-----------------------:|
| ecosystem_actor | 381 | 116 | 116 | 0 | 265 | 0 | 0 |
| ecosystem_funder | 105 | 41 | 41 | 0 | 64 | 0 | 0 |
| hub_hubmap | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| portfolio_startup | 156 | 11 | 11 | 0 | 145 | 0 | 0 |
| startup_onepager_s | 91 | 4 | 4 | 0 | 68 | 19 | 0 |
| mentor_clp26 | 55 | 0 | 0 | 4 | 51 | 0 | 0 |
| investor_crm | 529 | 0 | 0 | 257 | 65 | 207 | 0 |
| idea_curated_imd_pe | 16 | 0 | 0 | 0 | 16 | 0 | 0 |
| idea_curated_epic | 17 | 0 | 0 | 0 | 0 | 17 | 0 |
| jury_clp26 | 21 | 0 | 0 | 12 | 0 | 9 | 0 |
| policy_ecosystem | 40 | 0 | 0 | 0 | 40 | 0 | 0 |

Gap export: [`location-gaps.csv`](./location-gaps.csv) (entities not meeting strict verified-address policy; no personal emails/phones).

### Ideas (BookStack)

Live Idea Browser pages are served from BookStack (`BOOKSTACK_*` not set in this audit run). Counts above for **idea_curated_*** rows are **offline curated subsets only**, not the full catalog. Full ideas have `country` tags and optional city in markdown — **no lat/lng in the list API**.

### Portfolio vs `/s/` one-pagers

- Portfolio grid (`portfolio-core.json`): **156** startups — ISO country code only.
- `/s/` JSON one-pagers (`onepagers/data/`): **91** files; `nexus-crosslinks.json` lists **121** valid slugs.

## Per-type notes

### ecosystem_actor

Primary map dataset for `/ecosystem/`. Plottable pins use `geo.precision` `address` or `city` (`static/ecosystem/geo-utils.mjs`). Country-precision actors (223) show as country badges only.

**By country (actors):** Peru 293, El Salvador 77, Colombia 6, United States 4, South Korea 1

- Map-plottable pins (address+city precision): **116**
- Policy-ok verified address pins: **116**
- Country badge only: **265**

### ecosystem_funder

Subset of ecosystem actors with `category` in `funder`, `finance`, `international`.

### hub_hubmap

HubMap (`site/cth-static/hubs/hubs-data.json`). Geo is a single lat/lng per hub; several match national capital coordinates.

### portfolio_startup

No geo fields; legacy `nexus-latam-map.js` used country centroids + jitter (not used by ecosystem MapLibre).

### startup_onepager_s

Public `/s/{slug}` cards — country ribbon only.

### mentor_clp26

CLP26 mentor directory — country string only.

### investor_crm

Investors SPA JSON — `country` sparse; `geo_focus` is investment geography, not office location.

### idea_curated_imd_pe

Proxy subset; not a full BookStack export.

### idea_curated_epic

Epic Angels curated list; not map-backed.

### jury_clp26

Event jury cards — no location fields.

### policy_ecosystem

Policy nodes in ecosystem story — country metadata only (no map pins).

## Ecosystem actor precision (deployed bundle)

- `address`: **116**
- `city`: **32**
- `country`: **233**

## Regenerate

```bash
python3 ops/geo/location_audit.py
```
