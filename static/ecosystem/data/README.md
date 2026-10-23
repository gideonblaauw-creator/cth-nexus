# Ecosystem map data (public bundle)

Extracted from Canva actor maps. **`actors.raw.json`** is the ingest snapshot (staff-only fields); **`actors.json`** is the sanitized deploy artifact (no `notes`, emails, phones, Drive links, or website check metadata).

## Files

- `actors.raw.json` — source snapshot for `scripts/ecosystem/build_public_data.py`
- `actor_cards.json` — wiki-enriched card fields (source for merge into `actors.raw.json`)
- `actors.json` — sanitized actors with optional `card` block (role, description, founding year) and `geo`
- `relations.json` — typed edges; **public** only when listed in `ops/ecosystem/graph_relation_evidence.json`. `evidence_type` defaults to `public_quote` (verbatim quote on `source_url`, checked by `scripts/ecosystem/verify_relation_quotes.py`). `cth_cohort` skips that live fetch only for a programme in `ops/ecosystem/cth_run_programmes.json`, with no personal email, phone, or home address, and with `consent_ref` when the row records money or a pilot outcome (Gideon decision 25, 22 Oct 2026). Self-loops are omitted. See `ops/ecosystem/UNVERIFIED-RELATIONS.md`.
- `designs.json` — source design metadata

## Build

```bash
python3 ops/ecosystem/apply_sv_geocodes.py   # optional refresh (overrides / policy)
python3 scripts/ecosystem/merge_geo_from_live.py
python3 scripts/build_ecosystem_actor_cards.py
python3 scripts/ecosystem/build_public_data.py
python3 scripts/ecosystem/build_graph_relation_evidence.py
python3 scripts/ecosystem/sync_graph_relation_sources.py
python3 scripts/ecosystem/verify_relation_quotes.py
```

`merge_geo_from_live` (also invoked by the card + public build scripts) applies SV geo policy and ignores live cache city guesses for `sv-*` actors.

`nexus.card_slug` is set only for startups with an existing `/s/` one-pager (not ecosystem org cards).

## Coverage

| Country | Actors in bundle |
|---------|-------------------|
| Peru | 201 |
| El Salvador | 77 (72 deck profiles + 5 flagged extras; see `ops/ecosystem/SV_DECK_AUDIT.md`) |
| Colombia | 105 (actor list v1; 11 Peru-aligned categories, no startups) |
| Guatemala | 0 (UI empty state) |
| Costa Rica | 0 (UI empty state) |

## Known gaps

- Guatemala and Costa Rica: no Canva actor mapping yet.
- Colombia: institutions-only deck (8 actors).
- No `person` actors in source maps → LinkedIn row shows PENDIENTE for org-only data.
- Nexus `/s/` slugs: only a handful match one-pagers today (see build script counts).
