# Research: UQHU & Yakufil (Peru water) — public sources only

Date accessed: 2026-10-21. Relations below were added to `ops/ecosystem/actor_relations_verified.csv` only when both endpoints exist in `actors.json`.

## New verified relations (added to CSV)

| from_id | to_id | type | Source |
|---------|-------|------|--------|
| `pe-jaku-emprende-unsa-arequipa` | `pe-yakufil` | `hub_startup` | [UNSA — Yakufil emprendimiento](https://www.unsa.edu.pe/yakufil-emprendimiento-unsa-que-revoluciona-el-tratamiento-de-aguas-residuales/) |
| `pe-proinnovate-startup-peru` | `pe-yakufil` | `funding` | [UNSA — Startup Perú 9G](https://www.unsa.edu.pe/emprendedores-de-la-unsa-ganan-concurso-y-recibiran-s-60-000-por-parte-de-startup-peru-9g/) |
| `pe-proinnovate-startup-peru` | `pe-yakufil` | `program_participation` | [ProInnóvate — Día del Agua 2024](https://www.gob.pe/institucion/proinnovate/noticias/924305-dia-del-agua-innovaciones-para-gestionar-el-cuidado-y-aprovechamiento-del-agua-en-el-peru) |
| `pe-caja-arequipa` | `pe-yakufil` | `funding` | [UNSA — Premio Orgullo Emprendedor](https://www.unsa.edu.pe/yakufil-emprendimiento-unsa-que-revoluciona-el-tratamiento-de-aguas-residuales/) |

Corroboration (not duplicated in CSV): Startup Perú 9G preliminary results list **YAKUFIL ECOINGENIERIA S.R.L.** as approved/acredited — [PDF](https://startup.proinnovate.gob.pe/wp-content/uploads/2023/04/Resultados-Preliminares-Startup-Peru-9G-Emprendimientos-Innovadores-17.04.23.pdf).

## UQHU — findings (no new actor_relations rows)

| Topic | Public evidence | Gap for graph |
|-------|-----------------|---------------|
| Origin / university | UNASAM news: startup **Uqhu** from CyTA/ESAT research; Young Water Fellowship bootcamp | **UNASAM** not in `actors.json` — proposed actor `pe-unasam` |
| Young Water Fellowship | [UNASAM news — bootcamp nacional](https://www.unasam.edu.pe/noticia/y0zRtTQ1BgA=) | **Young Water Solutions** not in `actors.json` — proposed international program actor |
| Gacelas Perú 2026 | [Cewas — Gacelas programme](https://www.cewas.org/articles/gacelas-programme) lists **UQHU** among nine bootcamp participants | **Cewas** not in `actors.json` — proposed actor |
| ClimaTech / Emprende UP REIN | Public Climatech 2025 page lists cohort size, not startup names including UQHU | No verified incubation edge to `pe-emprende-up-climatech-rein-hub-peru` |
| ProInnóvate water portfolio | [Innovación hídrica PRODUCE/ProInnóvate](https://www.gob.pe/institucion/proinnovate/noticias/1095741-innovacion-hidrica-produce-impulsa-tecnologias-sostenibles-para-combatir-la-escasez-de-agua) — no UQHU mention | — |
| Datasets | SUNASS + ANA `published_dataset` rows in `data_relations.json` (see `RESEARCH-PE-WATER-DATASETS.md`) | No `uses_dataset` edges for UQHU/Yakufil yet |

## YakuSmart — verified relations (added to CSV)

| from_id | to_id | type | Source |
|---------|-------|------|--------|
| `pe-proinnovate-startup-peru` | `pe-yakusmart` | `program_participation` | [Produce — riego agroexportador](https://www.gob.pe/institucion/produce/noticias/1451346-startup-financiada-por-proinnovate-optimiza-el-riego-agricola-para-incrementar-el-valor-exportable-de-las-frutas) |
| `pe-proinnovate-startup-peru` | `pe-yakusmart` | `funding` | Same Produce noticia (titular “financiada por ProInnóvate”) |
| `pe-incubaunt-la-libertad` | `pe-yakusmart` | `program_participation` | Same Produce noticia (portafolio Incubadora UNT) |
| `pe-emprende-up-climatech-rein-hub-peru` | `pe-yakusmart` | `hub_startup` | [Emprende UP — ClimateLaunchpad](https://es.linkedin.com/posts/emprende%2Eup_emprendeup-yakusmart-climatelaunchpad-activity-7511118125346656257-IIct) |
| `pe-cleantechhub` | `pe-yakusmart` | `co_organized_event` | [CleantechHUB — CLP Américas 2026](https://es.linkedin.com/posts/cleantechhub_climatelaunchpad-americas-regional-final-activity-7503144329247563776-TJpx) |

**Challenge fit:** `works_on_challenge` → `challenge:PE-2-agua` in `relations.json` (misma nota Produce: optimización de riego y recursos hídricos).

**Product context (no new graph rows):** [yakusmart.io/es](https://yakusmart.io/es) — casos de campo (Arequipa granada, ahorro hídrico).

### YakuSmart — gaps (sin URL pública suficiente para arista)

| Topic | Status |
|-------|--------|
| Fundación Bayer Scale Up (10 startups) | Mencionado en Produce; **Fundación Bayer** no está en `actors.json` |
| Monto exacto ProInnóvate / convocatoria Startup Perú | No citado en la nota Produce usada |
| `uses_dataset` SUNASS/ANA | Sin evidencia pública de uso de conjuntos del grafo |
| Amazonía Impact Ventures como funder | Solo en constelación bosques; **no** verificado para agua |
| Arista `incubated` en `relations.json` (ClimaTech → YakuSmart) | Duplicada conceptualmente; evidencia verificada vía `hub_startup` + LinkedIn Emprende UP |

## Yakufil — additional context (covered by new rows)

| Topic | Source |
|-------|--------|
| Incubation | JAKU Emprende UNSA (UNSA articles 2023 & 2024) |
| Public grant | Startup Perú 9G via ProInnóvate |
| Prize | Premio Orgullo Emprendedor 2024 — Caja Arequipa |
| Gacelas Perú | Cewas page lists **Yakufil Ecoingeniería** (no Cewas actor in graph) |
| ClimaTech REIN constellation | No public URL naming Yakufil + Emprende UP ClimaTech hub incubation |

## Proposed new actors (not added to `actors.json`)

1. **`pe-unasam`** — Universidad Nacional Santiago Antúnez de Mayolo (UQHU origin, CIAD/CyTA).
2. **`pe-cewas`** or international **`int-cewas`** — implements Gacelas Perú with Young Water Solutions.
3. **`int-young-water-solutions`** — Young Water Fellowship program operator.
4. **`pe-incubadora-empresas-unasam-spinout`** — UNASAM incubadora cited with SpinOut on public posts (needs stable gob.pe/unasam.edu.pe program page before vetted edge).
