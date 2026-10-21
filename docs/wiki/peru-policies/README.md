# Peru climate policies — wiki staging

Markdown generated for BookStack book **3042** (*Nexus agent review*) only.

## Regenerate

```bash
python3 docs/ecosystem/scripts/generate_peru_policies_wiki.py
```

## Publish (requires `BOOKSTACK_TOKEN` = `token_id:token_secret`)

```bash
export BOOKSTACK_TOKEN='…'
python3 docs/ecosystem/scripts/publish_peru_policies_bookstack.py
```

Output: `bookstack-published.json` with page ids and URLs.

## Contents

| File | Role |
|------|------|
| `00-overview.md` | Summary + links to catalog parts and key instruments |
| `catalog-part-*.md` | Full PE policy table (9 parts, ~15k rows incl. Mapa staging) |
| `pe-policies-catalog.csv` | Same catalog for spreadsheets |
| `ley-30754-lmcc.md` | Key instrument |
| `ds-013-2019-minam-reglamento-lmcc.md` | LMCC regulation |
| `ndc-peru-2020.md` | NDC |
| `encc-2050-politica-nacional.md` | National ENCC policy |
| `incentivos-startup-peru-clima.md` | StartUp Perú / incentives |

**Mapa de Actores:** Jennifer González deck (20 Oct 2026), staging under `data/ecosystem-policy/staging/peru-mapa-actores-2026/`.

Challenge links marked **Sugerido** are sector-inferred (`addresses_challenge`), not issuer-verified.
