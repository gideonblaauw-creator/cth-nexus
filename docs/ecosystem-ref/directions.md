# Nexus Ecosystem — Five Design Directions (OSS Research)

**Date:** 2026-10-20  
**Branch:** `research/ecosystem-directions`  
**Builds on:** [`research.md`](research.md), [`spec.md`](spec.md), [`prototype/index.html`](prototype/index.html) (sigma.js baseline — not repeated here)  
**Data:** 286 actors, 75 relations (`docs/ecosystem/prototype/data/`)

---

## 1. Live site check (2026-10-20)

| URL | HTTP | What we could observe |
|-----|------|------------------------|
| [`/ecosystem/`](https://nexus.cleantechhub.net/ecosystem/) | **302** → `/nexus-auth/?next=/ecosystem/` | Staff gate (Caddy `forward_auth` + Flask `nexus_auth`). Unauthenticated fetch shows Spanish gate copy (“Acceso al directorio… @cleantechhub.net”). **Page content, cards, map, and vis-network not visible without session.** |
| [`/ecosystem/data/actors.json`](https://nexus.cleantechhub.net/ecosystem/data/actors.json) | **401** JSON | Data bundle correctly protected behind same auth. |
| [`/hubs/`](https://nexus.cleantechhub.net/hubs/) | **200** | Public REIN Hubs LATAM shell loads (Caddy static). Confirms Nexus front door healthy; ecosystem is the gated exception. |

### Why a “real” LATAM map likely does not show (even after staff login)

From **`origin/feat/ecosystem-env`** (closest GitHub mirror of production static bundle):

1. **No geospatial stack in repo** — `index.html` uses an inline **SVG caricature** of countries (`#latam-map`), not Leaflet, MapLibre, or tile URLs. Country click toggles filter only.
2. **No coordinates in data** — actors have `country` / occasional `city` (77× `San Salvador` only); **zero `geo.lat/lng`** in GitHub JSON.
3. **“Map” is not a basemap** — even with auth, users see schematic polygons + bar chart, not OSM/Protomaps.
4. **VPS-only Leaflet/OSM fix** — Gideon noted commits `3d7079ac` / `79d042ef` deployed on VPS today; **neither SHA exists in this GitHub remote**. Until those commits land on a tracked branch, GitHub `feat/ecosystem-env` still describes the SVG + card UI.
5. **Possible VPS regressions** — if Leaflet was added locally, typical failure modes are: missing `leaflet.css`, blocked tile CDN, JS error before init, or auth-gated relative paths to `data/*.json`. We could not verify authenticated DOM from this agent run.

### Why the relations panel feels “cheap”

`ecosystem.js` on `feat/ecosystem-env` uses **vis-network** with default physics, **single gray edge color**, no ego depth, no typed legend, no edge labels, no graph-first layout (cards + charts dominate). That matches Gideon’s “cheap version” feedback vs Kumu / Graph Commons / Endeavor maps.

---

## 2. Embeddable open-source survey

**Fit key:** ★★★ = strong for 286 nodes / 75 typed edges + staff static embed; ★ = weak or wrong license.

| Tool | License | Maturity | Last release (approx.) | Embed effort | Fit for Nexus data | URL |
|------|---------|----------|------------------------|--------------|-------------------|-----|
| **sigma.js** + **graphology** | MIT | ★★★ WebGL standard | sigma **4.0.3** (2026-10-15); graphology **0.26.0** (2026-02-08) | **S** — CDN + JSON | ★★★ Force/geo hybrid, ego filter, path find; v4 + `@sigma/layer-maplibre` | https://www.sigmajs.org/ , https://graphology.github.io/ |
| **Cytoscape.js** (+ fcose/cose-bilkent) | MIT | ★★★ | **3.30.x** active | **S–M** | ★★★ Rich styling, compound clusters (country), a11y plugins | https://js.cytoscape.org/ |
| **vis-network** (current) | MIT / Apache | ★★ legacy | **9.1.9** | **S** (already in prod) | ★★ OK &lt;500 nodes; weak SNA UX | https://visjs.github.io/vis-network/ |
| **@cosmos.gl/graph** (cosmos.gl) | MIT | ★★ GPU force | npm active 2025–26 | **M** | ★★★ Wow factor for dense graphs; layout+render one package | https://github.com/cosmosgl/graph , https://cosmos.gl |
| **@cosmograph/cosmograph** | **CC-BY-NC-4.0** | ★★ productized | **2.5.1** (2026-08) | **M** | ★★ **Not OSS for CTH commercial site** — needs business license | https://cosmograph.app/licensing/ |
| **deck.gl** ArcLayer / GeoJsonLayer | MIT | ★★★ | **9.x** | **M** with MapLibre | ★★★ Cross-border **cofunds/incubated** arcs when lat/lng exist | https://deck.gl/ |
| **MapLibre GL JS** | BSD-3 | ★★★ | **4.7.x** | **S** | ★★★ Real LATAM basemap + vector tiles | https://maplibre.org/ |
| **OpenFreeMap** / **Protomaps** tiles | **ODbL** / **BSD** tiles | ★★★ | 2025–26 | **S** (style URL) | ★★★ No Mapbox token; attribution on footer | https://openfreemap.org/ , https://protomaps.com/ |
| **Kepler.gl** | MIT | ★★ (Uber) | 3.x maintenance | **L** — React app | ★★ Great geo+time if we adopt React embed | https://kepler.gl/ |
| **Leaflet** + OSM raster | BSD / ODbL data | ★★★ | **1.9.x** | **S** | ★★ Fine for pins; arcs need plugin or deck overlay | https://leafletjs.com/ |
| **d3-force** / **d3-chord** | ISC | ★★★ | d3 **7.9** | **S** | ★★ Matrix/story views; not primary graph at scale | https://d3js.org/ |
| **Gephi Lite** | **GPL-3.0** | ★★ | 2024–25 | **M** (iframe) | ★ Copyleft — **avoid embed** in Nexus static; use as analyst desktop | https://gephi.org/gephi-lite/ |
| **Onodo** (Bulgarian EU) | AGPL / hosted | ★★ | maintained | **L** self-host | ★ AGPL + server; better as export target | https://onodo.org/ |
| **Graph Commons** | **SaaS** (API) | ★★★ UX ref | n/a | **L** | ★ Not OSS — schema/import pattern only | https://graphcommons.com/ |
| **Kumu** | **SaaS** | ★★★ UX ref | n/a | n/a | Reference for metrics/ego, not embed | https://kumu.io/ |
| **InfraNodus** | **SaaS** | ★★ | n/a | n/a | Text/network AI — not actor JSON embed | https://infranodus.com/ |
| **Flourish** | **Proprietary** | ★★★ | n/a | **S** iframe | ⚠️ **Not OSS** — pretty stories, license cost | https://flourish.studio/ |
| **Obsidian graph** | **Proprietary** | ★★ UX ref | n/a | n/a | Local graph UX patterns only | https://obsidian.md/ |
| **Retina** (BBVA) | Mixed / research | ★ | old | **L** | ★ Institutional maps — not maintained embed | (archived references) |
| **StartupBlink / Dealroom / Crunchbase** | Proprietary | ★★★ refs | n/a | n/a | Benchmark only (geo+graph product patterns) | https://www.startupblink.com/ , https://dealroom.co/ |

**Non-OSS flagged:** Cosmograph (NC), Flourish, Kumu, Graph Commons hosted, Gephi Lite (GPL embed risk).

---

## 3. Five design directions

Static mockups: [`prototypes/`](prototypes/) · Screenshots: [`screenshots/`](screenshots/)

### Direction 1 — Geo-first LATAM map + flow arcs

| | |
|--|--|
| **User story** | As a **country lead**, I open the ecosystem page and immediately see **Peru / El Salvador / Colombia** on a real basemap with **program arcs** (cofunds, hosts, incubated) so I spot cross-border gaps and hub geography. |
| **Stack** | **MapLibre GL JS** + [**OpenFreeMap**](https://openfreemap.org/) `liberty` style + **deck.gl** `ArcLayer` + GeoJSON point layer. |
| **Data changes** | **`geo.lat/lng`** per actor (city geocode + country jitter); normalize **`country` → ISO**; optional **`edge.weight`** for arc width; keep **`type`** for arc filter. |
| **Interactions** | Pan/zoom; filter edge types; click pin → inspector; country chip sync; optional 3D pitch. |
| **Effort** | **M** (geocode pipeline + dual MapLibre/deck bundle ~120KB gzip). |
| **Risks** | Tile CDN blocked on corporate WiFi; inaccurate jitter until real cities; sparse arcs (only 75 edges). |
| **Brand fit** | ★★★ CTH cyan / REIN orange arc gradients match [`nexus-brand.css`](../../site/nexus-assets/nexus-brand.css). |
| **Mockup** | [`prototypes/d1-geo-arcs/index.html`](prototypes/d1-geo-arcs/index.html) · ![d1](screenshots/d1-geo-arcs.png) |

### Direction 2 — Force-directed SNA + clustering + ego view

| | |
|--|--|
| **User story** | As **REIN program staff**, I explore **who incubates whom** with a **Kumu-like** force graph, **focus REIN Hub Perú**, depth slider 1–3, node size = degree. |
| **Stack** | **Cytoscape.js** (cose/fCoSE) *or* **sigma.js 4** + **graphology-layout-forceatlas2**; optional **@cosmos.gl/graph** if we need GPU layout at 2k edges later. |
| **Data changes** | **`category`**, **`type`** on edges; computed **`degree` / betweenness** in CI; **`pin`** flag for anchor nodes (hubs, ministries). |
| **Interactions** | Search focus; ego depth; orphan toggle; path BFS; inspector with EN/ES edge labels. |
| **Effort** | **S–M** (replace vis-network; reuse existing JSON). |
| **Risks** | Hairball if we show all 286 with only 75 edges (many isolates); needs **min-degree** default & challenge-node policy. |
| **Brand fit** | ★★★ REIN orange hub halos; CTH deep blue edges — aligns with [`spec.md`](spec.md) Phase 1. |
| **Mockup** | [`prototypes/d2-force-cluster/index.html`](prototypes/d2-force-cluster/index.html) · ![](../screenshots/d2-force-cluster.png) |

### Direction 3 — Hybrid split: linked map + graph

| | |
|--|--|
| **User story** | As **mentor lead**, I **select an org on the map** and see its **local graph** on the right (Obsidian-style), with linked highlighting and country brush. |
| **Stack** | **MapLibre** (left) + **sigma.js** (right); shared selection bus in vanilla JS; same OpenFreeMap tiles. |
| **Data changes** | Same geocode as D1; **`nexus.card_slug`** on nodes for deep links; edge **`directed`** boolean. |
| **Interactions** | Click either pane; country filter; fly-to on map; graph re-layout subset. |
| **Effort** | **M** (two renderers + sync state). |
| **Risks** | Dual WebGL memory on low-end laptops; must respect **`prefers-reduced-motion`**. |
| **Brand fit** | ★★★ Matches Dealroom/StartupBlink “geo lens + graph lens” pattern from [`research.md`](research.md). |
| **Mockup** | [`prototypes/d3-hybrid-split/index.html`](prototypes/d3-hybrid-split/index.html) · ![](../screenshots/d3-hybrid-split.png) |

### Direction 4 — Matrix & flows (chord / Sankey)

| | |
|--|--|
| **User story** | As **funder outreach**, I see **which categories fund which** (funder→accelerator→startup) as **flow ribbons**, not only a hairball. |
| **Stack** | **d3-chord** / **d3-sankey** (ISC); optional **RAWGraphs** export for staff slides. |
| **Data changes** | **`weight`** on edges; **`sector[]`** tags; aggregate **`category × category × edgeType`** cube in `derived/flows.json`. |
| **Interactions** | Hover ribbon → list edges; click category → filter main graph; export SVG. |
| **Effort** | **M** (derivation job + second tab). |
| **Risks** | 75 edges → sparse chords; misleading flows if **`works_on_challenge`** dominates (35/75). |
| **Brand fit** | ★★ Strong for **PDF/deck** exports; secondary view, not primary landing. |
| **Mockup** | [`prototypes/d4-flow-matrix/index.html`](prototypes/d4-flow-matrix/index.html) · ![](../screenshots/d4-flow-matrix.png) |

### Direction 5 — Story-driven explorer + time slider

| | |
|--|--|
| **User story** | As **IDB/CTH stakeholder**, I walk **guided chapters** (Challenges → Policy → Capital → Hubs → Alliances) with a **timeline** when `since` / cohort years exist. |
| **Stack** | Vanilla **story rail** + **sigma** or SVG highlight layer; later **scrollama** / GSAP for donor microsite feel (Startup Genome CARIBEquity pattern). |
| **Data changes** | **`since` / `until`** on edges; **`founded_year`** on startups; story config JSON (`docs/ecosystem/stories/rein-latam.json`). |
| **Interactions** | Chapter click; range slider scrubs time; auto-zoom subgraph per chapter. |
| **Effort** | **L** (content + time fields mostly missing today). |
| **Risks** | Narrative stale without editorial workflow; time slider empty until CLP cohort dates merged. |
| **Brand fit** | ★★★ REIN storytelling; best as **mode** atop D2/D3, not standalone v1. |
| **Mockup** | [`prototypes/d5-story-explorer/index.html`](prototypes/d5-story-explorer/index.html) · ![](../screenshots/d5-story-explorer.png) |

---

## 4. Recommendation

**Primary: Direction 3 (Hybrid linked map + graph)**, implemented with **MapLibre + OpenFreeMap** and **sigma.js 4 + graphology** (per [`spec.md`](spec.md) stack).

**Why:**

1. Directly answers both gaps Gideon raised — **real LATAM map** (D1) and **serious network** (D2) in one staff workflow without flipping tabs blindly.
2. **All MIT/BSD** embed stack; no Cosmograph NC or Flourish lock-in.
3. **Incremental data path:** ship with country-centroid geocode (see `prototypes/shared/prepare_geo.py`), then replace with city geocode in Phase 3 (`ECO-17` in spec).
4. **Preserves** existing card grid / charts as secondary panel (staff already use cards); graph+map become hero.
5. **Direction 4** as analytics tab once mentor/funder weights arrive; **Direction 5** as REIN-branded “guided tour” after `since` fields exist.

**Phase 0.5 next steps (engineering, not this branch):** cherry-pick VPS Leaflet commits `3d7079ac` / `79d042ef` into GitHub; verify tile URL + CSP; migrate vis-network → sigma; add geocode CI artifact.

---

## 5. Artifacts on this branch

| Path | Purpose |
|------|---------|
| [`directions.md`](directions.md) | This document |
| [`prototypes/`](prototypes/) | Five static HTML mockups + shared geo JSON |
| [`screenshots/*.png`](screenshots/) | Capture of each mockup |
| [`prototypes/capture-screenshots.sh`](prototypes/capture-screenshots.sh) | Regenerate screenshots locally |

**Regenerate geo + screenshots:**

```bash
python3 docs/ecosystem/prototypes/shared/prepare_geo.py
bash docs/ecosystem/prototypes/capture-screenshots.sh
```

---

## 6. References (OSS & tiles)

- sigma.js — https://www.sigmajs.org/  
- graphology — https://graphology.github.io/  
- Cytoscape.js — https://js.cytoscape.org/  
- cosmos.gl — https://github.com/cosmosgl/graph  
- MapLibre — https://maplibre.org/  
- OpenFreeMap — https://openfreemap.org/  
- deck.gl — https://deck.gl/  
- Kepler.gl — https://kepler.gl/  
- Gephi Lite — https://gephi.org/gephi-lite/  
- Onodo — https://onodo.org/  
