# HubMap location fixes (batch: `hubs`)

**Branch:** `cursor/hubs-fix-a7ad`  
**Base:** `cursor/location-audit-ef81` (audit PR #86)  
**Generated:** 2026-10-21  

## Scope

Five `hub_hubmap` rows in `site/cth-static/hubs/hubs-data.json` were plotted at city/national-capital coordinates with no `source_url`. This batch proposes verified-address pins per [LOCATION-AUDIT.md](../LOCATION-AUDIT.md) policy.

Deliverable: [`hubs.csv`](./hubs.csv) only (no bundle deploy in this PR).

## Summary counts

| Metric | Count |
|--------|------:|
| Hubs in audit | 5 |
| Resolved with `precision=address` + coords | 5 |
| Location unknown (no pin) | 0 |

## Per-hub notes

### `externado` — Universidad Externado de Colombia

- **Source:** [uexternado.edu.co/contacto](https://www.uexternado.edu.co/contacto/) — *Calle 12 No. 1-17 Este. Bogotá, Colombia.*
- **Geocode:** `Universidad Externado de Colombia, Bogotá` (`countrycodes=co`) → university amenity on Calle 12 (La Candelaria).
- **Sanity:** Replaces Bogotá-area pin at national-reference coords; lat/lng now on Externado campus.

### `el-salvador` — UTEC · REIN Hub El Salvador

- **Source:** [utec.edu.sv campus modal](https://www.utec.edu.sv/en/races/architecture) — *Campus Dr. José Mauricio Loucel, Escalón: 3a. calle Poniente Schafik Hándal y bulevar Constitución #301, colonia Escalón.*
- **Geocode:** `Boulevard Constitución 301, Colonia Escalón, San Salvador` (`countrycodes=sv`).
- **Sanity:** ~1.5 km from former San Salvador capital centroid; Colonia Escalón matches UTEC Loucel campus (CREA / innovation hub).

### `landivar` — Universidad Rafael Landívar

- **Source:** [principal.url.edu.gt/acerca-de](https://principal.url.edu.gt/acerca-de/) — footer *Vista Hermosa III, Zona 16, Guatemala, Centroamérica 01016* (Campus Central).
- **Geocode:** `Universidad Rafael Landívar, Zona 16, Ciudad de Guatemala` (`countrycodes=gt`) → university POI in Zona 16.
- **Sanity:** ~5 km from former Guatemala City capital centroid; published address is zona-level (common for URL); pin aligns with mapped campus in Zona 16.

### `emprende-up` — Emprende UP · Universidad del Pacífico

- **Source:** [up.edu.pe contacto](https://www.up.edu.pe/paginas/contactenos.aspx) — domicilio *Av. Salaverry N° 2020, distrito de Jesús María* (main campus; Emprende UP site has no street address).
- **Geocode:** `Universidad del Pacífico, Avenida Salaverry 2020, Jesús María, Lima` (`countrycodes=pe`).
- **Sanity:** ~4.2 km from former Lima centroid; matches UP main campus (Plaza Geis / Salaverry frontage).

### `lci-veritas` — Universidad LCI Veritas

- **Source:** [studyabroad.veritas.cr/contact-us](https://studyabroad.veritas.cr/contact-us/) — *Universidad VERITAS CPIES, Calle 31, Avenida 20, Zapote, San Jose, Costa Rica 10105* (official `veritas.cr` subdomain).
- **Geocode:** `Universidad Veritas, San José, Costa Rica` (`countrycodes=cr`) → university amenity on Avenida 20, Zapote.
- **Sanity:** Pin in Zapote, San José; replaces greater-metro centroid-style coords.

## Geocoding method

- Provider: [Nominatim](https://nominatim.openstreetmap.org/) (OpenStreetMap), **≥1 s between requests**, `User-Agent: cth-nexus-location-audit/1.0 (geo fix batch)`.
- Coordinates taken from the best match for the **published street/campus string** (prefer `university` / `amenity` over bare street interpolation when the institution is named on the source page).
- No Wikidata, capital centroids, jitter, or geocoder-only sources in `source_url`.

## Unknowns

None for this batch — all five hubs have an official published location on the entity (or parent university) site and a Nominatim sanity-checked coordinate pair.
