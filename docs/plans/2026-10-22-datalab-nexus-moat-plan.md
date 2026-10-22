# Datalab to Nexus moat plan

**Date:** 2026-10-22

**Status:** Plan only.

**Mark on GTM inputs:** The company list and the sector order came from the GTM Strategy desk. The demo format and the personas stay a GTM hypothesis. The source note is plan `bc-f31a71df`. This file stores company names only.

This file does not change the app. This file does not change the data. This file does not deploy a site.

## 1. Purpose

CleantechHUB (CTH) has a demand side and a supply side.

Datalab finds a gap. Nexus finds the actors that can close the gap.

ClimateLaunchpad (CLP) prepares the startups. The CTH Academy prepares the startups.

The go-to-market shows Datalab gap results to a corporate Sustainability Officer (CSO). The first country is Colombia.

The first milestone is the CSO demo path. The path is Move 1 plus Move 4. Move 3 runs in parallel. Move 3 must finish before a CSO sees the demo.

## 2. Facts on 2026-10-22

The counts below are from `main` in this repo.

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

A public relation has `verified: true`, a `source_url`, and a verbatim quote. `scripts/ecosystem/verify_relation_quotes.py` checks the quote. The source must name both actors and the relation.

`ops/ecosystem/UNVERIFIED-RELATIONS.md` records 40 public relations and 45 hidden relations. The file date is 2026-10-21.

Draft PR 101 is open. The PR body reports 47 public relations and 43 hidden relations. The PR is not merged. The live count stays 40. Do not use a PR 101 relation in the demo.

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

**Company bound:** The first map wave is the 21 Wave 1 companies in section 5.4. The gaps come from their public sustainability reports. The supply side is the startups and funders that can close those gaps.

**Walkthrough company:** One Wave 1 name. Gideon picks that name.

**Later work:** The 13 Wave 2 companies, Move 2, Move 3B, and the paid workshop.

## 4. Minimum scope of the demo

The demo has three parts. The parts are the teaser, the 20-minute walkthrough, and the Colombia map slice.

The teaser is free. The teaser is 1 to 2 pages. The teaser contains a company profile, the top 5 gaps, and 3 to 5 matches for each gap.

Build the company profile from public data. Use the company sustainability report. A BVC filing may support the profile. The company must be one Wave 1 name from section 5.4.

Rank exactly five gaps for a full teaser. Give each gap 3 to 5 matches. Give each match a public URL and a verbatim quote. Drop a match that has no quote. Record a shortfall when a gap has fewer than 3 matches. Do not add a filler match.

Keep the 2-page limit. Print the gap rank, the gap title, the match name, and the source link. Keep the full quote in the JSON. Read two or three quotes aloud in the walkthrough.

The walkthrough lasts 20 minutes. Use the teaser and the ecosystem map. Do not open `/p/home` in the walkthrough.

The map slice shows the 21 Wave 1 companies. It shows the gaps their sustainability reports name. It shows the startups and funders that can close those gaps. It hides the 13 Wave 2 names. Show a pin only for a verified street address. Show location unknown for every other actor. Show a public relation only when the quote check passes.

The milestone is complete when all of these tests pass.

1. The teaser JSON validates against the contract in section 8.
2. Every match has a public quote on the cited page.
3. The teaser uses one Wave 1 company, and Gideon has picked that name.
4. The map shows no Colombia pin without `precision` `address`.
5. `/p/home` has no `Actividad reciente` block.
6. `https://cleantechhub.net/` has no `+10 Millons Capital Raised` heading, or the heading has a public source on the page.
7. The demo files contain no personal email, no phone number, no home address, no Drive link, and no Canva link.

## 5. GTM desk inputs

Plan id: `bc-f31a71df`.

The company list and the sector order are from the GTM Strategy desk. Mark the demo format and the personas **GTM hypothesis**.

### 5.1 Sectors

Use this priority order. The desk replaced the earlier order.

| Order | Sector | Role |
| ---: | --- | --- |
| 1 | Banking and insurance | Top sector |
| 2 | Energy and utilities | Top sector |
| 3 | Oil and gas | Top sector |
| 4 | Food and consumer | Next |
| 5 | Construction | After food and consumer |

The first Colombia map wave is the Wave 1 company list. Wave 1 also includes food, construction, and one waste company. Section 5.4 lists the names. A sustainability report names the gaps. The report wins when it disagrees with the working sector label.

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

Interaseo is on Wave 1. The five sector names do not include waste. Keep Interaseo on the first map. Read its sustainability report for the gaps.

`GEB (via TGI)` is the desk string. Cite the public report that names GEB, TGI, or both. Use the name the report uses.

Wave 2 is the next set of Datalab profiles. Keep every Wave 2 name off the first map wave.

Wave 2 names: Banco de Bogota, Amarilo, Colsubsidio, Fedepalma, Sodimac, Avianca, Aris Mining, Bavaria, Banco de Occidente, Comfama, Cafam, Claro, GeoPark.

## 6. Questions for the GTM Strategy desk

The desk has sent the company list and the sector order. These questions remain. Mark an answer **GTM hypothesis** until the desk replies.

1. Which Wave 1 company is the first 20-minute walkthrough?
2. Confirm the working sector label for each Wave 1 name, including Interaseo.
3. Confirm the primary persona and the secondary persona.
4. Confirm that the teaser stays at 1 to 2 pages when the quote text stays in the JSON.
5. Confirm the 20-minute walkthrough and the later paid workshop.
6. State which figures on `cleantechhub.net` may remain.
7. Give the public source for each figure that remains.
8. State whether a startup name in the teaser needs founder consent.
9. State the handoff format that the Presentations desk needs.

## 7. Move 1 — Gap-to-match shortlist

### Scope

Link one Datalab gap to one Nexus theme, one journey step, and one startup stage. Attach 3 to 5 matches. A match is a startup or a funder. Each match has a public source.

The output size is the teaser. A full teaser has 5 gaps. A full teaser has 15 to 25 matches.

Two match kinds exist.

- `theme_match`: the quote names the startup or the funder and the theme. The quote does not name the corporate.
- `actor_relation`: the quote names the corporate and the startup or funder, and it names the link.

A `theme_match` may appear in the teaser. A `theme_match` must not enter `relations.json`. An `actor_relation` may enter the graph only after `verify_relation_quotes.py` passes.

The gap taxonomy in section 8 is a draft. The status line is **to agree with the Datalab desk**.

### Hands jobs

Run the maker and the checker as a pair. The checker starts after the maker delivers the files. Use model `composer-2.5` for both jobs.

**Maker.** Add `ops/datalab/teaser.schema.json` from section 8. Add one valid fixture and one invalid fixture. Build the valid fixture from the public FENOGE to IPSE quote. Leave `company.name` empty. Put no new row in `relations.json`.

**Checker.** Validate both fixtures. Open the cited URL. Confirm the quote is on the page. Fail the job if a match has an empty quote. Fail the job if the maker writes a `theme_match` into `relations.json`.

### Data sources

Use the public page cited on each match. Use `ops/ecosystem/graph_relation_evidence.json` for an existing public relation. Use the portfolio file for startup name, theme code, and startup stage. Use a GRI report or a BVC filing for the company profile after Gideon names the company.

Do not use LinkedIn. Do not use an internal attendance list. Do not use a Drive file. Do not use a Canva file.

### Dependencies

The Datalab desk must accept the taxonomy draft before a named teaser goes to a CSO. Gideon must name the company or accept a blank name. Move 3A must be done before the walkthrough. The Presentations desk builds HTML from the JSON after the checker passes.

### Effort

Size: medium for the schema, the fixtures, and one Wave 1 teaser. That teaser needs 15 to 25 quotes. Collect those quotes in batches of one gap. Do not build teasers for all 21 Wave 1 companies in the first pair.

### Acceptance tests

1. `teaser.schema.json` rejects a match with no `public_source_url`.
2. `teaser.schema.json` rejects a match with no `public_quote`.
3. `teaser.schema.json` rejects a gap with more than 5 matches.
4. The valid fixture cites a page that contains the quote.
5. `relations.json` is unchanged by the pair.
6. The status field on the schema is `to agree with the Datalab desk`.

### HITL

Stop if the teaser uses a name that is not on Wave 1. Stop before the JSON goes to the Presentations desk. Gideon picks the first Wave 1 name. Stop if the Datalab desk rejects a theme id. Stop if a gap cannot reach 3 sourced matches. Record the shortfall. Do not fill the gap with an unsourced name.

## 8. Data contract draft

**Status: to agree with the Datalab desk.**

**GTM size rule:** GTM hypothesis. Each gap has 3 to 5 matches. Each match has a public source.

The contract is a draft. Do not treat it as accepted.

### 8.1 Theme ids

These ids follow the GTM sector order. They are a draft.

| Theme id | GTM sector | Portfolio code today | First map wave |
| --- | --- | --- | --- |
| `banking_insurance` | 1 Banking and insurance | No financed-emissions field exists. | Wave 1 companies in this sector |
| `energy_utilities` | 2 Energy and utilities | `EN` is close. It is not the same id. | Wave 1 companies in this sector |
| `oil_gas` | 3 Oil and gas | No code confirmed in this plan. | Wave 1 companies in this sector |
| `food_consumer` | 4 Food and consumer | `BIO` and `CE` are not this id. | Wave 1 companies in this sector |
| `construction` | 5 Construction | `CT-BU-*` may overlap. | Wave 1 companies in this sector |

The first map wave covers the Wave 1 companies in section 5.4. It covers the gaps in their sustainability reports. It covers the startups and funders that can close those gaps. `waste_services` is not a theme id yet. Interaseo still stays on the map. The Datalab desk must give Interaseo a theme id.

The Datalab desk must accept each theme id. The desk must say whether a CT code may sit on a gap.

### 8.2 Stage fields

`journey_step` uses the journey keys: `challenge`, `policy`, `hubs`, `data`, `partnerships`, `capital`.

`startup_stage` uses the portfolio stages: `Pre-Seed`, `Seed`, `Pre-Series A`, `Series B+`.

The Datalab desk must say which field ranks the gap. Store both fields.

### 8.3 Schema

Save the schema as `ops/datalab/teaser.schema.json` in the Move 1 job. The text below is the draft.

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

A blank company name is allowed in a fixture. A CSO-ready file must use one Wave 1 name. Gideon picks that name. The profile quote must appear on `profile_source_url`.

## 9. Move 4 — Colombia map for the Wave 1 companies

### Scope

Build the Colombia map with the same rules as the Peru map.

Use a public page or an official directory as the source. Strip email, phone, Drive links, and Canva links. Pin the actor only when the page gives a street address. Set location unknown when the page gives no street address. Add a public relation only through the quote catalog and `verify_relation_quotes.py`.

The first wave is the 21 Wave 1 companies in section 5.4. Add each company. Take the gaps from that company's public sustainability report. Add the startups and funders that can close those gaps. Each match needs a public source.

Do not add the 13 Wave 2 names in this wave. Do not crawl a whole sector past the Wave 1 companies and their matches. Do not import all 145 Colombia portfolio rows. Add a portfolio startup only when a report gap matches it.

The current bundle actors stay in the file. Feature one of those actors on the wave-1 layer only when a Wave 1 report cites it. The actors are `co-fenoge`, `co-minenergia`, `co-creg`, `co-upme`, `co-ipse`, and `co-bancoldex`. `co-bancoldex` is a funder. Bancolombia is a separate Wave 1 company.

A city name is not an address. Do not use the city-center table in `merge_peru_mapa_2026.py`. Do not use a country capital as a pin.

Correct the `co-ipse` source string in the same job that edits the actor.

Store company names only. Do not add a person name.

### Hands jobs

Run the maker and the checker as a pair. Use model `composer-2.5` for both jobs.

**Maker.** Add the Wave 1 companies in sector batches. Use the batches in the effort line below. Copy the field shape from the Peru ingest. Set `geo.precision` to `address` only with a street address and a source URL. Set every other new actor to location unknown. Quote each gap from the company sustainability report. Add match quotes only in `ops/ecosystem/graph_relation_evidence.json` when the quote names both actors and the relation. Run the sync script.

**Checker.** Run `ops/geo/location_audit.py` logic against the new rows. Run `scripts/ecosystem/verify_relation_quotes.py`. Fail any new pin whose precision is not `address`. Fail any new public relation that lacks a verbatim quote. Fail the job if a Wave 2 name appears on the wave-1 layer. Fail the job if a person name is in the new rows.

### Data sources

Use the company sustainability report for each gap. Use the organization website or an official directory for the address. Use the portfolio row only as a pointer to the startup website.

The Peru pattern lives in `scripts/ecosystem/merge_peru_mapa_2026.py`, `ops/geo/LOCATION-AUDIT.md`, and `static/ecosystem/geo-utils.mjs`.

Do not scrape LinkedIn. Do not geocode from a name plus a city.

### Dependencies

Section 5.4 names the companies. Move 1 supplies the match rule. The map job can add company records before every match quote exists. A company with no quoted gap stays on the map as location known or location unknown. It does not gain a fake match. Gideon picks the first walkthrough company from Wave 1 before that teaser is public.

### Effort

Size: large. The wave has 21 companies. Split the work into six batches.

1. Banking and insurance: Bancolombia, Davivienda, SURA, BBVA, Banco Popular.
2. Energy and utilities: ISA, GEB (via TGI), Enel, Celsia, EPM, Promigas.
3. Oil and gas: Ecopetrol, Parex, Terpel.
4. Food and consumer: Alqueria, Nutresa, Juan Valdez, Alpina.
5. Construction: Argos, Pavimentos Colombia.
6. Waste services: Interaseo.

Each batch reads the public sustainability reports and quotes the gaps those reports name. Then it attaches startups and funders that have a public source. Expect many location-unknown rows. The report quotes are the large part. One walkthrough teaser is still one company, not all 21.

### Acceptance tests

1. Every new Colombia pin has `precision` `address`, a street string, and a `source_url`.
2. An actor with no street address has no lat-lng pin.
3. `verify_relation_quotes.py` exits 0.
4. The public bundle has no new email, phone, Drive link, or Canva link.
5. The wave-1 view lists the 21 Wave 1 companies and their sourced matches. It does not list a Wave 2 name.
6. `co-ipse` no longer cites the Peru map as its source.
7. Actor counts in the README match `actors.json` after the job, or the README points at `actors.json`.
8. Each wave-1 gap cites a sustainability report and a verbatim quote. A company with no quote has no invented gap.

### HITL

Stop before the first public Colombia batch. Gideon confirms the source list. Stop when a page gives only a city. Mark location unknown. Stop when a quote names only one actor. Leave the relation hidden.

## 10. Move 3 — Trust cleanup and proof

Split the move. 3A blocks the demo. 3B waits for consent.

### 10.1 Move 3A — Trust cleanup

#### Scope

Remove the demo activity feed from `site/nexus-www/nexus-homepage.html`. Remove the four demo lines with the block. Remove the unused activity CSS when no other block uses it.

Fix the banner `+10 Millons Capital Raised` on `https://cleantechhub.net/`. The word `Millons` is a typo. The figure has no source on the page. Remove the figure. Put a figure back only when the same page shows the source.

The banner is not in this Git repo. Find the WordPress or Elementor source before the edit. Record the replacement text in a tracked change. Do not invent a new number.

The same row has five more unsourced headings. Section 2 lists the headings. Touch those headings only after Gideon adds them to the job. The default job changes the named banner only.

#### Hands jobs

Run the maker and the checker as a pair. Use model `composer-2.5` for both jobs. Start this pair now. It does not wait for the Datalab desk.

**Maker.** Delete the `Actividad reciente` block from the Nexus home file. Prepare the banner change as text. Do not deploy it. Do not edit the live WordPress site inside this pair.

**Checker.** Open the changed HTML. Confirm the four demo names are gone. Confirm the staff greeting is unchanged. Search the repo for `Millons`. Confirm the repo still has no banner string. Fetch `https://cleantechhub.net/` and record that the live heading is still present until the WordPress edit lands.

#### Data sources

Use `site/nexus-www/nexus-homepage.html`. Use the live page `https://nexus.cleantechhub.net/p/home`. Use the live page `https://cleantechhub.net/`.

#### Dependencies

The banner edit needs the WordPress source. Gideon must point to that source. The Nexus HTML edit needs a GitHub PR before deploy. Deploy from `main` with `scripts/deploy_nexus_live.sh`.

#### Effort

Size: small. One HTML block is in this repo. The banner is one heading outside the repo.

#### Acceptance tests

1. `nexus-homepage.html` contains no `Actividad reciente` block.
2. The file contains no `EcoPack Colombia` string.
3. The file contains no `Adriana Morales` string.
4. The live `/p/home` page matches `main` after deploy.
5. The live apex page does not show `+10 Millons Capital Raised`, or the visible figure has a source on that page.
6. No new capital number appears without a source.

#### HITL

Stop before the WordPress edit. Gideon confirms the removal of the figure. Gideon says whether the other five headings are in scope. Stop before deploy. The PR must be on `main`.

### 10.2 Move 3B — Short cases

#### Scope

Publish two or three short cases. One case is Air4U. One case is a CLP startup with a public funder match. A third case is optional.

Each case needs a public source and the founder's consent. Store the consent outside the public bundle. Do not put the consent file in git if it holds personal data.

Air4U has a public one-pager at `onepagers/sites/air4u/index.html`. The page names Miguel Ángel Rozo and `https://air4u.co/`. That page is not consent for a new case.

A CLP funder match must already be a public relation on `main`. PR 101 is not on `main`. Do not use a PR 101 edge as the case source. Prefer a Colombia match when one exists on `main`. No Colombia startup-to-funder relation is public on `main` today. Wait until one passes the quote check.

The cases are not part of the minimum demo. Ship the demo without the cases when consent is missing.

#### Hands jobs

Run the maker and the checker as a pair after consent exists. Use model `composer-2.5` for both jobs.

**Maker.** Write two short case files under `docs/cases/`. Each file has the claim, the source URL, the quote, and a consent id. Add no personal email or phone.

**Checker.** Open each source URL. Confirm the quote. Confirm the consent id exists in the private store. Fail a case that cites PR 101.

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

The public count today is 40. The aim is more than 200 public relations. The aim does not override the quote rule.

A public relation still needs a public source. The source must name both actors and the relation. The quote must be verbatim on that page. An attendance list is not a public source. An intro email is not a public source. A staff note is not a public source.

Put those internal records in the private tier in section 12. Promote a private row only when a public page carries the quote.

Keep batches small. A batch of 10 new quotes is easier to check than a batch of 50.

### Hands jobs

Run the maker and the checker as a pair. Use model `composer-2.5` for both jobs. Start the pair after the CSO demo milestone. The schema draft may land earlier. Do not grow the public count before the demo gate.

**Maker.** Add `ops/ecosystem/private_evidence.schema.json` from section 12. Add one sample row in a private path that `build_public_data.py` does not read. Add no public relation in the sample.

**Checker.** Confirm `actors.json` and `relations.json` have no private field. Run `verify_relation_quotes.py`. Fail the job if the sample row is in the public bundle.

Later batches use the same pair shape. The maker adds quotes. The checker runs the script.

### Data sources

Use a public page for a public relation. Use the CTH record only inside the private tier. CLP, Academy, and investor-matching staff supply the private outcome. They do not supply the public quote.

### Dependencies

The private tier needs Gideon's GO before any staff record is stored. The public rule is already in force. Move 2 does not block the CSO demo.

### Effort

Size: medium for the schema and the first sample. The path from 40 to 200 is a repeated batch. Each batch is small. Do not schedule one job that adds 160 relations.

### Acceptance tests

1. The private sample is absent from `static/ecosystem/data/`.
2. `verify_relation_quotes.py` exits 0.
3. Every new public relation has a quote on the live page.
4. The public count rises only by rows that pass the script.
5. Hidden rows stay `verified: false`.
6. The sync script deletes a self-loop row. The script does not keep a self-loop as a hidden row.

### HITL

Stop when the quote is almost right but not verbatim. Leave the row hidden. Stop when the page names one actor only. A human accepts a borderline name variant. The script result wins over a model opinion.

## 12. Private evidence tier

**Status:** Proposal. Gideon must accept it before use.

The tier stores CTH records. The public site does not read this tier.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Private evidence",
  "type": "object",
  "additionalProperties": false,
  "required": ["tier", "touchpoint", "actors", "outcome", "consent_to_publish"],
  "properties": {
    "tier": { "const": "private" },
    "touchpoint": { "enum": ["clp", "academy", "investor_matching"] },
    "actors": {
      "type": "array",
      "minItems": 2,
      "maxItems": 2,
      "items": { "type": "string" }
    },
    "outcome": { "enum": ["meeting", "pilot", "money", "none"] },
    "internal_record_id": { "type": "string" },
    "consent_to_publish": { "type": "boolean" },
    "public_source_url": { "type": ["string", "null"] },
    "public_quote": { "type": ["string", "null"] }
  }
}
```

Store the file outside `static/ecosystem/data/`. Keep secrets and personal data in Infisical or in the private store. Do not commit them.

### Public pages may show

- An organization name.
- A relation type.
- A public URL.
- A verbatim quote from that URL.
- The date of access.
- A public office address.
- An outcome when the public source states that outcome.

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

`consent_to_publish` does not replace the quote rule. A public relation still needs `public_source_url` and `public_quote`.

## 13. Push back

These points disagree with a straight reading of the targets.

The target of 200 public relations can force weak relations. Keep the quote rule as the floor. Count only rows that pass `verify_relation_quotes.py`. Leave a weak row hidden. A batch stops when the quotes run out.

Move 3A is the cheapest pair. It must land before a CSO sees the product. It is a parallel gate. It is not the milestone. The milestone stays the CSO demo path.

Move 1 needs a Datalab gap taxonomy. That taxonomy is not in the repo. Section 8 is a draft. The status is **to agree with the Datalab desk**. A CT code is not a Datalab gap id.

The desk sent the sector order and the company list. Use them. The working sector label on each name is a group. The sustainability report wins when the report names a different gap. Portfolio codes `CE`, `BIO`, and `EN` are still not these sectors.

The teaser asks for 3 to 5 matches on each of 5 gaps. That is 15 to 25 public quotes. The Colombia graph has 6 actors and 2 public relations. It cannot fill the teaser. Use portfolio sites and other public pages. Drop the match when the quote is missing. A 2-page sheet cannot print every quote. Print the link. Keep the quote in the JSON.

A theme match is not a graph relation. Write it in the teaser only. Do not write it into `relations.json`.

Two stage fields exist. Do not merge the journey step with the startup stage.

The bad banner is on the public apex site. A PR in this repo cannot edit Elementor. Wait for the WordPress source. Remove the figure when no source exists. Do not type a replacement number. The other five headings on that row have the same defect. They stay out of scope until Gideon adds them.

`/p/home` is a public URL and an internal greeting. Do not use it as the CSO screen. The walkthrough uses the teaser and `/ecosystem/`.

Do not build 21 full teasers before the first walkthrough. The walkthrough uses one Wave 1 company. The map lists all 21 Wave 1 names. Add a match only when the quote exists. A missing quote stays a shortfall. Wave 2 stays off this map. Do not force Avianca, Claro, or a compensation fund into the five sector names. They are Wave 2.

PR 101 is a draft. The live public count is 40. The demo uses `main`.

Privacy holds for every move. Do not publish a personal email, a phone number, a home address, a Drive link, or a Canva link.

The Peru city-center table is the wrong pattern for Colombia pins. Use a street address or location unknown.

## 14. Sequence

| Order | Work | Blocks the demo | Pair model |
| --- | --- | --- | --- |
| A | Move 3A trust cleanup | Yes | `composer-2.5` maker and checker |
| A | Send section 6 to the GTM Strategy desk | No | Human |
| A | Move 1 schema and fixtures | No | `composer-2.5` maker and checker |
| B | Gideon GO list in section 15 | Yes | Human |
| B | Datalab desk reply on section 8 | Yes, for a named teaser | Human |
| C | Move 1 full teaser, one gap per batch | Yes | `composer-2.5` maker and checker |
| C | Move 4 Colombia wave, 21 Wave 1 companies | Yes | `composer-2.5` maker and checker |
| D | Presentations desk builds the HTML teaser | Yes | That desk |
| D | 20-minute walkthrough | Demo event | Human |
| E | Move 2 private tier, then quote batches | No | `composer-2.5` maker and checker |
| E | Move 3B cases after consent | No | `composer-2.5` maker and checker |
| E | Wave 2 companies, 13 names | No | Later pair |
| E | Paid workshop | No | GTM desk |

Rows with the same order letter may run in parallel. A later letter waits for the earlier letter.

The demo gate is the end of order D. Move 2 does not sit on that gate.

## 15. Decisions that need Gideon's GO

Record one yes or no for each line.

1. Use the 21 Wave 1 companies as the first Colombia map wave.
2. Keep the 13 Wave 2 names off that wave.
3. Use this sector order: banking and insurance, energy and utilities, oil and gas, food and consumer, construction.
4. Take each gap from that company's public sustainability report.
5. Include Interaseo on Wave 1. Give it a theme id after the Datalab desk replies.
6. Pick the first walkthrough company from Wave 1.
7. Store company names only. Do not add a person name.
8. Send section 8 to the Datalab desk as the draft contract.
9. Accept a teaser gap with `shortfall` `true` in an internal file.
10. Forbid a CSO-ready file while any gap has `shortfall` `true`.
11. Keep `theme_match` out of `relations.json`.
12. Remove `+10 Millons Capital Raised` when no source is on the page.
13. Leave the other five apex headings unchanged in this job.
14. Remove the `/p/home` activity feed.
15. Accept the private-evidence tier in section 12.
16. Confirm the privacy ban on personal email, phone, home address, Drive links, and Canva links.
17. Name the WordPress source for the apex banner.
18. Confirm that the Presentations desk owns the HTML teaser.
19. Confirm that deploy happens from `main` only, with backup and rollback.
20. Confirm that PR 101 stays out of the demo until it is on `main`.
21. Confirm that Colombia pins use a street address or location unknown.
22. Confirm that LinkedIn scraping is out of scope.
23. Confirm that secrets stay in Infisical.

## 16. Hard rules

1. Open a GitHub PR before a live change.
2. Deploy from `main` only.
3. Run `scripts/deploy_nexus_live.sh` or `ops/ecosystem/apply_live.sh` only after that merge.
4. Keep the backup and the rollback script from those tools.
5. Patch `ops/Caddyfile`. Do not replace the file.
6. Patch the live Caddy file the same way. Run `caddy validate` before reload.
7. Do not scrape LinkedIn.
8. Keep secrets in Infisical. The host name `secrets.cleantechhub.net` is the secrets endpoint. Do not copy a secret into git, into the Caddy file, or into this plan.
9. A public relation needs a source that names both actors and the relation, plus a verbatim quote.
10. A CSO-facing page must not show demo activity or an unsourced capital figure.
