# Nexus LATAM Ecosystem Graph — Product & Technical Spec

**Status:** Draft (research branch)  
**Audience:** CTH/REIN staff, Nexus engineers  
**Live target (future):** `https://nexus.cleantechhub.net/ecosystem/` (static bundle under `static/ecosystem/`, staff-gated)  
**Brands:** CTH + REIN skins, **EN/ES** copy  
**Prototype:** [`prototype/index.html`](prototype/index.html) (sigma.js + graphology, real `actors.json` / `relations.json`)

---

## 1. Problem statement

The current ecosystem page (`feat/ecosystem-env`) is a **filterable card grid** with charts and a small **vis-network** panel. Gideon’s requirement: make **relationships** first-class — who funds, hosts, incubates, partners with, regulates, or mentors whom — with LATAM geo context and explorer-grade interactions (ego view, path finding, time where data exists), while keeping the **staff-only gate**.

---

## 2. Goals & non-goals

### Goals
- Primary canvas = **force-directed graph** (and optional **geo arc map**) of actors.
- **Typed, directed edges** with provenance and bilingual labels.
- Derive maximum edges from **existing Nexus repo data** before manual curation.
- **Performance:** smooth at ~500 nodes / ~2k edges (12-month target).
- **Accessibility:** keyboard navigation, screen reader summaries, reduced motion.
- Preserve **CTH/REIN** toggle and **EN/ES** i18n patterns from current page.

### Non-goals (this program)
- Public anonymous access (staff gate stays).
- Real-time sync with Crunchbase/Dealroom (optional future enrichment).
- Replacing HumHub, mentor app, or one-pager generators.

---

## 3. Personas & jobs-to-be-done

| Persona | Job |
|---------|-----|
| REIN/CTH program staff | See hub influence: incubated startups, cofunded programs, gov links |
| Mentor lead | Trace mentor → startup → hub → funder paths |
| Country lead | Compare PE vs SV vs CO **graph density** and gaps (GT/CR) |
| Funder outreach | Ego network from `pe-cleantechhub` / REIN hub nodes |

---

## 4. Proposed data model

### 4.1 Node (`Actor`)

```typescript
type ActorKind = 'org' | 'person' | 'program' | 'challenge';

type ActorCategory =
  | 'startup' | 'accelerator' | 'funder' | 'corporate' | 'government'
  | 'academia' | 'ngo_foundation' | 'international' | 'finance'
  | 'chamber' | 'media' | 'mentor' | 'hub' | 'program';

interface Actor {
  id: string;                    // stable slug, e.g. pe-emprende-up-climatech-rein-hub-peru
  name: { en: string; es: string } | string; // phase 1: string OK
  kind: ActorKind;
  category: ActorCategory;
  country: 'PE' | 'SV' | 'CO' | 'GT' | 'CR' | string;
  city?: string | null;
  geo?: { lat: number; lng: number } | null;
  website?: string | null;
  linkedin?: string | null;
  nexus?: {
    card_slug?: string | null;   // /s/{slug}
    hub_id?: string | null;      // hubs-data.json id
    mentor_id?: string | null;
  };
  sector?: string[];             // CLP CT-* tags, Drawdown-aligned later
  brand_affinity?: ('cth' | 'rein')[];
  source?: { type: string; id?: string; extracted_at?: string };
  meta?: Record<string, unknown>;
}
```

### 4.2 Edge (`Relationship`)

```typescript
type EdgeType =
  | 'invested-in'
  | 'funded-by'
  | 'cofunds'
  | 'hosts'
  | 'hosts-program'
  | 'runs-program'
  | 'incubated'
  | 'accelerated'
  | 'mentored'
  | 'alumni-of'
  | 'partners-with'
  | 'part-of-group'
  | 'owns'
  | 'participates'
  | 'works-on-challenge'
  | 'regulates'
  | 'employed-at'      // Endeavor-style; future
  | 'member-of';       // programs, networks

interface Relationship {
  id: string;                    // hash or uuid
  source: string;                // actor id
  target: string;
  type: EdgeType;
  directed: boolean;             // default true except partners-with
  weight?: number;               // Graph Commons style; default 1
  since?: string | null;         // ISO date
  until?: string | null;
  label?: { en?: string; es?: string };
  evidence?: {
    source: 'canva' | 'mentor_cards' | 'onepager' | 'hubs' | 'manual' | 'clp_roster';
    ref?: string;
    notes?: string;
    confidence: 'verified' | 'inferred' | 'pending';
  };
}
```

### 4.3 Graph bundle (deploy artifact)

```
static/ecosystem/data/
  actors.json          # nodes
  relations.json       # edges (rename → relationships.json in v2)
  meta.json            # version, counts, build sha, i18n keys
  derived/             # optional CI output
    mentor-edges.json
    hub-edges.json
    startup-edges.json
```

### 4.4 Edge type semantics (LATAM cleantech)

| Type | Typical source → target | Example |
|------|-------------------------|---------|
| `hosts` | university → incubator | UNALM → Incubagraria |
| `runs-program` | ministry → program | MINAM → Programa Bionegocios |
| `cofunds` | program → hub/incubator | ProInnóvate → REIN Hub Perú |
| `incubated` | hub → startup | REIN Hub → YakuSmart |
| `partners-with` | hub ↔ org | REIN Hub ↔ CleantechHUB |
| `works-on-challenge` | org → challenge area | SV actors → challenge nodes |
| `mentored` | mentor → startup | mentor_cards |
| `funded-by` | startup → funder | future / manual |
| `alumni-of` | person → university | future |

**Legacy mapping** from current `relations.json`: keep `hosts`, `partner`→`partners-with`, `runs_program`→`runs-program`, `cofunds`, `incubated`, `works_on_challenge`→`works-on-challenge`, etc.

---

## 5. Deriving edges from existing Nexus data

| Source | Path | Nodes | Edges to emit | Matching |
|--------|------|-------|---------------|----------|
| Canva extract | `static/ecosystem/data/*.json` | orgs | 75+ typed edges | id slugs |
| Startup one-pagers | `onepagers/data/{slug}.json` | `category=startup` | `nexus.card_slug=slug`; optional `website` match to actor | normalize name, fuzzy website |
| Portfolio HTML | `pages/p/startup-portfolio/index.html` | startups | country, CLP cohort, sector tags on nodes | slug in `n`/`p` fields |
| Mentor cards | `data/clp26/mentor_cards.json` | `kind=person`, `category=mentor` | `mentored` → startup; `member-of` → country hub | match `startups_mentored[]` to one-pager `name` / slug |
| Hubs | `site/cth-static/hubs/hubs-data.json` | `category=hub` | `hosts-program`, `partners-with` REIN/CTH | hub `id` ↔ actor id convention |
| Mentoring app | `site/mentoring/` | sessions | future `mentored` weights | API later |
| Investors site | `site/investors/` | funders | `funded-by` when disclosed | manual QA |

### 5.1 Build pipeline (recommended)

1. **`scripts/ecosystem/build_graph.py`** — ingest sources → validate → emit bundle.
2. **Validation rules:** no dangling source/target; duplicate edges merge weight; log orphan actors.
3. **CI:** fail if &gt; N% orphans without `category` in allowlist (gov intl often sparse).
4. **Staff override:** `data/ecosystem/overrides.json` for manual edges (Git-reviewed).

### 5.2 Identifier conventions

- Country prefix: `pe-`, `sv-`, `co-` (existing).
- Person: `person-{slug(name)}-{country}`.
- Program/challenge: reuse design ids where present (`works_on_challenge` targets).

---

## 6. Interaction design

### 6.1 Layout modes

1. **Graph** (default) — force-directed; node size = degree or betweenness; edge color = type.
2. **Geo** — MapLibre basemap + points; optional **deck.gl ArcLayer** for cross-border `cofunds` / `invested-in`.
3. **Matrix** (phase 3) — chord adjacency for category×category flows.

### 6.2 Core interactions

| Interaction | Behavior |
|-------------|----------|
| Search | Focus node, dim non-neighbors, list match results |
| Filters | Country, category, sector, edge types, min-degree slider (existing) |
| Click node | Inspector: links, Nexus card, website, **Open ego view** |
| Ego view | Depth 1–3 (Obsidian local graph pattern) |
| Path finding | Select A + B → shortest path (unweighted BFS; weighted Dijkstra later) |
| Time slider | Filter edges/nodes with `since`/`until`; animate `founded` year when present |
| Pin | Fix hub positions; re-run layout on rest |
| Export | PNG/SVG graph; CSV edges; JSON snapshot |

### 6.3 Empty states

- GT/CR: map + copy “mapeo en preparación” (existing i18n).
- Orphans toggle: “show unconnected actors” (Obsidian orphan pattern).

### 6.4 Brand & language

- Reuse `data-brand="cth|rein"` CSS tokens from `nexus-brand.css`.
- All edge type labels and inspector fields in **EN/ES** catalog (`I18N` object pattern in `ecosystem.js`).

---

## 7. Recommended technology stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Graph model | **graphology** | Typed attributes, traversals, import/export |
| Renderer | **sigma.js v2** (WebGL) | 500+ nodes; better perf than vis-network at scale |
| Layout | **ForceAtlas2** (graphology-layout-forceatlas2) or **cose** via Cytoscape if team prefers single lib | FA2 matches Kumu/Graph Commons feel |
| Geo | **MapLibre GL JS** + **deck.gl** ArcLayer | LATAM arcs for capital/program flows |
| Alt / fallback | **Cytoscape.js** | Rich a11y plugins, fcose layout |
| Build | Python ingest + JSON schema (jsonschema) | Matches repo’s static data pattern |
| Auth | Existing **Nexus gate** cookie/session | No change to public routes |

**Prototype** uses sigma + graphology (CDN) to de-risk WebGL path; production may embed in `ecosystem.js` bundle or small Vite chunk under `static/ecosystem/`.

---

## 8. Performance

- **Target:** 60fps pan/zoom at 400 visible nodes; &lt;100ms filter apply.
- Load single compressed JSON; **index** adjacency in worker (`Map<source, Edge[]>`).
- Hide labels below zoom threshold (Obsidian text fade).
- **Level-of-detail:** collapse low-degree funders into “Funder cluster” meta-node above threshold.
- Lazy-load inspector details; don’t render all edge labels.

---

## 9. Accessibility

- Graph region: `role="application"` + **`aria-label`** describing selection state.
- Keyboard: Tab through search/filters; Enter to focus node; Esc clears selection.
- **Screen reader:** announce “Node X, 4 connections, incubator, Peru” on focus.
- Provide **table view** of filtered edges (Graph Commons data table pattern) — fully navigable.
- **`prefers-reduced-motion`:** disable force simulation; use static layout positions from last save.
- Color: edge types distinguishable by **shape/pattern** not color alone.

---

## 10. Security & staff gate

- Keep **`meta robots noindex`** and staff authentication on `/ecosystem/` (same as current `index.html`).
- Do not embed emails or internal Drive URLs in public bundle (already sanitized in README).
- Gate implementation: [`site/nexus-auth/gate.html`](../../site/nexus-auth/gate.html) + Caddy routes under `/nexus-auth*` ([`ops/nexus-roots.json`](../../ops/nexus-roots.json)).

---

## 11. Phased delivery plan

### Phase 0 — Research & prototype (this branch)
- `docs/ecosystem/research.md`, `spec.md`, `prototype/index.html`
- No production deploy

### Phase 1 — Graph-first MVP (merge to `feat/ecosystem-env`)
- Replace card-primary layout with graph-primary
- Migrate to graphology + sigma (or Cytoscape)
- Schema v2 + legacy type mapper
- Table view + ego depth 2

### Phase 2 — Data fusion
- `build_graph.py` + mentor/hub/startup derived edges
- Overrides file + CI validation
- Nexus deep links on all matched startups

### Phase 3 — Geo & time
- MapLibre + city geocoding
- ArcLayer for cross-border flows
- Time slider on cohort/year

### Phase 4 — Analytics & export
- Betweenness / community detection highlights
- PitchBook-style segment export PNG
- Optional LAVCA/Crunchbase enrichment (manual)

---

## 12. Parallel ticket plan (small, independent)

Tickets are sized for parallel work; order within a phase can shuffle.

| ID | Title | Phase | Depends |
|----|-------|-------|---------|
| ECO-01 | JSON Schema for Actor + Relationship | 1 | — |
| ECO-02 | Edge type i18n catalog (EN/ES) | 1 | ECO-01 |
| ECO-03 | Integrate sigma.js graph as primary panel | 1 | — |
| ECO-04 | Port existing filters to graph visibility pipeline | 1 | ECO-03 |
| ECO-05 | Inspector panel + Nexus `/s/` + hub links | 1 | ECO-03 |
| ECO-06 | Ego view depth slider | 1 | ECO-03 |
| ECO-07 | Path finder (BFS) UI | 1 | ECO-03 |
| ECO-08 | Accessible edge/data table view | 1 | ECO-04 |
| ECO-09 | `build_graph.py` skeleton + validators | 2 | ECO-01 |
| ECO-10 | Derive mentor→startup edges from `mentor_cards.json` | 2 | ECO-09 |
| ECO-11 | Merge `hubs-data.json` hub nodes + partner edges | 2 | ECO-09 |
| ECO-12 | Match one-pagers to actors by slug/website | 2 | ECO-09 |
| ECO-13 | Staff `overrides.json` + review doc | 2 | ECO-09 |
| ECO-14 | CI check: dangling edges / orphan report artifact | 2 | ECO-09 |
| ECO-15 | MapLibre country focus + actor pins | 3 | ECO-04 |
| ECO-16 | deck.gl ArcLayer for selected edge types | 3 | ECO-15 |
| ECO-17 | Geocode pipeline for cities | 3 | ECO-15 |
| ECO-18 | Time slider + edge `since` fields | 3 | ECO-01 |
| ECO-19 | Betweenness highlight + “bridge actors” chip | 4 | ECO-03 |
| ECO-20 | PNG/SVG export | 4 | ECO-03 |
| ECO-21 | GT/CR placeholder content workflow | 2 | — |
| ECO-22 | Performance: worker adjacency index | 1 | ECO-03 |
| ECO-23 | `prefers-reduced-motion` static layout mode | 1 | ECO-03 |

---

## 13. Acceptance criteria (Phase 1 MVP)

- [ ] Staff can open `/ecosystem/`, authenticate, land on **graph view** with ≥75 edges visible.
- [ ] Filter by PE/SV/CO and category updates graph in &lt;200ms on laptop.
- [ ] Click REIN Hub Perú → ego view shows incubated startups and partners.
- [ ] Path mode finds route ProInnóvate → YakuSmart if path exists in data.
- [ ] EN/ES toggle updates UI strings; REIN/CTH toggles theme.
- [ ] WCAG: table view operable without mouse; reduced motion respected.

---

## 14. Open questions

1. Should **challenge** nodes (`works_on_challenge`) remain in graph or become sector tags only?
2. Person nodes: show mentors publicly on staff map or aggregate to “Mentor network” meta-node?
3. Colombia expansion: ingest full Canva deck when available — separate country graph or unified?
4. Merge `feat/ecosystem-env` to `main` before or after graph MVP?

---

## 15. Related files

| Artifact | Location |
|----------|----------|
| Research | [`research.md`](research.md) |
| Prototype | [`prototype/index.html`](prototype/index.html) |
| Data (copy) | [`prototype/data/actors.json`](prototype/data/actors.json), [`prototype/data/relations.json`](prototype/data/relations.json) |
| Production (branch) | `origin/feat/ecosystem-env:static/ecosystem/` |
