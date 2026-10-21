# Ecosystem map data (public bundle)

Extracted from Canva actor maps. **`actors.raw.json`** is the ingest snapshot (staff-only fields); **`actors.json`** is the sanitized deploy artifact (no `notes`, emails, phones, Drive links, or website check metadata).

## Files

- `actors.raw.json` — source snapshot for `scripts/ecosystem/build_public_data.py`
- `actor_cards.json` — wiki-enriched card fields (source for merge into `actors.raw.json`)
- `actors.json` — sanitized actors with optional `card` block (role, description, founding year) and `geo`
- `relations.json` — 93 typed edges (79 public with `verified` + `source_url`; see `ops/ecosystem/UNVERIFIED-RELATIONS.md`)
- `designs.json` — source design metadata

## Build

```bash
python3 ops/ecosystem/apply_sv_geocodes.py   # optional refresh (overrides / policy)
python3 scripts/ecosystem/merge_geo_from_live.py
python3 scripts/build_ecosystem_actor_cards.py
python3 scripts/ecosystem/build_public_data.py
```

`merge_geo_from_live` (also invoked by the card + public build scripts) applies SV geo policy and ignores live cache city guesses for `sv-*` actors.

`nexus.card_slug` is set only for startups with an existing `/s/` one-pager (not ecosystem org cards).

## Coverage

| Country | Actors in bundle |
|---------|-------------------|
| Peru | 201 |
| El Salvador | 77 (72 deck profiles + 5 flagged extras; see `ops/ecosystem/SV_DECK_AUDIT.md`) |
| Colombia | 8 |
| Guatemala | 0 (UI empty state) |
| Costa Rica | 0 (UI empty state) |

## Known gaps

- Guatemala and Costa Rica: no Canva actor mapping yet.
- Colombia: institutions-only deck (8 actors).
- No `person` actors in source maps → LinkedIn row shows PENDIENTE for org-only data.
- Nexus `/s/` slugs: only a handful match one-pagers today (see build script counts).
