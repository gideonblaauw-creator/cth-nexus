# Nexus ecosystem — Peru enrichment (Oct 2026)

## GitHub-first (hard rule)

**Do not run `apply_peru_merge.sh` or copy to `/opt/cth-nexus/static` until this branch is pushed to GitHub and merged/deployed via the normal pipeline.**

Push is blocked on this VPS until the GitHub deploy key is fixed (Infra).

## Branch contents

| Branch | SHA (local) | Contents |
|--------|-------------|----------|
| `cursor/eco-peru-update-60de` | `52ca185887e9936dbde08c8fbc83fe7a95b480d2` | Actor/ relation enrichment + UI (`actors.json` 381, `relations.json` 95) |
| `research/ecosystem-policy` | `d5e547bdc5a6b56b00af048441612bdbbec28e10` | Policy staging only (`data/ecosystem-policy/staging/peru-mapa-actores-2026/`) — **not** live |

Regenerate actors: `scripts/ecosystem/merge_peru_mapa_2026.py`  
Regenerate policy staging: `scripts/ecosystem/extract_peru_policy_staging.py`

## Live status (2026-10-20)

**Already applied live once** (before GitHub-first rule): production served **381** actors / **8** policy-type nodes from disk under `/opt/cth-nexus/static/ecosystem/`.

To revert production to pre-enrichment bundle (**286** actors) until GitHub is ready:

```bash
sudo /var/backups/nexus-eco-peru-20261020-230014/rollback.sh
```

Backups (newest last): `/var/backups/nexus-eco-peru-20261020-225109`, `…-225550`, `…-230014` (rollback target = state **before** final apply).
