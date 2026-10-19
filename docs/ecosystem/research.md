# Nexus Ecosystem Graph — Platform Research

**Date:** 2026-10-19  
**Scope:** How leading ecosystem / climate-tech intelligence products model **entities**, **relationships**, and **interaction patterns** — inputs for Nexus LATAM (CTH + REIN, EN/ES).  
**Current Nexus baseline:** `static/ecosystem/` on branch `feat/ecosystem-env` — 286 actors, 75 typed edges, card grid + `vis-network` panel, staff gate via Nexus auth ([`site/nexus-auth/gate.html`](../../site/nexus-auth/gate.html)).

---

## Executive synthesis

| Pattern | Who uses it | Nexus takeaway |
|--------|-------------|----------------|
| **Curated graph** (orgs + people + deals as first-class edges) | Crunchbase, Dealroom, Briter, Endeavor | Edges must be typed, sourced, and filterable; cards alone are insufficient. |
| **Taxonomy-first drill-down** (challenge → vertical → players) | Net Zero Insights, Sightline, Startup Genome | LATAM cleantech needs REIN/CTH sector ontology aligned to CLP verticals, not only “category chips”. |
| **Force / SNA layout + ego depth** | Kumu, Graph Commons, Obsidian, Endeavor multiplier maps | Default UX: force graph + **local graph depth** + centrality-driven node size. |
| **Geo + segment maps** | StartupBlink, Dealroom (`geojson_url`), deck.gl-style arc maps | LATAM map is a **lens**, not the only view; combine with graph. |
| **Static market maps + relational DB behind** | PitchBook, Dealroom market maps | Good for PDFs; Nexus should generate similar **exports** from live graph. |
| **Stage / lifecycle framing** | Startup Ecosystem Canvas, Startup Genome lifecycle | Use for **onboarding** and empty states, not as the primary graph schema. |
| **Jobs / directory without graph** | Climatebase | Useful for future “talent edges” (`employed-at`, `hiring-for`) — not a graph UX reference today. |

---

## 1. Dealroom — Ecosystem Platform & API

**URLs:** [Ecosystem Platform](https://dealroom.co/ecosystems-network/), [Ecosystem object (API docs)](https://developers.dealroom.co/objects/ecosystem), [List ecosystems API](https://developers.dealroom.co/api-reference/ecosystems/list-ecosystems), [Market maps API](https://dealroom.co/api/marketmaps), [Platform llms index](https://dealroom.co/llms.txt)

### Data model
- **Ecosystem** = curated, filter-backed **entity collection** with branding, access control, optional region, **GeoJSON** boundary, tab config, and saved “landscapes” (entity lists). Fields include `filter`, `geojson_url`, `anonymous_access`, `tabs_config`, colors, currency ([Ecosystem object](https://developers.dealroom.co/objects/ecosystem)).
- **Entities** (companies, investors, people, universities, gov/NGO) share a unified index; **relationship cards** materialize edges: funding rounds, investments, founders, jobs, child orgs, similar orgs, etc. ([List ecosystems API](https://developers.dealroom.co/api-reference/ecosystems/list-ecosystems) — Entities/Transactions tags).
- **Market maps / landscapes** = segmented company lists with public JSON feeds linking list → companies API ([marketmaps](https://dealroom.co/api/marketmaps)).

### Visuals & UX
- White-label **ecosystem portals**: metrics (EV, funding, unicorns, exits), entity search, comparisons ([ecosystems-network](https://dealroom.co/ecosystems-network/)).
- **Geo** via ecosystem GeoJSON + regional filters.
- **Charts** via chart factory API ([llms.txt](https://dealroom.co/llms.txt)).
- Less emphasis on public force-graph; strength is **filtered tables + landscapes + geo**.

### Tech (public)
- REST API (`api-next.dealroom.co`), Auth0, version header; ecosystems are user-owned collections atop entity graph.

### Implications for Nexus
- Treat **REIN Hub Perú**, **Externado CO**, etc. as **Ecosystem objects** with slug, brand skin, and saved views.
- Store **`filter` DSL** or JSON filter spec mirroring UI chips (country, category, min-degree).
- Plan **GeoJSON** for LATAM focus countries when city coords exist.

---

## 2. StartupBlink — Global Map & Index

**URLs:** [Global startup map](https://www.startupblink.com/startups), [Ecosystem success / methodology blog](https://www.startupblink.com/blog/assessing-startup-ecosystem-success/), [2024 trends](https://www.startupblink.com/blog/global-startup-ecosystem-trends-in-2024/), [Ecosystem Pro Dashboard](https://lp.startupblink.com/ecosystem-pro-dashboard/), [GSER 2024 PDF (mirror)](https://www.nordichq.com/wp-content/uploads/2024/11/startup-blink-startupecosystemreport2024-1.pdf)

### Data model
- **Entities:** startups, unicorns, exits, corporates, support orgs — crowdsourced map + partner feeds (Crunchbase, Semrush, Statista) ([blog](https://www.startupblink.com/blog/assessing-startup-ecosystem-success/)).
- **Edges:** implicit (co-location, sector tags); index is **scored** not primarily relational.
- **Parameters:** dozens of algorithm inputs; 2024 adds scientific papers, sovereign credit ratings, “fading” for unicorn age ([blog](https://www.startupblink.com/blog/assessing-startup-ecosystem-success/)).

### Visuals & UX
- **Geo map** with region / country / city browse; industry + sub-industry filters ([startups](https://www.startupblink.com/startups)).
- **Ranking tables** (1000+ cities) with population/region filters; Pro **health checks** across 40+ parameters ([Pro Dashboard](https://lp.startupblink.com/ecosystem-pro-dashboard/)).
- Funding & employment **time-series charts** per location.

### Implications for Nexus
- Borrow **country comparison bar charts** (already in current Nexus ecosystem page) but wire to **graph metrics** (density, clustering, mentor coverage) not just actor counts.
- Pro-style **“health check”** panel for PE/SV/CO vs LATAM peers — future phase.

---

## 3. Crunchbase — Entity graph & cards

**URLs:** [Organization (v3.1)](https://data.crunchbase.com/v3.1/docs/organization), [Entity Lookup API](https://data.crunchbase.com/docs/using-entity-lookup-apis), [Investment cards](https://data.crunchbase.com/reference/getinvestmentcard-1), [OpenAPI-derived data model (YAML)](https://raw.githubusercontent.com/api-evangelist/crunchbase-data/refs/heads/main/data-model/crunchbase-data-data-model.yml)

### Data model
- **Organizations** (company, investor, school, group) with roles; **People**; **Funding rounds**; **Investments** linking investor ↔ organization ↔ round ([Organization](https://data.crunchbase.com/v3.1/docs/organization)).
- **Graph center:** `organizations` with 41+ relationship **cards** (founders, investors, participated_investments, child_organizations, jobs, etc.) ([data model YAML](https://raw.githubusercontent.com/api-evangelist/crunchbase-data/refs/heads/main/data-model/crunchbase-data-data-model.yml)).
- Identifiers: `{ uuid, permalink, entity_def_id }` — agents follow permalinks.

### Visuals & UX
- Profile-centric UI; **lists and search**; market maps are secondary to entity pages.
- Investment traversal: organization → `participated_investments` card → funding_round, partner ([examples](https://data.crunchbase.com/docs/examples-entity-lookup-api)).

### Implications for Nexus
- Adopt **permalink/slug** stability (`pe-emprende-up-climatech-rein-hub-peru`) and **edge provenance** (`source`, `source_design_id`, `notes`) like existing `relations.json`.
- Model **Investment** as reified edge or hyper-edge (round + amount + date) when CLP/funder data arrives.

---

## 4. Startup Genome — Lifecycle & dashboards

**URLs:** [Lifecycle model report PDF](https://startupgenome.com/contents/report/startup-genome-research-article--startup-ecosystem-lifecycle-model-and-phases-2017-and-2019.pdf), [CARIBEquity tool (IDB)](https://startupgenome.com/insights/idbcaribequity), [Insights hub](https://startupgenome.com/insights), [Methodology (Drive)](https://drive.google.com/file/d/1sKHMPxne-HXi1ZbFakZzDHPWdeoiy8fh/view)

### Data model
- **Ecosystem-level metrics:** Output (# startups), Success Factors, Lifecycle phase (Activation → Globalization → Expansion → Integration) ([PDF](https://startupgenome.com/contents/report/startup-genome-research-article--startup-ecosystem-lifecycle-model-and-phases-2017-and-2019.pdf)).
- **Factors:** Resource Attraction, Startup Leakage, Triggers (exits/unicorns) ([Methodology](https://drive.google.com/file/d/1sKHMPxne-HXi1ZbFakZzDHPWdeoiy8fh/view)).
- Not a public org-org graph; relational logic is **benchmarking**.

### Visuals & UX
- Scroll-based **microsites**: lifecycle phase, success factor scores, comparisons, funding charts, directory ([CARIBEquity](https://startupgenome.com/insights/idbcaribequity)).
- Color-coded phase indicators; ranking views.

### Implications for Nexus
- Optional **lifecycle badge** per country (PE/SV/CO) on map panel — narrative layer atop graph.
- IDB Lab CARIBEquity pattern validates **public microsite + directory + comparisons** for donor/gov audiences ([IDB Lab blog](https://bidlab.org/en/blog/entrepreneurial-innovation-caribbean-fragmentation-expansion)).

---

## 5. Kumu — Network maps & SNA

**URLs:** [Force-directed layout](https://docs.kumu.io/guides/layouts/force-directed), [@settings reference](https://docs.kumu.io/overview/advanced-editor-hub/settings-reference), [Metrics (SNA)](https://docs.kumu.io/guides/metrics), [Architecture](https://docs.kumu.io/overview/kumus-architecture)

### Data model
- **Elements** (nodes), **connections** (directed/undirected/mutual), **loops**; maps hold positions + default behaviors ([architecture](https://docs.kumu.io/overview/kumus-architecture)).
- **Fields** on elements drive layout (geo, scatter x/y) and decoration.

### Visuals & UX
- **Force-directed** default for stakeholder/SNA templates: gravity, charge, spring length/strength ([force-directed](https://docs.kumu.io/guides/layouts/force-directed)).
- **Geo template:** `geo-location` field, map styles ([settings](https://docs.kumu.io/overview/advanced-editor-hub/settings-reference)).
- **Focus / showcase**, **cluster**, **bridge**, **ignore-orphans** ([settings](https://docs.kumu.io/overview/advanced-editor-hub/settings-reference)).
- **Metrics:** degree, betweenness, closeness, eigenvector, reach — bind to size/color ([metrics](https://docs.kumu.io/guides/metrics)).

### Implications for Nexus
- Ship **orphan toggle**, **focus mode** (ego), **pin** hub nodes (REIN hubs, ministries).
- Expose **betweenness** to find bridge orgs (e.g. ProInnóvate ↔ incubators).

---

## 6. Graph Commons — Typed spreadsheet → graph

**URLs:** [Importing data](https://docs.graphcommons.com/create/importing-data.md), [API](https://docs.graphcommons.com/build/api.md), [API reference](https://graphcommons.github.io/api-v1/), [Product](https://graphcommons.com/)

### Data model
- **nodeTypes** / **edgeTypes** (schema) vs **nodes** / **edges** (instances).
- CSV: edges require `From Type, From Name, Edge Type, To Type, To Name`; optional **Weight** ([importing](https://docs.graphcommons.com/create/importing-data.md)).
- API returns layout algorithm params, per-node **degree_centrality**, weighted edges ([API reference](https://graphcommons.github.io/api-v1/)).

### Visuals & UX
- Force-directed layout; **data table** side-by-side with graph ([editing data table](https://docs.graphcommons.com/create/editing-data-table.md)).
- AI-assisted graph expansion (2025+) ([graphcommons.com](https://graphcommons.com/)).

### Implications for Nexus
- Staff workflow: edit **`relations.csv`** / JSON in repo → CI validates → deploy bundle.
- Weight column = co-funding amount or mentor session count when available.

---

## 7. Climatebase — Climate jobs & org directory

**URLs:** [Jobs](https://climatebase.org/jobs), [Organizations](https://climatebase.org/organizations), [Home](https://jobs.climatebase.org/)

### Data model
- **Organizations** with sector, size, workplace, location; **Jobs** linked to orgs ([jobs](https://climatebase.org/jobs)).
- Relational job↔org; **no public network map**.

### Visuals & UX
- Heavy **faceted search** (sector, org type, experience, remote) ([jobs](https://climatebase.org/jobs)).
- Fellowship, events, climate weeks modules ([home](https://jobs.climatebase.org/)).

### Implications for Nexus
- Future **`employed-at` / `programs-with`** edges from jobs data; UX reference for **filter chips**, not graph layout.

---

## 8. Net Zero Insights — Climate-first taxonomy & Market Compass

**URLs:** [Platform](https://netzeroinsights.com/), [Climate Tech Taxonomy](https://netzeroinsights.com/resources/the-climate-tech-taxonomy/), [Market Compass](https://netzeroinsights.com/resources/new-feature-market-compass/), [Market research](https://netzeroinsights.com/resources/climate-tech-market-research/)

### Data model
- **Taxonomy:** challenge areas → verticals → technology pathways → companies/investors/deals ([taxonomy](https://netzeroinsights.com/resources/the-climate-tech-taxonomy/)).
- **Players** typed: Champions / Emerging / New / Acquired; investors by asset class ([Market Compass](https://netzeroinsights.com/resources/new-feature-market-compass/)).
- **Signals:** deployments, partnerships, offtake — not only funding ([platform](https://netzeroinsights.com/)).

### Visuals & UX
- **Explore** drill-down; **Players** market map by sub-vertical; **Reports** snapshots.
- **Ecosystem activity map** (companies, investors, corporates) on platform home ([platform](https://netzeroinsights.com/)).

### Implications for Nexus
- Align actor **`sector` / CLP tags** (`CT-AF-010`, etc.) to a **3-level taxonomy** for filter and edge typing (`works_on_challenge` already in Nexus relations).

---

## 9. PitchBook — Market Maps (segment landscapes)

**URLs:** [Market Maps product](https://pitchbook.com/products/desktop/discovery/market-maps-tool), [How to use](https://pitchbook.com/help/how-to-use-market-maps-in-pitchbook), [Sector taxonomies report](https://pitchbook.com/news/reports/market-maps), [Discovery overview](https://pitchbook.com/products/desktop/discovery)

### Data model
- **Companies** in segments; underlying search criteria saved with map ([help](https://pitchbook.com/help/how-to-use-market-maps-in-pitchbook)).
- Deals, investors, valuations linked in Desktop — graph is **implicit** in data model.

### Visuals & UX
- **Logo treemap / segment grid**; export PNG/PDF/PPT/Excel ([product](https://pitchbook.com/products/desktop/discovery/market-maps-tool)).
- Industry overview charts: deal activity, top investors ([discovery](https://pitchbook.com/products/desktop/discovery)).

### Implications for Nexus
- **Export mode:** segment grid for “Colombia institutions” deck + **SVG graph** for relationship story.
- Climate tech segments exist in PitchBook maps ([reports](https://pitchbook.com/news/reports/market-maps)) — benchmark segment naming.

---

## 10. Sightline Climate (CTVC) — Value chain & capital stack maps

**URLs:** [Sightline for new climate economy](https://www.ctvc.co/a-sightline-for-the-new-climate-economy/), [Climate Capital Stack map](https://www.ctvc.co/who-are-the-climate-tech-investors/), [Platform](https://www.sightlineclimate.com/platform), [Grid tech market map example](https://www.ctvc.co/grid-tech-hardware/)

### Data model
- **Climate-first taxonomy:** 7 verticals, 60+ sectors, 300+ technologies ([CTVC](https://www.ctvc.co/a-sightline-for-the-new-climate-economy/)).
- Relational: companies ↔ investors ↔ deals ↔ technologies; readiness scores ([platform](https://www.sightlineclimate.com/platform)).

### Visuals & UX
- **Sector Compass** + dynamic **market map** (value chain layers) ([CTVC](https://www.ctvc.co/a-sightline-for-the-new-climate-economy/)).
- Public **Capital Stack** map: filter by investor type & geography, download image ([capital stack](https://www.ctvc.co/who-are-the-climate-tech-investors/)).

### Implications for Nexus
- REIN/CTH **funder layer** view = simplified capital stack for LATAM cleantech.
- Link nodes to **`/s/{slug}`** one-pagers like Sightline links to profiles.

---

## 11. Endeavor Insight — Multiplier / founder network maps

**URLs:** [Multiplier Effect](https://multipliereffect.endeavor.org/the-multiplier-effect), [Mapping Poland](https://endeavor.org/mapping-polands-tech-sector/), [Spain report PDF](https://endeavor.org/wp-content/uploads/dlm_uploads/2022/09/Endeavor-Insight-Mapping-Spains-Tech-Sector-1.pdf), [Insight services](https://endeavor.org/insight/)

### Data model
- **Nodes:** companies (founders collapsed to flagship org).
- **Edges (typed, colored):** former employment, mentorship, angel investment, serial entrepreneurship ([Spain PDF](https://endeavor.org/wp-content/uploads/dlm_uploads/2022/09/Endeavor-Insight-Mapping-Spains-Tech-Sector-1.pdf)).
- **Node size:** function of k-hop reach in network ([Poland](https://endeavor.org/mapping-polands-tech-sector/)).
- Sources: interviews + LinkedIn + Crunchbase + PitchBook ([multiplier](https://multipliereffect.endeavor.org/the-multiplier-effect)).

### Visuals & UX
- Interactive map; **year-founded** time filter; legend by edge type ([Spain PDF](https://endeavor.org/wp-content/uploads/dlm_uploads/2022/09/Endeavor-Insight-Mapping-Spains-Tech-Sector-1.pdf)).
- **Ego / ripple** views for flagship companies (DocPlanner, Booksy) ([Poland](https://endeavor.org/mapping-polands-tech-sector/)).

### Implications for Nexus
- Add **`mentored`**, **`alumni-of`**, **`invested-in`** when merging `mentor_cards.json` + CLP roster.
- Size REIN hubs by **incubated** out-degree — matches multiplier narrative.

---

## 12. LAVCA — LATAM VC data & directory

**URLs:** [2026 Ecosystem Insights](https://www.lavca.org/research/2026-startup-ecosystem-insights/), [2025 Insights + data portal](https://www.lavca.org/research/2025-latin-american-startup-ecosystem-insights/), [Research hub](https://www.lavca.org/research/), [2026 Trends in Tech](https://www.lavca.org/research/2026-lavca-trends-in-tech/)

### Data model
- **Transactions** (VC by stage, country, sector); **directory** of 1000+ startups ($1M+ raised) with founders, gender, rounds ([2025](https://www.lavca.org/research/2025-latin-american-startup-ecosystem-insights/)).
- Graph not public; **tables + portal** for members.

### Visuals & UX
- Report charts; **interactive data portal** (sort/download) for members ([2025](https://www.lavca.org/research/2025-latin-american-startup-ecosystem-insights/)).
- Emerging **hub rankings** ([2026](https://www.lavca.org/research/2026-startup-ecosystem-insights/)).

### Implications for Nexus
- Crosswalk Nexus startups to LAVCA directory IDs when fundraising data is added.
- Hub ranking metrics could mirror graph **betweenness** of REIN nodes.

---

## 13. IDB Lab / IDB — Regional ecosystem mapping

**URLs:** [CARIBEquity blog](https://bidlab.org/en/blog/entrepreneurial-innovation-caribbean-fragmentation-expansion), [CARIBEquity product](https://bidlab.org/en/products/knowledge-and-connections/caribequity), [Fintech LAC study (IDB news)](https://www.iadb.org/en/news/study-fintech-ecosystem-latin-america-and-caribbean-exceeds-3000-startups), [Fintech report PDF](https://publications.iadb.org/publications/english/document/Fintech-in-Latin-America-and-the-Caribbean-A-Consolidated-Ecosystem-for-Recovery.pdf)

### Data model
- Ecosystem assessment: startups, investors, ESOs; **interactive digital mapping tool** ([blog](https://bidlab.org/en/blog/entrepreneurial-innovation-caribbean-fragmentation-expansion)).
- Fintech: country counts, segments — **statistical**, maps in reports ([IDB news](https://www.iadb.org/en/news/study-fintech-ecosystem-latin-america-and-caribbean-exceeds-3000-startups)).

### Visuals & UX
- CARIBEquity digital tool (Startup Genome–built): lifecycle, comparisons, directory ([CARIBEquity SG article](https://startupgenome.com/insights/idbcaribequity)).
- Fintech **regulation map** (interactive) cited in IDB/Finnovista reports ([PDF](https://publications.iadb.org/publications/english/document/Fintech-in-Latin-America-and-the-Caribbean-A-Consolidated-Ecosystem-for-Recovery.pdf)).

### Implications for Nexus
- Position Nexus as **operational graph** for CTH/REIN programs (CLP, hubs) vs IDB-style **policy benchmarking**.
- GT/CR empty states align with IDB “mapping in progress” messaging.

---

## 14. Briter (Briter Bridges) — Emerging markets intelligence

**URLs:** [Data platform](https://www.briter.co/data), [Home](https://www.briter.co/), [Intelligence Hub / market maps](https://www.briter.co/intelligence-hub), [Reports](https://www.briter.co/insights/reports)

### Data model
- **Organizations**, **investors**, **deals**, **hubs/accelerators**, sectors, SDG/impact tags ([data](https://www.briter.co/data)).
- ~20k orgs, 15k deals — relational DB with dashboards.

### Visuals & UX
- **Sector market maps** (static) + platform filters, exports, white-label ([intelligence hub](https://www.briter.co/intelligence-hub)).
- LATAM coverage alongside Africa/Asia ([home](https://www.briter.co/)).

### Implications for Nexus
- Comparable **scope** for LATAM cleantech subset; Nexus differentiator = **program-native edges** (CLP, REIN incubation).

---

## 15. Startup Ecosystem Canvas — Stage/supporter taxonomy

**URLs:** [Founder Institute canvas](https://fi.co/canvas), [Grow / community mapping](https://fi.co/grow)

### Data model
- **Stages:** Idea → Launch → Growth.
- **Supporters:** Evangelists, Government, Talent (universities, employers) ([canvas](https://fi.co/canvas)).
- Not a graph — **checklist of resource types**.

### Visuals & UX
- Infographic canvas per city; reduces fragmentation for newcomers ([grow](https://fi.co/grow)).

### Implications for Nexus
- Use as **secondary “resources by stage”** panel linked from graph nodes (e.g. accelerator → Launch stage).

---

## 16. Obsidian — Graph view (knowledge graph UX)

**URLs:** [Graph view help](https://obsidian.md/help/plugins/graph), [Changelog 0.9.0 (forces)](https://obsidian.md/changelog/2020-09-21-desktop-v0.9.0/)

### Data model
- **Nodes** = notes; **edges** = internal links; tags as node classes.

### Visuals & UX
- Global vs **local graph** with **depth slider** ([help](https://obsidian.md/help/plugins/graph)).
- Filters: search syntax, orphans, attachments; **groups** by color.
- **Forces:** center, repel, link force, link distance ([help](https://obsidian.md/help/plugins/graph)).
- **Time-lapse** by file creation time ([help](https://obsidian.md/help/plugins/graph)).

### Implications for Nexus
- **Local graph (ego)** is the highest-ROI daily UX — copy depth slider + neighbor-link toggle patterns.
- Orphan filter matches sparse Canva extract (many zero-degree actors).

---

## 17. Cassandra Xia / Climate Draft — Sector treemap (adjacent)

**URL:** [Climate map](https://cassandraxia.com/climate-map/)

- **Visual:** Project Drawdown taxonomy × companies sized by employees ([climate-map](https://cassandraxia.com/climate-map/)).
- Not relationship-first; useful for **sector gap** storytelling alongside graph.

---

## 18. Open-source graph stacks (implementation references)

| Library | Role | Docs |
|--------|------|------|
| **Cytoscape.js** | Web graph + layouts (cose, fcose), styling, extensions | [js.cytoscape.org](https://js.cytoscape.org/) |
| **sigma.js + graphology** | WebGL large graphs, ForceAtlas2 | [sigmajs.org](https://www.sigmajs.org/), [graphology](https://graphology.github.io/) |
| **vis-network** | Canvas force graph (used in current Nexus ecosystem page) | [visjs.org](https://visjs.github.io/vis-network/docs/network/) |
| **deck.gl ArcLayer + MapLibre** | Geo arcs for flows (investment, mentorship) | [deck.gl ArcLayer](https://deck.gl/docs/api-reference/layers/arc-layer), [MapLibre](https://maplibre.org/) |
| **d3-force** | Obsidian-style simulation | [d3-force](https://d3js.org/d3-force) |

---

## Current Nexus data snapshot (feat/ecosystem-env)

Source: `static/ecosystem/data/README.md` on `origin/feat/ecosystem-env`.

| Metric | Value |
|--------|-------|
| Actors | 286 |
| Edges | 75 |
| Countries | PE 201, SV 77, CO 8; GT/CR empty |
| Edge types | `works_on_challenge` (35), `hosts` (9), `runs_program`, `cofunds`, `incubated`, … |
| Gaps | No persons; few `/s/` links; Colombia institutions-only |

---

## References (quick index)

1. Dealroom — https://dealroom.co/ecosystems-network/  
2. StartupBlink — https://www.startupblink.com/startups  
3. Crunchbase — https://data.crunchbase.com/v3.1/docs/organization  
4. Startup Genome — https://startupgenome.com/insights/idbcaribequity  
5. Kumu — https://docs.kumu.io/guides/layouts/force-directed  
6. Graph Commons — https://docs.graphcommons.com/create/importing-data.md  
7. Climatebase — https://climatebase.org/jobs  
8. Net Zero Insights — https://netzeroinsights.com/resources/the-climate-tech-taxonomy/  
9. PitchBook — https://pitchbook.com/products/desktop/discovery/market-maps-tool  
10. Sightline / CTVC — https://www.ctvc.co/who-are-the-climate-tech-investors/  
11. Endeavor Insight — https://multipliereffect.endeavor.org/the-multiplier-effect  
12. LAVCA — https://www.lavca.org/research/2026-startup-ecosystem-insights/  
13. IDB Lab — https://bidlab.org/en/blog/entrepreneurial-innovation-caribbean-fragmentation-expansion  
14. Briter — https://www.briter.co/data  
15. Startup Ecosystem Canvas — https://fi.co/canvas  
16. Obsidian Graph — https://obsidian.md/help/plugins/graph  
