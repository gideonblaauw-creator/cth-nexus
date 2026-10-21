# CleantechHUB Nexus — How the puzzle fits together

**Artifact type:** Internal review (not deployed, not customer-facing)  
**Generated from repo:** `static/ecosystem/`, `story.mjs`, `story-chapters.json`, `site/cth-static/hubs/`, Nexus `/s/` one-pagers, `/ideas`, `/p/startup-portfolio`  
**Diagram:** [`map.mmd`](map.mmd) · [`map.html`](map.html) · [`map.png`](map.png)  
**Wire review (large type):** [`map-wire.html`](map-wire.html) · [`map-wire.png`](map-wire.png) (3000px) · [`map-wire.pdf`](map-wire.pdf) · [`map-wire-mobile.png`](map-wire-mobile.png)

| Symbol | Meaning |
|--------|---------|
| **LIVE** | Shipped in `cth-nexus` `main` and/or reachable on Nexus today (some surfaces are staff-gated). |
| **PLANNED** | Specified or partially stubbed; not fully wired in UI/data. |
| **PARTIAL** | Live with known gaps (sparse slugs, inferred edges, etc.). |

---

## 1. North star

Staff and partners move across **the same actors**—ministries, hubs, funders, startups—through different lenses:

1. **Explore** the LATAM graph (map + network + filters).  
2. **Walk a guided story** (chapters that filter edge types and geography).  
3. **Open depth pages**—HubMap, Nexus cards, portfolio, Ideas, Wiki—without losing country context.

**Source of truth:** GitHub [`gideonblaauw-creator/cth-nexus`](https://github.com/gideonblaauw-creator/cth-nexus) **`main`**. Production static is promoted deliberately (`ops/ecosystem/README.md`: merge first, then `apply_live.sh`).

---

## 2. Core surfaces (pieces + paths)

| Piece | URL / path | Repo home | Status |
|-------|------------|-----------|--------|
| **D3 Explore** (map + network + actor cards tab) | `https://nexus.cleantechhub.net/ecosystem/` | `static/ecosystem/` (`ecosystem.mjs`, `index.html`) | **LIVE** · staff auth (`nexus-auth`) |
| **D5 Guided story** | Same URL · tab “Historia guiada” / “Guided story” | `story.mjs`, `data/story-chapters.json` | **LIVE** · chapter order **differs from target** (see §3) |
| **HubMap** | `https://nexus.cleantechhub.net/hubs/` · `/hubs/{slug}/` | `site/cth-static/hubs/` (`hubs-data.json`, per-hub `index.html`) | **LIVE** · public |
| **Startup portfolio** | `/p/startup-portfolio` | `site/nexus-www/startup-portfolio.html` (embedded data) | **LIVE** |
| **Nexus startup cards** | `/s/{slug}` | `onepagers/sites/{slug}/`, `onepagers/data/*.json` | **LIVE** · many slugs |
| **Nexus Ideas** | `/ideas` | `app/nexus-ideas/` | **LIVE** |
| **Wiki — Idea Browser** | `wiki.cleantechhub.net/books/idea-browser` | BookStack (pages linked from one-pagers / `wiki-drafts/`) | **LIVE** |
| **Wiki — Actor pages** | `wiki.cleantechhub.net` (book **3042** until approved) | Draft workflow in ops; not fully linked from ecosystem UI | **PLANNED** (content/review) |
| **Policy DB** | Loaded into ecosystem bundle | `static/ecosystem/data/policies.json`, `policy_relations.json`; research lineage **SINIA (Peru)** + **Colombia** corpora via **`research/ecosystem-policy`** on GitHub | **LIVE** in bundle · **PARTIAL** cross-links |
| **Actor graph data** | `/ecosystem/data/*.json` | 286 actors, 75 org relations, 40 policies, 71 policy relations (`data/README.md`) | **LIVE** · staff-gated fetch |

---

## 3. D5 Guided story — chapter order

### Target order (staff spec — **PLANNED** reorder + new chapter)

1. **Challenges** — `works_on_challenge`; challenge nodes are Canva references, not orgs.  
2. **Policy** — verified graph edges + `issues_policy` + inferred `addresses_challenge` (Suggested).  
3. **Hubs** — `hosts`, `incubated`, `accelerated`, `partner`.  
4. **Data** — ecosystem / open-data layer chapter (**PLANNED**; no `data` chapter in `story-chapters.json` today).  
5. **Partnerships** — constellations + **Suggested** dashed edges (`story-chapters.json` → `constellations`).  
6. **Capital** — `cofunds`, `funds_layer`.

### Live order in `static/ecosystem/data/story-chapters.json` (**LIVE**)

| # | Chapter id | Title (EN) |
|---|------------|------------|
| 1 | `challenges` | Climate challenges |
| 2 | `policy` | Public policy |
| 3 | `capital` | Capital |
| 4 | `hubs` | Hubs & incubation |
| 5 | `partnerships` | Partnerships |

Implementation logic lives in `static/ecosystem/story.mjs` (`chapterScene`, `computeChapterEdgeCounts`, constellation builder). Reordering is a **config + rail UX** change; adding **Data** requires a new chapter definition (edge types, copy, map camera, and data sources).

Screenshots (reference): `static/ecosystem/screenshots-d5/`.

---

## 4. Cross-links

| From | To | Status | Notes |
|------|-----|--------|-------|
| **Challenge** | Related policies, ideas, solutions, startups (`/s/{slug}`), actors | **PLANNED** | Challenges exist as `challenge:*` ids; no inspector link row yet. |
| **Policy** | Issuing actor, affected startups | **PARTIAL LIVE** | Policy nodes (`policy:*`) + `policy_relations.json`; D5 policy chapter merges with org `relations.json`. Same-country rule in bundle build. |
| **Hubs chapter** | HubMap `/hubs/{slug}/` | **PLANNED** | Hub actors in graph; `hubs-data.json` slugs: `externado`, `landivar`, `emprende-up`, `el-salvador`, `lci-veritas`. `hubs.js` already links startups → `/s/`. |
| **Actor (ecosystem)** | Nexus card `/s/{slug}` | **PARTIAL LIVE** | Inspector renders `nexus.card_slug` (`ecosystem.mjs`); build script can set slugs from one-pagers—many actors still `null`. |
| **Actor** | Website, LinkedIn | **LIVE** | Inspector + cards tab; PENDIENTE when missing. |
| **Actor** | Wiki page fallback | **PLANNED** | Portfolio uses wiki search for CT nodes; dedicated actor book **3042** pending approval. |

---

## 5. Country separation

Ecosystem UI treats **Peru**, **Colombia**, and **El Salvador** as separate ecosystems (filters, map focus, chapter `countries` arrays in story config). **Guatemala** and **Costa Rica** are empty states in actor data today.

| Country | Actors (bundle) | Policies (bundle) |
|---------|-----------------|-------------------|
| Peru | 201 | 15 |
| Colombia | 8 (institutions-focused deck) | 14 |
| El Salvador | 77 | 11 |

**Rule:** Policies and `policy_relations` only connect actors in the **same country** (Peru policy rows use `country: "Peru"`, etc.; `story.mjs` uses per-country policy geo). Do not cross-wire PE policy nodes to CO startups in the public bundle.

HubMap additionally includes country-specific hub pages (e.g. Colombia `externado`, `landivar`; Peru `emprende-up`; El Salvador `el-salvador`).

---

## 6. Visitor journeys (examples)

### A — Challenge → policy → actor → startup → Wiki

1. Open **Guided story** → **Challenges** → select a challenge node (e.g. `challenge:PE-2-agua`).  
2. Move to **Policy** → see `issues_policy` / `addresses_challenge` (solid vs dashed).  
3. Click a **government or program actor** in the inspector (**Actor cards** tab or map selection).  
4. Follow **Nexus profile** → `/s/{slug}` when `nexus.card_slug` is set (otherwise portfolio or Ideas search).  
5. **PLANNED:** deep link to **Actor Wiki** (book 3042) when page exists; today Idea Browser wiki links are startup-centric.

### B — Hub → HubMap → people → startups

1. **Hubs** story chapter or filter hub-category actors.  
2. Open **HubMap** → `/hubs/{slug}/` for campus, team, CLP startups (`hubs-data.json`).  
3. From hub startup list → `/s/{slug}` (live in `hubs.js`).  
4. Optional: **startup portfolio** for cohort-wide view and CT taxonomy wiki search.

---

## 7. Data flow (build → deploy)

```text
Canva maps / manual curation
    → actors.raw.json, relations.json
research/ecosystem-policy (+ SINIA Peru, Colombia sources)
    → policies.json, policy_relations.json
onepagers + hubs + mentor rosters (future edge derivations)
    → scripts/ecosystem/build_public_data.py
    → sanitized static/ecosystem/data/*
merge to main → deliberate VPS promote (apply_live.sh)
    → nexus.cleantechhub.net/ecosystem/ (+ /hubs/, /s/, etc.)
```

---

## 8. Related docs

- Product/technical spec: `docs/ecosystem-ref/spec.md`  
- Design directions (D3 hybrid): `docs/ecosystem-ref/directions.md`  
- Geocoding & deploy caution: `ops/ecosystem/README.md`

---

*Internal review only. Do not deploy this folder to production or share outside CTH/REIN staff without approval.*
