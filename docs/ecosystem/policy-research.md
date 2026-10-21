# Nexus Ecosystem — Policy dataset (Gideon GO + SINIA, 20 Oct 2026)

**Branch:** `research/ecosystem-policy` · **Deploy:** none (staging only)

## Scope

**Nexus actor countries** in `docs/ecosystem/prototype/data/actors.json`: **Colombia, Peru, El Salvador** (286 org actors; 47 `government`).

Sources per record (`registry` field + `source_url`):

| Registry | Use |
|----------|-----|
| **SINIA** (MINAM) | Peru environmental norm catalogue — JSON:API `node/normatividad`, **Vigente** only |
| [Climate Policy Database](https://www.climatepolicydatabase.org/) | Country indexes + NDC 3.0 CO entry |
| [LSE Climate Change Laws of the World](https://climate-laws.org/) | Laws, CONPES, decrees, country geographies |
| [UNFCCC NDC registry](https://unfccc.int/NDCREG) | NDC PDFs (CO, PE, SV) |
| National green taxonomies | Colombia [Taxonomía Verde](https://www.taxonomiaverde.gov.co/) |
| `gob.pe` / ministry sites | Peru programs & norms not superseded by SINIA rows |

**Rebuild Peru catalogue:** `python3 docs/ecosystem/scripts/scrape_sinia_norms.py` → merges into `data/policies.json`, regenerates `policy_relations.json` (CO/SV verified edges from builder + SINIA PE links).

**Rebuild CO/SV curated only:** `python3 docs/ecosystem/scripts/build_policy_dataset.py` (overwrites; run before SINIA merge if refreshing non-PE).

## Relation schema (Gideon GO)

| Type | Endpoints | Verification |
|------|-----------|--------------|
| `issues_policy` | government actor → `policy:*` | `verified: true` only when SINIA issuer taxonomy or norm page body names the actor as issuer/implementer (legacy CO/PE/SV rows: named on cited URL) |
| `addresses_challenge` | `policy:*` or evidence id → `challenge:*` | `suggested: true`, sector-tag inference (PE challenges only today) |

Legacy org→org policy edges (`runs_program`, `regulates_layer`, …) remain in `relations.json` for D5 chapter merge in the prototype.

## Counts (SINIA scrape)

| Country | Policies |
|---------|--------:|
| Colombia | 14 |
| Peru | 13,271 (13,262 SINIA Vigente + 9 legacy kept) |
| El Salvador | 11 |
| **Total** | **13,296** |

**Peru dedupe:** 6 prior curated PE norms dropped where SINIA Vigente matched by norm number; 7 ids in `PRESERVE_PE_IDS` plus 2 program/NDC rows retained without SINIA duplicate.

**SINIA fields on PE rows:** `sinia_number`, `sinia_type`, `sinia_date`, `issuing_authority`, `descriptors`, `pdf_url` / `pdf_urls`, `registry: "SINIA"`, `source_url` = norm page (`https://sinia.minam.gob.pe` + path alias).

### `policy_relations.json`

| Edge type | Count | Notes |
|-----------|------:|-------|
| `issues_policy` | 4,903 | 4,884 PE (SINIA) + 19 CO/SV verified |
| `addresses_challenge` | 603 | policies + 3 MINAM datos abiertos evidence refs |

**Optional challenge evidence (suggested):** GHG inventory, waste composition, wildfires/heat points, degraded forest areas — catalog URLs on [datosabiertos.gob.pe](https://www.datosabiertos.gob.pe/) / SINIA portal.

### D5 policy chapter (merged with legacy `relations.json`)

See `docs/ecosystem/d5v2-gap-counts.json` — **5,518** policy-chapter edges (legacy org-org + staged policy relations).

## Government coverage

**47** government actors · **39** with ≥1 verified `issues_policy` · **8** without:

| Country | Unlinked (no issuer/implementer named on cited norm) |
|---------|------------------------------------------------------|
| Peru (5) | `pe-agrobanco`, `pe-promperu`, `pe-coworking-municipal-de-jesus-maria`, `pe-municipalidad-de-miraflores-emprende-miraflores`, `pe-surco-emprende` |
| El Salvador (3) | `sv-centa`, `sv-esco-agencia-de-el-salvador-para-la-cooperacion-in`, `sv-invest-agencia-de-promocion-de-inversiones-y-expor` |
| Colombia (0) | Ley 2169 / MADS not in graph — no verified edge for carbon-neutrality law |

**Other gaps**

- **Challenge nodes:** only `challenge:PE-1-bosques` and `challenge:PE-2-agua` — CO/SV policies have no challenge targets.
- **Colombia MADS / MinAmbiente** absent from `actors.json`.
- **PDF text mining** not used for issuer verification (taxonomy + norm page body only).

## Screenshot

`docs/ecosystem/screenshots/d5v2-ch2-policy.png` — regenerate via `docs/ecosystem/prototypes/capture-d5v2.mjs` with static server on port 8765 (large PE policy load may need longer `__ecoReady` timeout).
