# Nexus Ecosystem — Policy dataset (staged)

**Branch:** `research/ecosystem-policy` (from `research/ecosystem-directions` @ `486f2c7`)  
**Artifacts:** `data/policies.json`, `data/policy_relations.json` (patch merged in D5 prototype only — not deployed to `static/ecosystem/`)

## Method

1. **Scope** — Ecosystem countries in `actors.json`: Peru (201), El Salvador (77), Colombia (8). Guatemala and Costa Rica have **no org actors yet** but are included in `policies.json` for REIN/LATAM expansion and cross-country comparison.
2. **Instrument selection** — Priority on laws, NDCs, taxonomies, incentives, and national strategies with clear climate, water, forest, or energy links. Programs already in the graph (e.g. StartUp Perú, IPSE, FIDEAGRO) are linked via `implements` where ministry sources name them.
3. **Relations** — Only edges with a citable `source_url`. `verified: true` when the source states the link (ministry mandate, legal text, program page). `suggested: true` for sector-fit startup↔policy matches (rendered dashed in D5).
4. **Regeneration** — `python3 scripts/ecosystem/build_policies.py` writes root `data/*` and copies to `docs/ecosystem/prototypes/shared/` for the D3/D5 mockup.

## Sources (top)

| Source | Use |
|--------|-----|
| [Climate Change Laws of the World](https://climate-laws.org/) | Peru Ley 30754, ENCC 2050, Colombia 1715/2169, CR decarbonization plan, SV/GT references |
| [Climate Policy Database](https://climatepolicydatabase.org/) | Colombia Ley 2099, cross-checks |
| [UNFCCC NDC Registry](https://unfccc.int/NDCREG) | NDC PDFs (PE, CO, SV, GT, CR) |
| [Taxonomía Verde Colombia](https://www.taxonomiaverde.gov.co/) | Circular Externa 005/2022 |
| National portals | `gob.pe`, `funcionpublica.gov.co`, `sinia.minam.gob.pe`, `minenergia.gov.co`, `cambioclimatico.go.cr`, `marn.gob.gt`, MAG/MARN SV |

Every policy row includes `source_url`. Relation rows duplicate the supporting URL.

## Counts

### Policy nodes (46)

| Country | Count | By instrument type |
|---------|------:|--------------------|
| Peru | 12 | law 5, strategy 3, NDC 1, regulation 1, incentive 2 |
| Colombia | 10 | law 3, strategy 3, NDC 1, taxonomy 1, incentive 2 |
| El Salvador | 8 | law 2, strategy 3, NDC 1, incentive 2 |
| Guatemala | 8 | law 2, strategy 3, NDC 1, taxonomy 1, tax 1 |
| Costa Rica | 8 | law 3, strategy 4, NDC 1, incentive 1 |

### Policy chapter edges (base `relations.json` + patch)

After merging `policy_relations.json` into the D5 guide (chapter 2), **59** edges qualify for the Policy chapter (was **12** org-only program/regulation links).

| Edge type | Count (merged) |
|-----------|---------------:|
| implements | 14 |
| enables | 10 |
| issues | 9 |
| oversees | 7 |
| runs_program | 4 |
| regulates_layer | 3 |
| participates | 2 |
| finances | 2 |
| benefits | 3 |
| eligible | 3 |
| created | 1 |
| runs_initiative | 1 |

**Patch only (`policy_relations.json`):** 47 edges — **39 verified**, **8 suggested**.

### Verified vs suggested (patch)

- **Verified (39):** ministry→policy (`issues`/`oversees`), agency/program→policy (`implements`), policy→challenge (`enables`), policy→program (`finances`), cross-policy (`enables`).
- **Suggested (8):** startup `benefits`/`eligible` where sector fit is plausible but not documented as a formal program enrollment (PE water/forest/mobility startups; SV agro/recycling).

## Government actor coverage

| Country | Actors mapped to ≥1 policy |
|---------|---------------------------|
| Peru | MINAM, MINEM, PRODUCE, ProInnóvate, SERFOR, ANA, Programa Bosques, Bionegocios |
| Colombia | MinEnergía, UPME, CREG, IPSE |
| El Salvador | MARN, MINEC, CONAMYPE, MAG, FIDEAGRO |
| Guatemala | — (policies staged; no gov nodes in `actors.json`) |
| Costa Rica | — (policies staged; no gov nodes in `actors.json`) |

## Gaps / next curation

- **GT & CR:** Need government and agency nodes in `actors.json` to replace policy-only subgraphs.
- **Subnational:** Regional governments in Peru (Amazonas, Loreto, etc.) not yet tied to forest/water instruments.
- **Carbon pricing / fiscal:** Colombia carbon tax detail and Peru MEF instruments under-modeled.
- **Startup eligibility:** Only 8 suggested edges; one-pager sector tags would enable more verified `eligible` links.
- **Challenge nodes:** Only PE-1 (bosques) and PE-2 (agua) exist; CO/SV/GT/CR `enables` mostly policy-to-policy until challenge IDs are added.
- **Deploy:** Data is **staged** — production bundle still uses legacy `relations.json` until graph build pipeline merges the patch.

## Screenshot

Regenerated: `docs/ecosystem/screenshots/d5v2-ch2-policy.png`  
URL: `prototypes/d3-hybrid-split/index.html?mode=guide&chapter=1` (Policy = chapter index 1).
