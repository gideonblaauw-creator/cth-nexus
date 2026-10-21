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
| Datasets | No public dataset publication/use links tied to UQHU in repo sources | `data_relations.json` still empty |

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
