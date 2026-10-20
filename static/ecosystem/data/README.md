# Ecosystem map data (public bundle)

Extracted from Canva actor maps. **`actors.raw.json`** is the ingest snapshot (staff-only fields); **`actors.json`** is the sanitized deploy artifact (no `notes`, emails, phones, Drive links, or website check metadata).

## Files

- `actors.raw.json` — source snapshot for `scripts/ecosystem/build_public_data.py`
- `actors.json` — 286 actors with `geo` (country centroid + jitter; city geocode ready)
- `relations.json` — 75 typed edges
- `designs.json` — source design metadata

## Build

```bash
python3 scripts/ecosystem/build_public_data.py
```

Adds `nexus.card_slug` from one-pager website/name matches.

## Coverage

| Country | Actors in bundle |
|---------|-------------------|
| Peru | 201 |
| El Salvador | 77 |
| Colombia | 8 |
| Guatemala | 0 (UI empty state) |
| Costa Rica | 0 (UI empty state) |

## Known gaps

- Guatemala and Costa Rica: no Canva actor mapping yet.
- Colombia: institutions-only deck (8 actors).
- No `person` actors in source maps → LinkedIn row shows PENDIENTE for org-only data.
- Nexus `/s/` slugs: only a handful match one-pagers today (see build script counts).
