# CLP26 PE2 — draft flags (HITL)

| slug | flag | notes |
|------|------|-------|
| all | `APP_ID_TRACK_UNKNOWN` | Public wiki HTML fetch did not expose BookStack `app_id` or `track` tags; omitted from `*.tags.json` (do not invent). |
| all | `NO_LOCAL_DECK_PDF` | Brief references `/workspace/climate-kic/decks/*.pdf`; not present in this workspace. Copy derived from brief `copy_draft` JSON only. |
| pezconfiable | `TAXONOMY_WIKI_VS_DECK` | wiki=CT-AF-006, deck/proposed=CT-IC-003 |
| vigia | `NO_WIKI_PAGE` | New Idea Browser page draft |
| vigia | `STAGE_UNKNOWN` | No stage in brief JSON; left empty in tags |
| vigia | `CATEGORY_INFERRED` | Category set to **Water** from theme WW + CT-WW-001; not confirmed against an existing Idea Browser Water page |
| wayra-watt | `WEBSITE_UPDATE` | Wiki showed no website; deck has wayrawatt.com |
| windlever | `TAXONOMY_WIKI_VS_DECK` | wiki=CT-EN-006, deck/proposed=CT-IC-005 |
| windlever | `POSITIONING_SHIFT` | Deck emphasizes agro-export monitoring + soil/env data subscription; wiki text is wind micro-power only — body updated from deck excerpts |
| windlever | `CATEGORY_VS_CT1` | Existing page slug/category **Clean Energy** retained; ct1 **CT-IC-005** is ag/data — confirm BookStack category with HITL |
| yakusmart | `TAXONOMY_WIKI_VS_DECK` | wiki=CT-WW-002, deck/proposed=CT-WW-004 |
| yakusmart | `CLIMATE_IMPACT_EMPTY` | No usable climate-impact excerpt in brief `copy_draft` |

**Hard rules applied:** no BookStack/Odoo/YouTube writes; `founder` empty in tags and metadata; no founder names in body; YouTube not populated.
