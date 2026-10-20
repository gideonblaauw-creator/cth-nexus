# Nexus Ecosystem — Policy dataset (Gideon GO, 20 Oct 2026)

**Branch:** `research/ecosystem-policy` · **Deploy:** none (staging only)

## Scope

**Nexus actor countries** in `docs/ecosystem/prototype/data/actors.json`: **Colombia, Peru, El Salvador** (286 org actors; 47 `government`).

Sources per record (`registry` field + `source_url`):

| Registry | Use |
|----------|-----|
| [Climate Policy Database](https://www.climatepolicydatabase.org/) | Country indexes + NDC 3.0 CO entry |
| [LSE Climate Change Laws of the World](https://climate-laws.org/) | Laws, CONPES, decrees, country geographies |
| [UNFCCC NDC registry](https://unfccc.int/NDCREG) | NDC PDFs (CO, PE, SV) |
| National green taxonomies | Colombia [Taxonomía Verde](https://www.taxonomiaverde.gov.co/) |
| `gob.pe` / ministry sites | Peru programs & norms |

Rebuild: `python3 docs/ecosystem/scripts/build_policy_dataset.py` → `data/policies.json`, `policy_relations.json`.

## Relation schema (Gideon GO)

| Type | Endpoints | Verification |
|------|-----------|--------------|
| `issues_policy` | government actor → `policy:*` | `verified: true` only when `source_url` names the actor or hosts its program page |
| `addresses_challenge` | `policy:*` → `challenge:*` | `suggested: true`, sector-tag inference (PE challenges only today) |

Legacy org→org policy edges (`runs_program`, `regulates_layer`, …) remain in `relations.json` for D5 chapter merge in the prototype.

## Counts (generated)

| Country | Policies |
|---------|--------:|
| Colombia | 14 |
| Peru | 15 |
| El Salvador | 11 |
| **Total** | **40** |

**By instrument:** law 12 · strategy 10 · NDC 6 · incentive 6 · regulation 4 · tax 1 · taxonomy 1

### `policy_relations.json`

| Edge type | Count | Notes |
|-----------|------:|-------|
| `issues_policy` | 38 | all `verified: true` |
| `addresses_challenge` | 33 | all `suggested: true` |

### D5 policy chapter (merged with legacy `relations.json`)

Run gap script after rebuild; expect **~83** edges (40 policy relations + 12 legacy org-org policy types + overlap).

## Government coverage gaps

**47** government actors · **21** with ≥1 verified `issues_policy` · **26** without (no citable source naming the actor):

| Country | Unlinked actors (sample) |
|---------|---------------------------|
| Peru (23) | Regional governments (Amazonas, Loreto, Madre de Dios, San Martín, Ucayali, Cusco), MEF, PromPerú, ProInversión, CONCYTEC, Agrobanco, COFIDE, SBS, SMV, SENAMHI, INAIGEM, IMARPE, municipal incubators, … |
| El Salvador (3) | CENTA, ESCO, INVEST |
| Colombia (0 unlinked in issues_policy set) | Ley 2169 / MADS not in graph — no verified edge for carbon-neutrality law |

**Other gaps**

- **Challenge nodes:** only `challenge:PE-1-bosques` and `challenge:PE-2-agua` — CO/SV policies have no challenge targets.
- **Colombia MADS / MinAmbiente** absent from `actors.json`.
- **Guatemala & Costa Rica** not in Nexus actors (omitted from this GO scope).
- **CPD country index rows** used as catalog pointers where a single instrument URL is not yet split out (e.g. JET roadmap, PE CPD index).

## Screenshot

`docs/ecosystem/screenshots/d5v2-ch2-policy.png` — regenerate via `docs/ecosystem/prototypes/capture-d5v2.mjs` with static server on port 8765.
