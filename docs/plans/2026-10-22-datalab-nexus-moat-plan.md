# Datalab to Nexus moat plan

**Date:** 2026-10-22

**Status:** Plan only. Section 15 is decided. Do not implement map, app, or deploy work until Gideon gives a broader GO. **Shortlist GO (voice, 22 Oct 16:47 COT):** add round 1 mining and logistics names from the sustainability report mapping only. No map changes in this edit.

**Mark on GTM inputs:** The company list came from the GTM Strategy desk. Round 1 verticals are decided in section 15. The demo format and the personas stay a GTM hypothesis. The source note is plan `bc-f31a71df`. This file stores company names only.

This file does not change the app. This file does not change the data. This file does not deploy a site.

## 1. Purpose

CleantechHUB (CTH) has a demand side and a supply side.

Datalab finds a gap. Nexus finds the actors that can close the gap.

ClimateLaunchpad (CLP) prepares the startups. The CTH Academy prepares the startups.

The go-to-market shows Datalab gap results to a corporate Sustainability Officer (CSO). The first country is Colombia.

The first milestone is the CSO demo path. The path is Move 1 plus Move 4. Move 3 runs in parallel. Move 3 must finish before a CSO sees the demo.

## 2. Facts on 2026-10-22

The counts below are from `main` before PR 101 merged. This plan does not restate the count after that merge.

| Item | Count |
| --- | ---: |
| Actors in `static/ecosystem/data/actors.json` | 381 |
| Public relations | 40 |
| Relations in the bundle | 85 |
| Hidden relations | 45 |
| Peru actors | 293 |
| El Salvador actors | 77 |
| Colombia actors | 6 |
| Actors with `geo.precision` `address` | 116 |
| Actors with `geo.precision` `city` | 32 |
| Actors with `geo.precision` `country` | 233 |

A public relation in that count has `verified: true`, a `source_url`, and a verbatim quote. `scripts/ecosystem/verify_relation_quotes.py` checks the quote. The source must name both actors and the relation. Section 15 item 25 exempts CTH cohort data. That exemption is not in the script yet.

`ops/ecosystem/UNVERIFIED-RELATIONS.md` records 40 public relations and 45 hidden relations. The file date is 2026-10-21.

PR 101 is merged. The merge time is 22 Oct 2026, 14:03 UTC. DECIDED. It is live. The demo may use a relation from that merge when the relation is on `main`.

The map page is `static/ecosystem/index.html`. The public URL is `https://nexus.cleantechhub.net/ecosystem/`. On 2026-10-22 the page and the JSON return HTTP 200.

`static/ecosystem/geo-utils.mjs` plots a pin only when `geo.precision` is `address`. Any other actor is location unknown. The page has a location-unknown panel.

The Peru ingest is `scripts/ecosystem/merge_peru_mapa_2026.py`. The source name on 279 actors is `Mapa de Actores Perú 2026`. The script strips email, Google Drive links, and Canva links. The script also contains city-center coordinates. Do not copy those coordinates.

The relation loop uses three scripts.

1. `scripts/ecosystem/build_graph_relation_evidence.py` holds the quote catalog.
2. `scripts/ecosystem/sync_graph_relation_sources.py` writes `relations.json` and `ops/ecosystem/UNVERIFIED-RELATIONS.md`.
3. `scripts/ecosystem/verify_relation_quotes.py` fetches each public page and checks the quote.

`scripts/ecosystem/build_public_data.py` drops notes, email, phone, and Drive links. Add a Canva strip in that script when a later job touches it. The journey view already blocks Drive links and Canva links.

`static/ecosystem/data/README.md` still says Peru 201 and Colombia 8. Those figures are stale. Use `actors.json`.

Colombia actors in the bundle:

| Id | Category | Pin |
| --- | --- | --- |
| `co-fenoge` | funder | location unknown |
| `co-bancoldex` | finance | address |
| `co-minenergia` | government | location unknown |
| `co-creg` | government | location unknown |
| `co-upme` | government | location unknown |
| `co-ipse` | government | location unknown |

`co-ipse` carries the source string `Mapa de Actores Perú 2026`. Correct that string when a job edits the actor.

Two Colombia relations are public. FENOGE to IPSE is `funds_layer`. UPME to IPSE is `regulates_layer`. Three Colombia fund relations stay hidden.

The startup portfolio has 156 startups. The file is `site/nexus-assets/previews/startups-redesign-20261016/portfolio-core.json`. Colombia (`c` = `CO`) has 145 rows. Portfolio themes are Circular (`CE`), Bioeconomy (`BIO`), and Energy (`EN`). Colombia location precision is address 10, city 56, country 49, unknown 17, and missing 13.

Those portfolio themes are not the GTM sector list. A CT code list exists on `site/nexus-www/startup-portfolio.html`. Examples are `CT-EN-*`, `CT-AF-*`, and `CT-BU-*`. That list is not a Datalab gap taxonomy.

Journey steps in `static/ecosystem/journey.mjs` are `challenge`, `policy`, `hubs`, `data`, `partnerships`, and `capital`. Portfolio startup stages include `Pre-Seed`, `Seed`, `Pre-Series A`, and `Series B+`. Keep the journey step and the startup stage as two fields.

The Nexus home file is `site/nexus-www/nexus-homepage.html`. Caddy serves it at `/p/home`. The page contains a demo block titled `Actividad reciente`. The four lines name EcoPack Colombia, Adriana Morales, DGGF Netherlands, and CLAC25 Batch. On 2026-10-22 the live page still shows that block. The page greeting is an internal staff greeting.

The text `+10 Millons Capital Raised` is not in this repo. It is not on `/p/home`. It is an Elementor heading on `https://cleantechhub.net/`. The same row shows five more headings. The headings are `+ 8 países`, `+5 Megatons to CO2 save`, `+40 Ecosystem partners`, `+1000 Climate solutions supported`, and `+50 Millions Capital Leveraged`. The apex site is not a file in this repo. `ops/Caddyfile` has no `cleantechhub.net` site block.

Deploy from main uses `scripts/deploy_nexus_live.sh`. The script writes a backup and `rollback.sh`. Geo apply uses `ops/ecosystem/apply_live.sh`. That script also writes a backup and a rollback script. Run either script only after the GitHub PR is on `main`.

## 3. First milestone

**Name:** CSO demo.

**Path:** Move 1 and Move 4.

**Parallel gate:** Move 3A. A CSO demo must not show the demo activity feed. A CSO demo must not show the unsourced banner.

**Owner of the HTML teaser:** the Presentations desk. This milestone hands that desk a JSON file. This milestone does not build the HTML.

**Company bound:** The name list is the 21 Wave 1 companies in section 5.4. Round 1 uses the four verticals in section 5.1. Oil and gas names stay on the list. They are out of round 1. Each gap comes only from that company's own published sustainability report. The supply side is the startups and funders that can close those gaps.

**Walkthrough company:** One Wave 1 name. Gideon picks that name.

**Later work:** The 13 Wave 2 companies, Move 2, Move 3B, and the paid workshop.

## 4. Minimum scope of the demo

The demo has three parts. The parts are the teaser, the 20-minute walkthrough, and the Colombia map slice.

The teaser is free. The teaser is 1 to 2 pages. The teaser contains a company profile, the top 5 gaps, and 3 to 5 matches for each gap.

Build the company profile from public data. A BVC filing may support the profile. A gap comes only from that company's own published sustainability report. The company must be one Round 1 name from Wave 1.

Rank exactly five gaps for a full teaser. Give each gap 3 to 5 matches. Give each match a public URL and a verbatim quote. Drop a match that has no quote. Record a shortfall when a gap has fewer than 3 matches. Do not add a filler match.

Keep the 2-page limit. Print the gap rank, the gap title, the match name, and the source link. Keep the full quote in the JSON. Read two or three quotes aloud in the walkthrough.

The walkthrough lasts 20 minutes. Use the teaser and the ecosystem map. Do not open `/p/home` in the walkthrough.

The map name list shows the 21 Wave 1 companies. Round 1 work uses the four verticals in section 5.1. It hides the 13 Wave 2 names. Show a pin only for a verified street address. Show the pin only. Show no address text. Show location unknown for every other actor. Show a `public_quote` relation only when the quote check passes. Show a `cth_cohort` relation when the CTH page publishes the fact. No quote is needed for that row.

The milestone is complete when all of these tests pass.

1. The teaser JSON validates against the contract in section 8.
2. Every `public_quote` match has a public quote on the cited page. A `cth_cohort` match uses the CTH page. It does not need a quote.
3. The teaser uses one Wave 1 company, and Gideon has picked that name.
4. The map shows no Colombia pin without `precision` `address`. A Colombia pin shows the pin only. It shows no address text.
5. `/p/home` has no `Actividad reciente` block.
6. `https://cleantechhub.net/` has no `+10 Millons Capital Raised` heading. The removal has a backup and a rollback. The other five headings stay.
7. The demo files contain no personal email, no phone number, no home address, no Drive link, and no Canva link.

## 5. GTM desk inputs

Plan id: `bc-f31a71df`.

The company list is from the GTM Strategy desk. Round 1 verticals are decided in section 15. Mark the demo format and the personas **GTM hypothesis**.

### 5.1 Sectors

DECIDED. Voice, 22 Oct 10:03 COT. Round 1 verticals are the sectors below. Oil and gas are out.

| Order | Vertical | Round 1 |
| ---: | --- | --- |
| 1 | Energy and utilities | Yes |
| 2 | Mining | Yes |
| 3 | Agribusiness and food | Yes |
| 4 | Logistics | Yes |

Verticals are sectors. A sector connects to a theme. Logistics connects to clean air. Themes are Nature Challenges. Section 15 states that rule.

Nature Challenges cover environment, climate, and nature only. Social and governance are out of scope. The names align with the GRI Topic Standards vocabulary. The list stays curated. Bosque Seco is a project. Bosque Seco is not a theme.

The Colombia CSO demo is first. Round 1 uses Wave 1 companies in these four verticals. Banking and insurance, construction, waste services, and oil and gas stay on the Wave 1 name list. They are out of round 1. Wave 1 has no mining name. Wave 1 has no logistics name. Do not add a Wave 2 name to fill that gap.

### 5.2 Demo format

The offer is a free teaser of 1 to 2 pages. The teaser is a gap snapshot.

The snapshot has three blocks.

1. A company profile from public data.
2. The top 5 ranked gaps.
3. 3 to 5 Nexus startups or funders for each gap.

A 20-minute CSO walkthrough follows the teaser. A paid workshop comes after the walkthrough. The paid workshop is outside this milestone.

The Presentations desk builds any HTML version of the teaser.

### 5.3 Personas

The primary persona is the CSO or the head of sustainability. The employer is a large Colombian corporate. The corporate is listed on the BVC, or the corporate has a published GRI report.

The secondary persona is the head of ESG reporting or the head of procurement.

### 5.4 Company list

The desk sent these company names. Store company names only. Store no contact names.

Wave 1 has a warm contact. A Datalab profile already exists. The first map wave uses Wave 1 only.

| Company | Working sector |
| --- | --- |
| Bancolombia | Banking and insurance |
| Davivienda | Banking and insurance |
| SURA | Banking and insurance |
| BBVA | Banking and insurance |
| Banco Popular | Banking and insurance |
| ISA | Energy and utilities |
| GEB (via TGI) | Energy and utilities |
| Enel | Energy and utilities |
| Celsia | Energy and utilities |
| EPM | Energy and utilities |
| Promigas | Energy and utilities |
| Ecopetrol | Oil and gas |
| Parex | Oil and gas |
| Terpel | Oil and gas |
| Alqueria | Food and consumer |
| Nutresa | Food and consumer |
| Juan Valdez | Food and consumer |
| Alpina | Food and consumer |
| Argos | Construction |
| Pavimentos Colombia | Construction |
| Interaseo | Waste services |

The desk label `Food and consumer` is the round 1 vertical agribusiness and food. Interaseo stays on the Wave 1 name list. Waste services is not a round 1 vertical. Read gaps only from each company's own published sustainability report.

`GEB (via TGI)` is the desk string. Cite the public report that names GEB, TGI, or both. Use the name the report uses.

Wave 2 is the next set of Datalab profiles. Keep every Wave 2 name off the first map wave.

Wave 2 names: Banco de Bogota, Amarilo, Colsubsidio, Fedepalma, Sodimac, Avianca, Aris Mining, Bavaria, Banco de Occidente, Comfama, Cafam, Claro, GeoPark.

### 5.4.1 Round 1 mining and logistics shortlist (mapping picks)

**Scope:** Shortlist only. Do not add these rows to the ecosystem map in this edit.

**Sustainability report mapping inventory:** On 22 Oct 2026 this inventory is **not** in `ops/`, `docs/`, or `data/` in the `cth-nexus` repo. The picks below come from the Datalab Colombia corporate sustainability report mapping (October 2026 harvest: one profile per company with a published report URL). Per-company mapping row: `https://datalab.cleantechhub.net/app/js/co-profile-<slug>.js`. A git copy under `ops/datalab/` is still pending. Section 15 item 27 covers the Drive copy. Do not use Wave 2 names to fill these sectors.

**Selection rules applied:** Section 5.3 (large Colombian corporate with a published GRI-style sustainability report). Section 15 item 4 (gaps come only from that company's own published sustainability report). Section 5.4 (Wave 1 uses warm contacts and existing Datalab profiles where the desk already named the company). Promigas and TGI stay on the desk Wave 1 list as energy and utilities. They are not duplicated here.

| Company | Round 1 vertical | Report year | Published sustainability report URL | Mapping |
| --- | --- | ---: | --- | --- |
| Cerrejón | Mining | 2024 | https://www.cerrejon.com/.rest/api/v1/documents/496364a49081ce531e85660822110e0a/informe-sostenibilidad-2024.pdf | Picked from mapping (`co-profile-cerrejon.js`) |
| Cerro Matoso S.A. | Mining | 2024 | https://cerromatoso.com.co/wp-content/uploads/2025/07/REPORTE-DE-SOSTENIBILIDAD-2024-COMPLETO.pdf | Picked from mapping (`co-profile-cerro-matoso-s-a.js`) |
| Mineros S.A. | Mining | 2023 | https://files.tryflowdrive.com/348/file-5c22ab22-c842-49aa-bd65-e9caace9cd3a_2023_Memoria_de_Sostenibilidad_Mineros-VF.pdf | Picked from mapping (`co-profile-mineros-s-a.js`) |
| Acerías Paz del Río S.A. | Mining | 2023 | https://www.pazdelrio.com.co/wp-content/uploads/2024/05/informe_sostenibilidad_2023.pdf | Picked from mapping (`co-profile-acerias-paz-del-rio-s-a.js`) |
| Cenit Transporte y Logística de Hidrocarburos S.A.S. | Logistics | 2024 | https://cenit-transporte.com/wp-content/uploads/2025/10/INFORME%20SOSTENIBILIDAD%20CENIT%202024.pdf | Picked from mapping (`co-profile-cenit-transporte-y-logistica-de-hidrocarburos-s-a-s.js`) |
| Oleoducto de Colombia S.A. | Logistics | 2024 | https://www.oleoductodecolombia.com/wp-content/uploads/2025/04/NS_Informe_Integrado_2024_26_marzo_compressed-1.pdf | Picked from mapping (`co-profile-oleoducto-de-colombia-s-a.js`) |
| Oleoducto de los Llanos Orientales S.A. | Logistics | 2024 | https://www.odl.com.co/wp-content/uploads/2025/05/RIGS_ODL_2024_2504.pdf | Picked from mapping (`co-profile-oleoducto-de-los-llanos-orientales-s-a.js`) |
| Palermo Sociedad Portuaria | Logistics | 2024 | https://palermosociedadportuaria.com/wp-content/uploads/2026/01/Informe-de-sostenibilidad-V6.pdf | Picked from mapping (`co-profile-palermo-sociedad-portuaria.js`) |

## 6. Questions for the GTM Strategy desk

Section 15 closes the round 1 verticals, the banner, and the gap source. These questions remain. Mark an answer **GTM hypothesis** until the desk replies.

1. Which Round 1 company is the first 20-minute walkthrough?
2. Confirm the working sector label for each Wave 1 name, including Interaseo.
3. Confirm the primary persona and the secondary persona.
4. Confirm that the teaser stays at 1 to 2 pages when the quote text stays in the JSON.
5. Confirm the 20-minute walkthrough and the later paid workshop.
6. Give the public source for each of the five apex headings that stay.
7. State whether a startup name in the teaser needs founder consent.
8. State the handoff format that the Presentations desk needs.

## 7. Move 1 — Gap-to-match shortlist

### Scope

Link one gap to one Nature Challenge, one journey step, and one startup stage. Attach 3 to 5 matches. A match is a startup or a funder. Each match has a public source. The theme is a Nature Challenge. Section 15 states that rule.

The output size is the teaser. A full teaser has 5 gaps. A full teaser has 15 to 25 matches.

Two match kinds exist.

- `theme_match`: the quote names the startup or the funder and the theme. The quote does not name the corporate.
- `actor_relation`: the quote names the corporate and the startup or funder, and it names the link.

A `theme_match` may appear in the teaser. A `theme_match` must not enter `relations.json`. An `actor_relation` with `evidence_type` `public_quote` may enter the graph only after `verify_relation_quotes.py` passes. A `cth_cohort` relation may enter the graph from the CTH page. No quote is needed.

Section 8 is on hold. DECIDED. Do not send section 8.

### Hands jobs

Run the maker and the checker as a pair. The checker starts after the maker delivers the files. Use model `composer-2.5` for both jobs.

**Maker.** Add `ops/datalab/teaser.schema.json` from section 8. Add one valid fixture and one invalid fixture. Build the valid fixture from the public FENOGE to IPSE quote. Leave `company.name` empty. Put no new row in `relations.json`.

**Checker.** Validate both fixtures. Open the cited URL. Confirm the quote is on the page. Fail the job if a match has an empty quote. Fail the job if the maker writes a `theme_match` into `relations.json`.

### Data sources

Use the public page cited on each match. Use `ops/ecosystem/graph_relation_evidence.json` for an existing public relation. Use the portfolio file for startup name, theme code, and startup stage. Use the company's own published sustainability report for each gap. A BVC filing may support the profile only.

Use a LinkedIn company link only when the company website shows it. Section 16 states the limit. Do not use an internal attendance list. Do not use a Drive file. Do not use a Canva file.

### Dependencies

Do not send section 8. The demo uses Round 1 verticals and Nature Challenges from section 15. Move 3A must be done before the walkthrough. The Presentations desk builds HTML from the JSON after the checker passes. This plan stays plan-only until Gideon gives GO.

### Effort

Size: medium for the schema, the fixtures, and one Wave 1 teaser. That teaser needs 15 to 25 quotes. Collect those quotes in batches of one gap. Do not build teasers for all 21 Wave 1 companies in the first pair.

### Acceptance tests

1. `teaser.schema.json` rejects a `public_quote` match with no `public_source_url`.
2. `teaser.schema.json` rejects a `public_quote` match with no `public_quote`. A `cth_cohort` match may omit the quote.
3. `teaser.schema.json` rejects a gap with more than 5 matches.
4. The valid fixture cites a page that contains the quote.
5. `relations.json` is unchanged by the pair.
6. The schema file stays in the repo as a draft. Do not send it.

### HITL

Stop if the teaser uses an oil and gas name in round 1. Stop before the JSON goes to the Presentations desk. Stop if a gap cannot reach 3 sourced matches. Record the shortfall. A CSO-ready file is blocked while any gap has `shortfall` `true`. Do not fill the gap with an unsourced name. Do not send section 8.

## 8. Data contract draft

**Status: on hold. DECIDED. Do not send section 8.**

**GTM size rule:** GTM hypothesis. Each gap has 3 to 5 matches. Each match has a public source.

The contract is a draft. Do not treat it as accepted.

### 8.1 Theme ids

This table is the old sector draft. It is not the theme list. Do not send it. Themes are Nature Challenges. Section 15 states that rule. `oil_gas` is not a round 1 vertical. Social and governance are out of scope. Bosque Seco is a project. Bosque Seco is not a theme.

| Theme id | GTM sector | Portfolio code today | First map wave |
| --- | --- | --- | --- |
| `banking_insurance` | 1 Banking and insurance | No financed-emissions field exists. | Wave 1 companies in this sector |
| `energy_utilities` | 2 Energy and utilities | `EN` is close. It is not the same id. | Wave 1 companies in this sector |
| `oil_gas` | 3 Oil and gas | No code confirmed in this plan. | Wave 1 companies in this sector |
| `food_consumer` | 4 Food and consumer | `BIO` and `CE` are not this id. | Wave 1 companies in this sector |
| `construction` | 5 Construction | `CT-BU-*` may overlap. | Wave 1 companies in this sector |

The name list covers the Wave 1 companies in section 5.4. Round 1 uses section 5.1. A gap comes only from that company's own published sustainability report. `waste_services` is not a theme id. Interaseo stays on the name list. Do not ask the Datalab desk for a theme id. Do not send section 8.

A Nature Challenge uses curated GRI Topic Standards words. A CT code is not that theme id. Do not treat this draft as accepted.

### 8.2 Stage fields

`journey_step` uses the journey keys: `challenge`, `policy`, `hubs`, `data`, `partnerships`, `capital`.

`startup_stage` uses the portfolio stages: `Pre-Seed`, `Seed`, `Pre-Series A`, `Series B+`.

Store both fields. Do not send section 8 to ask which field ranks the gap.

### 8.3 Schema

Save the schema as `ops/datalab/teaser.schema.json` only after Gideon gives GO. The text below is the old draft. Do not send it. The `oil_gas` enum value is not a round 1 theme.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://nexus.cleantechhub.net/schema/datalab-teaser.json",
  "title": "Datalab teaser",
  "type": "object",
  "additionalProperties": false,
  "required": ["contract_status", "gtm_status", "company", "gaps"],
  "properties": {
    "contract_status": {
      "const": "to agree with the Datalab desk"
    },
    "gtm_status": {
      "const": "GTM hypothesis"
    },
    "company": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "country", "persona", "profile_source_url", "profile_quote"],
      "properties": {
        "name": { "type": "string" },
        "country": { "const": "Colombia" },
        "persona": { "enum": ["cso", "esg_reporting", "procurement"] },
        "profile_source_url": { "type": "string", "minLength": 1 },
        "profile_quote": { "type": "string", "minLength": 1 },
        "bvc_listed": { "type": ["boolean", "null"] },
        "gri_report_url": { "type": ["string", "null"] }
      }
    },
    "gaps": {
      "type": "array",
      "minItems": 1,
      "maxItems": 5,
      "items": { "$ref": "#/$defs/gap" }
    }
  },
  "$defs": {
    "gap": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "gap_id",
        "rank",
        "title",
        "theme_id",
        "journey_step",
        "startup_stage",
        "statement",
        "evidence_url",
        "evidence_quote",
        "matches"
      ],
      "properties": {
        "gap_id": { "type": "string", "minLength": 1 },
        "rank": { "type": "integer", "minimum": 1, "maximum": 5 },
        "title": { "type": "string", "minLength": 1 },
        "theme_id": {
          "enum": [
            "banking_insurance",
            "energy_utilities",
            "oil_gas",
            "food_consumer",
            "construction"
          ]
        },
        "journey_step": {
          "enum": ["challenge", "policy", "hubs", "data", "partnerships", "capital"]
        },
        "startup_stage": {
          "enum": ["Pre-Seed", "Seed", "Pre-Series A", "Series B+"]
        },
        "statement": { "type": "string", "minLength": 1 },
        "evidence_url": { "type": "string", "minLength": 1 },
        "evidence_quote": { "type": "string", "minLength": 1 },
        "matches": {
          "type": "array",
          "minItems": 1,
          "maxItems": 5,
          "items": { "$ref": "#/$defs/match" }
        },
        "shortfall": { "type": "boolean" }
      }
    },
    "match": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "match_id",
        "actor_kind",
        "name",
        "claim_type",
        "public_source_url",
        "public_quote"
      ],
      "properties": {
        "match_id": { "type": "string", "minLength": 1 },
        "actor_ref": { "type": "string" },
        "actor_kind": { "enum": ["startup", "funder"] },
        "name": { "type": "string", "minLength": 1 },
        "claim_type": { "enum": ["theme_match", "actor_relation"] },
        "why": { "type": "string" },
        "public_source_url": { "type": "string", "minLength": 1 },
        "public_quote": { "type": "string", "minLength": 1 },
        "relation_type": { "type": "string" }
      }
    }
  }
}
```

A full teaser sets `shortfall` to `false` only when the gap has at least 3 matches. A gap with fewer than 3 matches sets `shortfall` to `true`. The schema allows one match so a shortfall file still validates. The checker fails a CSO-ready file when any gap has `shortfall` `true`.

A blank company name is allowed in a fixture. A CSO-ready file must use one Round 1 name. Gideon picks that name. The profile quote must appear on `profile_source_url`.

## 9. Move 4 — Colombia map for the Wave 1 companies

### Scope

Build the Colombia map with the same rules as the Peru map.

Use a public page or an official directory as the source. Strip email, phone, Drive links, and Canva links. Pin the actor only when the page gives a street address. Show the pin only. Show no address text. Set location unknown when the page gives no street address. Add a `public_quote` relation only through the quote catalog and `verify_relation_quotes.py`. A `cth_cohort` relation uses the CTH page. The script skips its quote check.

The name list is the 21 Wave 1 companies in section 5.4. Round 1 uses the four verticals in section 5.1. Oil and gas are out of round 1. Take each gap only from that company's own published sustainability report. Add the startups and funders that can close those gaps. Each match needs a public source.

Do not add the 13 Wave 2 names in this wave. Do not crawl a whole sector past the Wave 1 companies and their matches. Do not import all 145 Colombia portfolio rows. Add a portfolio startup only when a report gap matches it.

The current bundle actors stay in the file. Feature one of those actors on the wave-1 layer only when a Wave 1 report cites it. The actors are `co-fenoge`, `co-minenergia`, `co-creg`, `co-upme`, `co-ipse`, and `co-bancoldex`. `co-bancoldex` is a funder. Bancolombia is a separate Wave 1 company.

A city name is not an address. Do not use the city-center table in `merge_peru_mapa_2026.py`. Do not use a country capital as a pin.

Correct the `co-ipse` source string in the same job that edits the actor.

Store company names only. Do not add a person name.

### Hands jobs

Run the maker and the checker as a pair. Use model `composer-2.5` for both jobs.

**Maker.** Add the Wave 1 companies in sector batches. Use the batches in the effort line below. Copy the field shape from the Peru ingest. Set `geo.precision` to `address` only with a street address and a source URL. Set every other new actor to location unknown. Quote each gap from the company sustainability report. Add match quotes only in `ops/ecosystem/graph_relation_evidence.json` when the quote names both actors and the relation. Run the sync script.

**Checker.** Run `ops/geo/location_audit.py` logic against the new rows. Run `scripts/ecosystem/verify_relation_quotes.py`. Fail any new pin whose precision is not `address`. Fail a Colombia pin that shows address text. Fail any new `public_quote` relation that lacks a verbatim quote. Pass a `cth_cohort` relation that cites the CTH page and has no quote. Fail the job if a Wave 2 name appears on the wave-1 layer. Fail the job if a round 1 match uses an oil and gas name. Fail the job if a person name is in the new rows.

### Data sources

Use the company sustainability report for each gap. Use the organization website or an official directory for the address. Use the portfolio row only as a pointer to the startup website.

The Peru pattern lives in `scripts/ecosystem/merge_peru_mapa_2026.py`, `ops/geo/LOCATION-AUDIT.md`, and `static/ecosystem/geo-utils.mjs`.

Follow the LinkedIn rule in section 16. Do not geocode from a name plus a city.

### Dependencies

Section 5.4 names the companies. Move 1 supplies the match rule. The map job can add company records before every match quote exists. A company with no quoted gap stays on the map as location known or location unknown. It does not gain a fake match. Gideon picks the first walkthrough company from Wave 1 before that teaser is public.

### Effort

Size: large. The name list has 21 companies. Round 1 is four verticals. Oil and gas are out of round 1.

Round 1 batches:

1. Energy and utilities: ISA, GEB (via TGI), Enel, Celsia, EPM, Promigas.
2. Agribusiness and food: Alqueria, Nutresa, Juan Valdez, Alpina.
3. Mining: desk Wave 1 has no mining name. Round 1 shortlist names are in section 5.4.1 (mapping picks). Do not add a Wave 2 name.
4. Logistics: desk Wave 1 has no logistics name. Round 1 shortlist names are in section 5.4.1 (mapping picks). Do not add a Wave 2 name.

These names stay on the Wave 1 list. They are out of round 1.

- Banking and insurance: Bancolombia, Davivienda, SURA, BBVA, Banco Popular.
- Oil and gas: Ecopetrol, Parex, Terpel.
- Construction: Argos, Pavimentos Colombia.
- Waste services: Interaseo.

Each round 1 batch reads that company's own published sustainability report. It quotes only the gaps that report names. Then it attaches startups and funders that have a public source. Expect many location-unknown rows. The report quotes are the large part. One walkthrough teaser is still one company, not all 21.

### Acceptance tests

1. Every new Colombia pin has `precision` `address`, a street string in the data, and a `source_url`. The public pin shows no address text.
2. An actor with no street address has no lat-lng pin.
3. `verify_relation_quotes.py` exits 0. The script skips `evidence_type` `cth_cohort`.
4. The public bundle has no new email, phone, Drive link, or Canva link.
5. The wave-1 view lists the 21 Wave 1 companies and their sourced matches. It does not list a Wave 2 name.
6. `co-ipse` no longer cites the Peru map as its source.
7. Actor counts in the README match `actors.json` after the job, or the README points at `actors.json`.
8. Each round 1 gap cites that company's own published sustainability report and a verbatim quote. A company with no quote has no invented gap.
9. Round 1 adds no oil and gas match. Ecopetrol, Parex, and Terpel may stay on the name list.

### HITL

Stop before the first public Colombia batch. Gideon confirms the source list. Stop when a page gives only a city. Mark location unknown. Stop when a quote names only one actor. Leave the relation hidden.

## 10. Move 3 — Trust cleanup and proof

Split the move. 3A blocks the demo. 3B waits for consent.

### 10.1 Move 3A — Trust cleanup

#### Scope

Remove the demo activity feed from `site/nexus-www/nexus-homepage.html`. Remove the four demo lines with the block. Remove the unused activity CSS when no other block uses it.

Remove the banner `+10 Millons Capital Raised` from `https://cleantechhub.net/`. DECIDED. Take a backup before the edit. Keep a rollback. Do not invent a new number.

The banner is not in this Git repo. Find the WordPress or Elementor source in the implementation job. Record the removal in a tracked change. This plan does not name that path.

The same row has five more headings. Section 2 lists them. DECIDED. Those five headings stay. Do not edit them in this job.

#### Hands jobs

Run the maker and the checker as a pair. Use model `composer-2.5` for both jobs. Do not start this pair in PR 102. Start it after Gideon gives GO. It does not wait for section 8.

**Maker.** Delete the `Actividad reciente` block from the Nexus home file. Prepare the banner change as text. Do not deploy it. Do not edit the live WordPress site inside this pair.

**Checker.** Open the changed HTML. Confirm the four demo names are gone. Confirm the staff greeting is unchanged. Search the repo for `Millons`. Confirm the repo still has no banner string. Fetch `https://cleantechhub.net/` and record that the live heading is still present until the WordPress edit lands.

#### Data sources

Use `site/nexus-www/nexus-homepage.html`. Use the live page `https://nexus.cleantechhub.net/p/home`. Use the live page `https://cleantechhub.net/`.

#### Dependencies

The banner edit needs the WordPress source. Find that source in the implementation job. Take a backup. Keep a rollback. The Nexus HTML edit needs a GitHub PR before deploy. Deploy from `main` only. Use `scripts/deploy_nexus_live.sh`.

#### Effort

Size: small. One HTML block is in this repo. The banner is one heading outside the repo.

#### Acceptance tests

1. `nexus-homepage.html` contains no `Actividad reciente` block.
2. The file contains no `EcoPack Colombia` string.
3. The file contains no `Adriana Morales` string.
4. The live `/p/home` page matches `main` after deploy.
5. The live apex page does not show `+10 Millons Capital Raised`.
6. The other five headings in section 2 still show.
7. The banner edit has a backup and a rollback.
8. No new capital number appears without a source.

#### HITL

Stop before the WordPress edit. The removal is decided. The other five headings stay. Stop before deploy. Deploy from `main` only. Use a backup and a rollback.

### 10.2 Move 3B — Short cases

#### Scope

Publish two or three short cases. One case is Air4U. One case is a CLP startup with a public funder match. A third case is optional.

Each case needs a public source and the founder's consent. Store the consent outside the public bundle. Do not put the consent file in git if it holds personal data.

Air4U has a public one-pager at `onepagers/sites/air4u/index.html`. The page names Miguel Ángel Rozo and `https://air4u.co/`. That page is not consent for a new case.

A CLP funder match must already be a public relation on `main`. PR 101 is live. DECIDED. Use a relation from that merge only when the relation is on `main`. Prefer a Colombia match when one exists on `main`. Wait for the quote check on a third-party claim.

The cases are not part of the minimum demo. Ship the demo without the cases when consent is missing.

#### Hands jobs

Run the maker and the checker as a pair after consent exists. Use model `composer-2.5` for both jobs.

**Maker.** Write two short case files under `docs/cases/`. Each file has the claim, the source URL, the quote, and a consent id. Add no personal email or phone.

**Checker.** Open each source URL. Confirm the quote. Confirm the consent id exists in Odoo. Fail a case that cites a relation that is not on `main`.

#### Data sources

Use the public source named in the case. Use the founder consent record. Use `relations.json` on `main` for a funder match.

#### Dependencies

3A is independent. 3B waits for consent. A funder case waits for a public relation on `main`.

#### Effort

Size: small after consent. Two short files. The wait is the consent, not the writing.

#### Acceptance tests

1. Each case file has a quote that is on the source page.
2. Each case file has a consent id.
3. The public page shows no personal email or phone.
4. The funder case cites a relation that `verify_relation_quotes.py` accepts on `main`.

#### HITL

Stop until the founder consents. Stop if the founder limits the wording. Use that wording.

## 11. Move 2 — Verified-relations loop

### Scope

Each CLP touchpoint, Academy touchpoint, and investor-matching touchpoint can add one verified relation. Log the outcome in the private tier. The outcome is `meeting`, `pilot`, `money`, or `none`.

The public count today is 40. The aim is more than 200 public relations. The aim does not override the quote rule for a third-party claim.

A `public_quote` relation still needs a public source. The source must name both actors and the relation. The quote must be verbatim on that page. An attendance list is not a public source. An intro email is not a public source. A staff note is not a public source.

CTH cohort data is exempt. Decided (Gideon 22 Oct 10:02 COT). The cohorts are CLP, the Academy, and other CTH programmes. CTH may publish that data on its own website. No quote is needed. No outside source is needed. No outside location is needed beyond CTH's own publication.

Put third-party records in Odoo until a public page carries the quote. Put cohort facts on the CTH page. Section 12 is the field map. Do not add a new private file in git. Promote a third-party row only when a public page carries the quote. Publish a `cth_cohort` row from the CTH page with no quote.

Keep batches small. A batch of 10 new quotes is easier to check than a batch of 50.

### Prerequisite pair

This pair runs before outcome logs for ecosystem actors and investors. It needs Gideon's GO. Use model `composer-2.5` for the maker and the checker.

**Maker.** Import ecosystem actors and investors into Odoo `res.partner` as companies only. Add `odoo_id` on the actor records in `static/ecosystem/data/actors.json`. Write no personal data in the repo.

**Checker.** Confirm each new partner is a company. Confirm the repo diff has no email, no phone, and no home address. Confirm each imported actor has an `odoo_id`. Fail the job if the public site reads Odoo.

### Hands jobs

Run the maker and the checker as a pair. Use model `composer-2.5` for both jobs. Start the pair after the CSO demo milestone. Start it after the prerequisite pair for ecosystem actors and investors. Do not grow the public count before the demo gate.

**Maker.** Log one sample outcome in Odoo. Use the field map in section 12. Add no file under `ops/ecosystem/` for that sample. Add no public relation in the sample.

**Checker.** Confirm `actors.json` and `relations.json` have no private comms field. Run `verify_relation_quotes.py`. Fail the job if the sample outcome appears in `static/ecosystem/data/`.

Later batches use the same pair shape. The maker adds quotes. The checker runs the script.

### Data sources

Use an outside page for a `public_quote` relation. Use the CTH page for a `cth_cohort` relation. Use Odoo for the private outcome. CLP, Academy, and investor-matching staff supply the private outcome. They do not supply a third-party quote.

### Dependencies

Gideon has named Odoo as the private store. The import pair still needs his GO. The public rule is already in force. Move 2 does not block the CSO demo.

### Effort

Size: large for the prerequisite pair. That pair covers the ecosystem actor file and the investor file. Size: medium for the later quote batches. Each batch is small. Do not schedule one job that adds 160 relations.

### Acceptance tests

1. The sample outcome is absent from `static/ecosystem/data/`.
2. `verify_relation_quotes.py` exits 0. The script skips `evidence_type` `cth_cohort`.
3. Every new `public_quote` relation has a quote on the live page. A `cth_cohort` relation has no quote check. Its source is the CTH page.
4. The public count rises only by rows that pass the script.
5. Hidden rows stay `verified: false`.
6. The sync script deletes a self-loop row. The script does not keep a self-loop as a hidden row.

### HITL

Stop when a `public_quote` is almost right but not verbatim. Leave that row hidden. Do not hide a `cth_cohort` row for a missing quote. Stop when the page names one actor only. A human accepts a borderline name variant. The script result wins over a model opinion for a `public_quote` row.

## 12. Private evidence tier

**Status:** Odoo is the system of record. Do not create a new private file.

**Note (voice, 22 Oct 09:55 COT):** Gideon: every actor that has a Nexus actor card also exists in Odoo, the CTH ERP. Odoo keeps the private comms data.

**Claim mark:** Gideon statement; repo confirms the CLP26 partner sync; gap on ecosystem actors and investors.

### What the repo confirms

Odoo `res.partner` is the source of truth for CLP26 startups, founders, and mentors.

- `scripts/build_portfolio_s_profiles.py` line 169 says the profile is synced from BookStack Startup Portfolio plus Odoo (SoT).
- `app/cth-nexus/api/handlers/odoo.py` function `upsert_mentor` writes mentors on `res.partner`.
- `app/nexus-ideas/scripts/epic_odoo_wiki_sync.py` copies Odoo to the wiki.
- `app/nexus-ideas/scripts/epic_founders_pipeline.py` copies Odoo to the wiki and then to Nexus.

The public site does not read Odoo. A `public_quote` relation still needs `public_source_url` and `public_quote`. A `cth_cohort` relation does not need a quote. Its source is the CTH page that publishes the fact.

### What the repo does not confirm

`static/ecosystem/data/actors.json` has no `odoo_id` and no Odoo sync. Many of those rows use the source `Mapa de Actores Perú 2026`. `site/investors/data/investors.json` has no `odoo_id` and no Odoo sync.

The repo does not show a model for the outcomes `meeting`, `pilot`, and `money`. `upsert_mentor` does write a `mail.message` on `res.partner`. That message is an onboarding note. It is not the outcome log.

### Field map

Keep this map in this plan. Do not add a schema file.

| Plan field | Odoo record |
| --- | --- |
| `actors` | `res.partner`, company only |
| `touchpoint` | A note, an activity, or a custom model on that partner |
| `outcome` | The same note, activity, or custom model |
| `internal_record_id` | The Odoo id |
| `consent_to_publish` | A field on the Odoo record |
| `public_source_url` | Public relation only. Odoo does not feed the public site. |
| `public_quote` | Public relation only. Odoo does not feed the public site. |

`touchpoint` uses `clp`, `academy`, or `investor_matching`. `outcome` uses `meeting`, `pilot`, `money`, or `none`. Gideon names the Odoo model for that pair before staff log outcomes.

The Move 2 prerequisite pair imports ecosystem actors and investors as companies. It adds `odoo_id` on the actor records. It writes no personal data in the repo. Section 15 item 17 decides that import. Run it only after the implementation GO. This plan does not run it.

Secrets for the Odoo connection stay in Infisical. Do not commit them.

### Public card field set (approved by Gideon 22 Oct)

Voice, 22 Oct 09:56 COT. Decided. A public actor card may show only these fields.

- Name.
- Description.
- Location.
- Website.
- Relation type.
- Public URL.
- A verbatim quote from that URL.
- Date of access.
- Public office address.
- An outcome only when the public source states that outcome.

### Public pages must not show

- An attendance list.
- An intro email.
- A personal email.
- A phone number.
- A home address.
- A Google Drive link.
- A Canva link.
- A staff note.
- A match score that is a staff opinion.
- An outcome that exists only in a CTH record.

`consent_to_publish` does not replace the quote rule for a third-party claim. A `public_quote` relation still needs `public_source_url` and `public_quote`. A `cth_cohort` relation does not need a quote. Its source is the CTH page. The cohort guardrails are decided. The privacy ban still applies. Money or a pilot needs the startup's consent. Only facts from CTH-run programmes count.

**Proposal.** Add a relation field `evidence_type`. The values are `public_quote` and `cth_cohort`. For `cth_cohort`, the source is the CTH page that publishes the fact. `verify_relation_quotes.py` skips the quote check. This implementation is a proposal.

### Open question for Gideon

Do not decide this in the plan. The ecosystem card in `static/ecosystem/ecosystem.mjs` also shows a two-letter mark, a role (`card.ecosystem_role`), and a LinkedIn link. The same card shows a founding year, a category badge, and a relation count. Those fields are outside the approved set. Gideon says which of them stay.

## 13. Push back

These points disagree with a straight reading of the targets.

The target of 200 public relations can force weak relations. Keep the quote rule as the floor for a third-party claim. Count a `public_quote` row only when it passes `verify_relation_quotes.py`. Leave a weak third-party row hidden. A batch stops when the outside quotes run out.

The cohort exemption in section 15 stands. The guardrails are decided.

The privacy ban still applies. Do not publish a personal email, a phone number, a home address, an attendance list, a Drive link, or a Canva link.

An outcome such as money or a pilot needs the startup's consent before CTH publishes it.

Only facts from CTH-run programmes count. Those facts are participation, the cohort, and the programme. A third-party claim still needs a verbatim quote.

Move 3A is the cheapest pair. It must land before a CSO sees the product. It is a parallel gate. It is not the milestone. The milestone stays the CSO demo path.

Section 8 is on hold. DECIDED. Do not send section 8. Themes are Nature Challenges. A CT code is not a Nature Challenge. Bosque Seco is a project. Bosque Seco is not a theme.

The desk sent the company list. Round 1 verticals are decided. The working sector label on each name is a group. The company's own published sustainability report wins on the gap text. Portfolio codes `CE`, `BIO`, and `EN` are still not these sectors.

The teaser asks for 3 to 5 matches on each of 5 gaps. That is 15 to 25 public quotes. The Colombia graph has 6 actors and 2 public relations. It cannot fill the teaser. Use portfolio sites and other public pages. Drop the match when the quote is missing. A 2-page sheet cannot print every quote. Print the link. Keep the quote in the JSON.

A theme match is not a graph relation. Write it in the teaser only. Do not write it into `relations.json`.

Two stage fields exist. Do not merge the journey step with the startup stage.

The bad banner is on the public apex site. A PR in this repo cannot edit Elementor. Remove the figure. Take a backup. Keep a rollback. Do not type a replacement number. The other five headings stay. DECIDED.

`/p/home` is a public URL and an internal greeting. Do not use it as the CSO screen. The walkthrough uses the teaser and `/ecosystem/`.

Do not build 21 full teasers before the first walkthrough. The walkthrough uses one Round 1 company. The map lists all 21 Wave 1 names. Oil and gas stay on that list and stay out of round 1. Add a match only when the quote exists. A missing quote stays a shortfall. A CSO-ready file is blocked while any gap has `shortfall` `true`. Wave 2 stays off this map. Do not add Aris Mining or Avianca to fill mining or logistics.

PR 101 is live. DECIDED. The count in section 2 is the count before that merge. The demo uses `main`.

Privacy holds for every move. Do not publish a personal email, a phone number, a home address, a Drive link, or a Canva link.

The Peru city-center table is the wrong pattern for Colombia pins. Plot a pin only for a street address. Show the pin only. Show no address text. Use location unknown when the page gives no street address.

## 14. Sequence

| Order | Work | Blocks the demo | Pair model |
| --- | --- | --- | --- |
| A | Move 3A trust cleanup | Yes | `composer-2.5` maker and checker |
| A | Send section 6 to the GTM Strategy desk | No | Human |
| A | Move 1 schema and fixtures | No | `composer-2.5` maker and checker |
| B | Section 15 is decided. Implementation waits for GO. | Yes, until that GO | Human |
| B | Section 8 stays on hold. Do not send it. | No | Human |
| C | Move 1 full teaser, one gap per batch | Yes | `composer-2.5` maker and checker |
| C | Move 4 Colombia wave, 21 Wave 1 companies | Yes | `composer-2.5` maker and checker |
| D | Presentations desk builds the HTML teaser | Yes | That desk |
| D | 20-minute walkthrough | Demo event | Human |
| E | Move 2 prerequisite: import actors and investors to Odoo | No | `composer-2.5` maker and checker. Needs GO. |
| F | Move 2 outcome logs in Odoo, then quote batches | No | `composer-2.5` maker and checker |
| E | Move 3B cases after consent | No | `composer-2.5` maker and checker |
| E | Wave 2 companies, 13 names | No | Later pair |
| E | Paid workshop | No | GTM desk |

Rows with the same order letter may run in parallel. A later letter waits for the earlier letter.

The demo gate is the end of order D. Move 2 does not sit on that gate.

## 15. Decisions

Gideon settled every item below. The voice note is 22 Oct 10:03 COT. Each item is DECIDED. This plan stays plan-only until Gideon gives GO.

1. DECIDED. The Colombia CSO demo is first. The first map list is the 21 Wave 1 companies. Round 1 uses the four verticals in item 3.
2. DECIDED. Keep the 13 Wave 2 names off that wave.
3. DECIDED. Round 1 verticals are energy and utilities, mining, agribusiness and food, and logistics. Oil and gas are out.
4. DECIDED. Gaps come only from each company's own published sustainability report.
5. DECIDED. Interaseo stays on the Wave 1 name list. Waste services is not a round 1 vertical. Do not send section 8 for a theme id.
6. DECIDED. The first walkthrough company is one Round 1 name from Wave 1. This note does not name that company.
7. DECIDED. Store company names only. Do not add a person name.
8. DECIDED. The Datalab contract is on hold. Do not send section 8.
9. DECIDED. An internal file may set `shortfall` to `true`. That file is not CSO-ready.
10. DECIDED. A CSO-ready file is blocked while any gap has `shortfall` `true`.
11. DECIDED. `theme_match` is out of `relations.json`.
12. DECIDED. Remove the `+10 Millons` banner from the apex site. Take a backup. Keep a rollback.
13. DECIDED. The other five apex headings stay.
14. DECIDED. Remove the synthetic demo activity feed.
15. DECIDED. The private evidence tier is Odoo. Every actor with a Nexus card is in Odoo.
16. DECIDED. Public card fields stay as section 12 lists them.
17. DECIDED. Import ecosystem actors and investors to Odoo `res.partner` as companies only. Add `odoo_id` on the actor records. Do not run that import in this plan.
18. DECIDED. The privacy ban still applies. Do not publish a personal email, a phone, a home address, an attendance list, a Drive link, or a Canva link.
19. DECIDED. Remove the apex banner with a backup and a rollback. This plan does not name a WordPress path.
20. DECIDED. The Presentations desk owns the HTML teaser.
21. DECIDED. Deploy from `main` only. Use a backup and a rollback.
22. DECIDED. PR 101 is live. The demo may use a relation from that merge when the relation is on `main`.
23. DECIDED. Colombia pins show the pin only. They show no address text. A pin still needs `precision` `address`. An actor with no street address stays location unknown.
24. DECIDED. Use a LinkedIn company page link only when the company's own site links to it. Do not scrape LinkedIn. Do not log in. Do not use the box browser. Do not use a crawler. Anything more needs its own GO. Voice, 22 Oct 09:59 COT. Confirmed 22 Oct 10:03 COT.
    - Never log in to LinkedIn.
    - Never use LinkedIn in the box browser.
    - Never use LinkedIn in a headless crawler.
    - Store the URL, the date, and the citing page.
    - Use company pages only.
    - Do not use a person profile.
25. DECIDED. CTH cohort data is exempt from the verbatim-quote rule. The cohorts are CLP, the Academy, and other CTH programmes. The privacy ban still applies. Money or a pilot needs the startup's consent. Only facts from CTH-run programmes count. Voice, 22 Oct 10:02 COT. Confirmed 22 Oct 10:03 COT.
26. DECIDED. Secrets live in Infisical.
27. DECIDED. Make the Drive copy after these decisions settle. Do not make that copy in this plan.
28. DECIDED. Themes are Nature Challenges. They cover environment, climate, and nature only. Social and governance are out of scope.
29. DECIDED. Verticals are sectors. A sector connects to a theme. Logistics connects to clean air.
30. DECIDED. Nature Challenges align with the GRI Topic Standards vocabulary. They stay curated.
31. DECIDED. Bosque Seco is a project. Bosque Seco is not a theme.
32. DECIDED. PR 102 stays plan-only until Gideon gives GO.
33. DECIDED. Shortlist GO (voice, 22 Oct 16:47 COT). Add section 5.4.1 mining and logistics names from the sustainability report mapping only. No map changes in that edit.

Open question. Do not decide it here. The ecosystem card also shows a two-letter mark, a role, and a LinkedIn link. Gideon says which of those stay.

## 16. Hard rules

1. Open a GitHub PR before a live change.
2. Deploy from `main` only.
3. Run `scripts/deploy_nexus_live.sh` or `ops/ecosystem/apply_live.sh` only after that merge.
4. Keep the backup and the rollback script from those tools.
5. Patch `ops/Caddyfile`. Do not replace the file.
6. Patch the live Caddy file the same way. Run `caddy validate` before reload.
7. When a company's own public website links to its LinkedIn company page, record that link. Use that link. Do not scrape LinkedIn directly. Do not scrape LinkedIn broadly. Follow only a LinkedIn link that appears on the company's public site. Decided (Gideon 22 Oct), see constraint. Voice, 22 Oct 09:59 COT. Never log in to LinkedIn. Never use LinkedIn in the box browser. Never use LinkedIn in a headless crawler. The allowed data is the LinkedIn URL as found on the site, the date, and the citing page. Any extra LinkedIn data needs a sanctioned route and a separate GO. Use company pages only. Do not use a person profile.
8. Keep secrets in Infisical. The host name `secrets.cleantechhub.net` is the secrets endpoint. Do not copy a secret into git, into the Caddy file, or into this plan.
9. A `public_quote` relation needs a source that names both actors and the relation, plus a verbatim quote. A `cth_cohort` relation is exempt. Decided (Gideon 22 Oct 10:02 COT). The source is the CTH page that publishes the fact. No quote is needed. No outside source is needed. Proposal: `evidence_type` is `public_quote` or `cth_cohort`. `verify_relation_quotes.py` skips the quote check for `cth_cohort`.
10. A CSO-facing page must not show the synthetic demo activity feed. Remove the `+10 Millons` banner from the apex site. Take a backup. Keep a rollback. The other five headings stay.
11. Do not send section 8. The Datalab contract is on hold.
12. PR 102 stays plan-only until Gideon gives GO.
13. A Colombia pin shows the pin only. It shows no address text.
14. Themes are Nature Challenges. Social and governance are out of scope. Bosque Seco is a project, not a theme.
15. Make the Drive copy after section 15 settles. Do not make that copy in this plan.
