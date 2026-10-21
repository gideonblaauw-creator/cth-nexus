# Ecosystem geocoding

**Deploy rule:** do not copy to `/opt/cth-nexus/static/…` until changes are merged on GitHub and promoted deliberately. Use `apply_live.sh` only after that.

- `geocode_actors.py` — primary geocoder
- `geocode-review.csv` — human review export
- `apply_live.sh` — copies `static/ecosystem/data/actors.json` and `nexus-assets/nexus-latam-map.js` to live paths (with backup)
