# Ecosystem actors — Wiki fallback (draft)

Audit and markdown drafts for BookStack book **3042** (`nexus-agent-review`). Public wiki pages are matched via anonymous crawl of **Startup Portfolio** and **Investor Profiles** only.

## Regenerate

```bash
python3 docs/wiki/ecosystem-actors/scripts/build_audit_and_drafts.py
```

Sources:

- `static/ecosystem/data/actors.json` on `main`
- Peru enrichment from `cursor/eco-peru-update-60de` (dedupe by id / name / website)

## Publish (not run by default)

```bash
export BOOKSTACK_TOKEN=...
python3 docs/ecosystem/scripts/publish_ecosystem_actors_bookstack.py --dry-run
```
