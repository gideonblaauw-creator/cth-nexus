# Nexus → Odoo partner import (Move 2 prerequisite)

Idempotent import of ecosystem **companies** (`static/ecosystem/data/actors.raw.json`, `type=org`) and **investors** (`site/investors/data/investors.json`) into Odoo `res.partner` (`is_company=True`).

## Matching (no duplicates)

1. Normalized **website host** (non-generic social hosts ignored).
2. Else normalized **company name** (letters/digits only, lowercased).

A row is **ambiguous** when multiple Odoo partners match the same key. The script never creates a second partner when any match exists.

## Modes

| Flag | Behavior |
| --- | --- |
| *(default)* | Dry run: read Odoo, write `ops/odoo/import_plan.csv` and `ops/odoo/import_summary.json`. No Odoo writes. No Nexus writes. |
| `--apply` | Create/update Odoo partners, then write `odoo_id` back to **internal** Nexus storage only (see below). **Not for maker PRs** — requires checker + Gideon sign-off. |

## Credentials (Infisical only)

From repo root, with [Infisical CLI](https://infisical.com/docs/cli/overview) logged in or a machine identity token:

```bash
export INFISICAL_DOMAIN=https://secrets.cleantechhub.net/api
npx @infisical/cli run --project=cth-agents --env=prod -- \
  python3 ops/odoo/import_nexus_partners.py
```

Expected secret keys (same as other CTH Odoo tooling): `ODOO_URL` or `ODOO_BASE_URL`, `ODOO_DB`, `ODOO_USERNAME` or `ODOO_USER`, `ODOO_PASSWORD` (API key).

Do not commit secrets. Do not pass credentials on the command line in git history.

## Internal `odoo_id` storage (not public)

Per plan PR #102 / section 15 item 17:

- **Actors:** `actors.raw.json` → `nexus.internal.odoo_id` (stripped from `actors.json` by `build_public_data.py`).
- **Investors:** `ops/odoo/investor_odoo_ids.json` map `{ "<investor_id>": <odoo_id> }` (not served under `/investors/`).

No personal email, phone, home address, or deal notes from Odoo are written into git.

## Outputs

- `import_plan.csv` — columns: `nexus_id`, `type`, `name`, `action`, `matched_odoo_id`, `reason`
- `import_summary.json` — aggregate counts and ambiguous-match ids
