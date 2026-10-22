---
startup: YakuSmart
slug: yakusmart
country: Peru
consent: true
date: 2026-10-22
consent_note: per Gideon
move: 3B
plan: docs/plans/2026-10-22-datalab-nexus-moat-plan.md
---

# YakuSmart — short case

CleantechHUB short case for Move 3B (CLP startup with a public funder match). No Colombia startup–funder relation exists on `main` yet; this case uses the verified ProInnóvate → YakuSmart relation from PR #101.

## Claim

YakuSmart is a Peru ClimateLaunchpad (**CLP26**) agritech startup whose irrigation platform is publicly described as supported by ProInnóvate (Programa Nacional de Innovación y Desarrollo Productivo).

## Evidence

### Programme (CTH-run)

| Field | Value |
| --- | --- |
| `evidence_type` | `cth_cohort` |
| `programme` | `cth-climate-launchpad` |
| `source_url` | https://nexus.cleantechhub.net/s/yakusmart |
| `date_accessed` | 2026-10-22 |
| `quote` | CLP26 Peru cohort |

### Funder match (public graph)

| Field | Value |
| --- | --- |
| `evidence_type` | `public_quote` |
| `relation` | `pe-proinnovate-startup-peru` → `pe-yakusmart` (`funding`) |
| `source_url` | https://www.gob.pe/institucion/proinnovate/noticias/1451423-startup-impulsada-por-proinnovate-optimiza-el-riego-agricola-para-incrementar-el-valor-exportable-de-las-frutas |
| `source_title` | ProInnóvate — YakuSmart optimiza el riego |
| `date_accessed` | 2026-10-22 |
| `quote` | Con el impulso del programa ProInnóvate del Ministerio de la Producción (PRODUCE), la startup YakuSmart desarrolló y mejoró una plataforma tecnológica que ayuda a las agroexportadoras a optimizar el riego de sus cultivos y aprovechar de manera más eficiente los recursos hídricos y energéticos. |

This relation is `verified: true` on `main` in `static/ecosystem/data/relations.json` and matches `ops/ecosystem/graph_relation_evidence.json`.

Programme id `cth-climate-launchpad` is listed in `ops/ecosystem/cth_run_programmes.json`.

## Out of scope for this file

No personal contact details, Drive links, or Canva links. Field results and savings figures in the same Gob.pe article are omitted here (pilot-style outcomes); only the funder-support claim above is published in this case.
