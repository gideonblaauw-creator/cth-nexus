# Nexus Ecosystem — Policy dataset (staged)

**Branch:** `research/ecosystem-policy` (from `research/ecosystem-directions` @ `486f2c7`)  
**Artifacts:** `data/policies.json`, `policy_relations.json` (repo root)  
**Deploy:** none — research/staging only; prototype reads symlinks under `docs/ecosystem/prototypes/`.

## Method

1. **Scope** — Ecosystem countries named in the product brief (Colombia, Peru, El Salvador, Guatemala, Costa Rica) plus any country present in `docs/ecosystem/prototype/data/actors.json` (currently **CO, PE, SV** only; GT/CR policies staged without government actor links).
2. **Policy nodes** — One row per citable instrument (`type: "Policy"`), with `instrument` ∈ {law, NDC, tax, taxonomy, incentive, regulation, strategy}, sector tags aligned to Nexus challenge themes (`agua`, `bosques`, `energía`, `adaptación`, etc.), and **`source_url` on every row**.
3. **Relations** — Drawn only when a primary source supports the edge. `verified: true` + `source_url` → solid edges in D5v2 guide mode; `suggested: true` → dashed (sector/challenge fit without a direct legal citation).
4. **Actor linkage** — Existing `government` (and program) slugs in `actors.json` linked via `issues` / `oversees` / `implements` / `runs_program` / `regulates_layer`. Legacy org→program edges from Canva remain; parallel edges to formal `policy:*` nodes enrich chapter 2 without removing D1 data.
5. **Peru national laws** — No separate Peru-only policy branch was visible on `origin` at staging time; Peru framework laws (30754, 28611, etc.) are included here. Drop or dedupe if a parallel job lands the same IDs.
6. **Sources (priority)** — [Climate Policy Database](https://climatepolicydatabase.org/), [LSE Climate Change Laws of the World](https://climate-laws.org/), [UNFCCC NDC registry](https://unfccc.int/NDCREG), [IEA policies](https://www.iea.org/policies), national `gob.pe` / `funcionpublica.gov.co` / ministry sites, [Colombia Taxonomía Verde](https://www.taxonomiaverde.gov.co/).

## Counts (staged)

### Policies by country

| Country | Policies |
|---------|----------|
| Colombia | 10 |
| Peru | 12 |
| El Salvador | 8 |
| Guatemala | 6 |
| Costa Rica | 6 |
| **Total** | **42** |

### Policies by instrument

| Instrument | Count |
|------------|------:|
| law | 16 |
| strategy | 8 |
| incentive | 7 |
| NDC | 5 |
| regulation | 4 |
| taxonomy | 2 |

### Policy-chapter relations (merged with legacy `relations.json`)

| Edge type | Count |
|-----------|------:|
| implements | 12 |
| oversees | 11 |
| issues | 10 |
| runs_program | 8 |
| enables | 7 |
| regulates_layer | 4 |
| finances | 3 |
| participates | 2 |
| created | 1 |
| runs_initiative | 1 |
| **Total (chapter 2)** | **59** |

### Verification

| | Count |
|---|------:|
| Verified relations (`verified: true`, not suggested) | 42 |
| Suggested relations (`suggested: true`, dashed) | 5 |
| Policy relation rows in `policy_relations.json` | 47 |

## Top sources (by citation count in dataset)

| Domain / registry | Uses |
|-------------------|-----:|
| `gob.pe` | 14 |
| `funcionpublica.gov.co` | 7 |
| `unfccc.int` (NDC PDFs) | 5 |
| `climate-laws.org` | 11 |
| `taxonomiaverde.gov.co` | 3 |
| `marn.gob.sv` / `minec.gob.sv` / `mag.gob.sv` | 6 |
| `minenergia.gov.co` / `ipse.gov.co` | 4 |
| `busquedas.elperuano.pe` | 1 |

## Gaps and next steps

- **Guatemala & Costa Rica** — Policies present; **no government actors** in `actors.json` yet → no verified ministry edges until GT/CR org nodes are added.
- **Colombia environment ministry (MADS)** — Not in actor graph; carbon-neutrality law (2169) linked mainly via MinEnergía/UPME with one **suggested** implements edge pending MADS node.
- **Challenge nodes** — Only `challenge:PE-*` exists; CO/SV policy→challenge links not asserted (would be suggested-only until challenge nodes exist).
- **Subnational & municipal** — Regional governments in PE actors not yet tied to sector laws (Amazonía, water basins).
- **IEA / Climate Policy Database** — Used for cross-check; URLs point to authoritative national copies where possible.
- **Production merge** — Wire `data/policies.json` into `static/ecosystem/data/` build pipeline and extend `guide-chapters.js` counts in CI (prototype already loads staged files).

## Screenshot

Regenerate D5v2 policy chapter:

```bash
cd docs/ecosystem/prototypes
python3 -m http.server 8765 &
node capture-d5v2.mjs   # writes docs/ecosystem/screenshots/d5v2-ch2-policy.png
```

## File layout

```
data/policies.json              # 42 policy nodes
policy_relations.json           # 47 staged edges (+ legacy relations in prototype)
docs/ecosystem/policy-research.md
docs/ecosystem/d5v2-gap-counts.json   # policy.total → 59 after merge
docs/ecosystem/prototypes/data/policies.json      → symlink
docs/ecosystem/prototypes/policy_relations.json   → symlink
```
