# El Salvador ecosystem · Canva deck audit

**Source of truth:** Canva design `DAGY8OMkdBw` — *MAPA DE ACTORES & ALIADOS El Salvador* (share link `https://canva.link/b0ykqucdro7hzii`; MCP `resolve-shortlink` returned not found — content read via authenticated Canva design id matching Gideon deck title).

**Live bundle:** `static/ecosystem/data/actors.json` · ids `sv-*`

## Summary (2026-10-21)

| Metric | Count |
|--------|------:|
| Live `sv-*` actors | 77 |
| Matched dedicated deck actor profiles | 72 |
| Added this pass | 0 |
| Corrected (websites / geo policy) | 8 website fixes + 77 geo rows |
| Extras in live data (not deleted; flagged in `actors.raw.json` notes) | 5 |

### Extras (no dedicated actor slide in deck)

| id | Rationale |
|----|-----------|
| `sv-uca` | Named in §3 ecosystem narrative only |
| `sv-esen` | Named in §3 ecosystem narrative only |
| `sv-usaid` | Listed in INTERNACIONAL taxonomy overview, no profile slide |
| `sv-recicla503` | Cited as example / Ternova circular partner, no profile slide |
| `sv-aes-el-salvador` | Named in sector overview list, no profile slide |

### Corrections

- Websites: `sv-recicla503`, `sv-usaid`, `sv-embajada-de-espana`, `sv-embajada-de-los-paises-bajos`, `sv-casalco`, `sv-crea-centro-de-emprendimiento-utec` (public URLs only).
- Geocoding: removed 75 generic San Salvador **city guess** pins (`actor-city` Nominatim); **16** verified **address** pins via `geocode-sv-overrides.json` + `apply_sv_geocodes.py`; **61** **country badge** (no lat/lng).

### Pin precision (public `actors.json`)

| precision | count |
|-----------|------:|
| address | 16 |
| country | 61 |

Rebuild:

```bash
python3 ops/ecosystem/apply_sv_geocodes.py   # when overrides change
python3 scripts/ecosystem/merge_geo_from_live.py
python3 scripts/ecosystem/build_public_data.py
```
