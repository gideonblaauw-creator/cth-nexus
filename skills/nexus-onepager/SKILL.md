---
name: nexus-onepager
description: >
  Build, deploy, and GitHub-sync CleantechHUB Nexus startup company profile one-pagers — bilingual
  (EN/ES) HTML at nexus.cleantechhub.net/s/{slug}. Trigger on "startup profile", "company profile",
  "one-pager", "Nexus page", "deploy /s/{slug}", "sync to GitHub", or Loom review polish. Source of
  truth: cth-nexus repo (onepagers/data + scripts/build_onepagers.py). Use when git push fails on VPS
  — fall back to Composio GITHUB_COMMIT_MULTIPLE_FILES.
---

# Nexus Startup Company Profile — Build, Deploy & Sync

Live examples: https://nexus.cleantechhub.net/s/curuba (pilot) · https://nexus.cleantechhub.net/s/coffee-kreis (legacy)

**Repo:** `gideonblaauw-creator/cth-nexus` at `/home/debian/cth-nexus`  
**Branch:** `cursor/nexus-startup-onepagers-5adf` → PR to `main`

---

## End-to-end checklist

Copy and track progress for every startup update:

```
- [ ] Edit onepagers/data/{slug}.json (or shared template/CSS/build script)
- [ ] python3 scripts/build_onepagers.py {slug}
- [ ] Visual check: frost panes, site-brand, deck embed, EN/ES toggle, LATAM photos
- [ ] Deploy live → /opt/nexus-onepagers/{slug}/
- [ ] curl -I https://nexus.cleantechhub.net/s/{slug} → 200
- [ ] GitHub sync (Composio if git push fails)
- [ ] Update PR on cursor/nexus-startup-onepagers-5adf
```

---

## Pilot roster (Aug 2026)

| Slug | JSON | Live URL |
|------|------|----------|
| curuba | `onepagers/data/curuba.json` | https://nexus.cleantechhub.net/s/curuba |
| terra-io | `onepagers/data/terra-io.json` | https://nexus.cleantechhub.net/s/terra-io |
| green-t | `onepagers/data/green-t.json` | https://nexus.cleantechhub.net/s/green-t |
| communitylab | `onepagers/data/communitylab.json` | https://nexus.cleantechhub.net/s/communitylab |
| bio-analytics | `onepagers/data/bio-analytics.json` | https://nexus.cleantechhub.net/s/bio-analytics |
| cacelio | `onepagers/data/cacelio.json` | https://nexus.cleantechhub.net/s/cacelio |

All six pilots use **local assets** (`./assets/…`), self-hosted **deck PDF**, and team photos — not Unsplash placeholders. Rebuild assets from deck PDFs with `skills/nexus-onepager/scripts/setup_startup_media.py {slug}`.

---

## Build

```bash
cd /home/debian/cth-nexus
python3 scripts/build_onepagers.py              # all six slugs
python3 scripts/build_onepagers.py curuba       # single slug
```

**Outputs:**
- `onepagers/sites/{slug}/index.html` — commit to GitHub
- `/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20/{slug}/index.html` — archive preview

**Shared files** (change once, rebuild all affected slugs):
- `onepagers/template/styles.css` — design system
- `scripts/build_onepagers.py` — HTML generator

---

## Deploy live (VPS)

Writing to `/opt/nexus-onepagers/{slug}/` goes live immediately (Caddy → `https://nexus.cleantechhub.net/s/{slug}`).

**When already on the VPS** (preferred):

```bash
SLUG=curuba
sudo mkdir -p /opt/nexus-onepagers/$SLUG
sudo cp /home/debian/cth-nexus/onepagers/sites/$SLUG/index.html \
  /opt/nexus-onepagers/$SLUG/index.html
sudo chmod 644 /opt/nexus-onepagers/$SLUG/index.html

# Curuba only — copy assets + deck
sudo cp -r /home/debian/cth-nexus/onepagers/sites/$SLUG/assets \
  /opt/nexus-onepagers/$SLUG/ 2>/dev/null || true
sudo cp /home/debian/cth-nexus/onepagers/sites/$SLUG/deck.pdf \
  /opt/nexus-onepagers/$SLUG/ 2>/dev/null || true

curl -I https://nexus.cleantechhub.net/s/$SLUG
```

**From another machine** (SSH fallback):

```bash
ssh debian@51.195.45.77 "sudo mkdir -p /opt/nexus-onepagers/{slug}"
scp onepagers/sites/{slug}/index.html debian@51.195.45.77:/tmp/{slug}-index.html
ssh debian@51.195.45.77 "sudo mv /tmp/{slug}-index.html /opt/nexus-onepagers/{slug}/index.html && sudo chmod 644 /opt/nexus-onepagers/{slug}/index.html"
```

---

## GitHub sync

Direct `git push` often fails on the VPS (`Permission denied (publickey)`). **Use Composio instead.**

### Prepare payload

```bash
cd /home/debian/cth-nexus
python3 skills/nexus-onepager/scripts/prepare_github_payload.py \
  --slug curuba \
  --message "Polish Curuba one-pager per Loom review" \
  > /tmp/gh-commit-curuba.json
```

For shared-only changes, pass explicit paths:

```bash
python3 skills/nexus-onepager/scripts/prepare_github_payload.py \
  --paths onepagers/template/styles.css scripts/build_onepagers.py \
  --message "Restore build script and update frost CSS" \
  > /tmp/gh-commit-shared.json
```

### Commit via Composio

Use `COMPOSIO_MULTI_EXECUTE_TOOL` with `tool_slug: GITHUB_COMMIT_MULTIPLE_FILES`. **Do not** call `GITHUB_COMMIT_MULTIPLE_FILES` as a direct MCP tool name — it only works through Composio.

```json
{
  "owner": "gideonblaauw-creator",
  "repo": "cth-nexus",
  "branch": "cursor/nexus-startup-onepagers-5adf",
  "message": "<commit message>",
  "upserts": [
    {"path": "onepagers/data/curuba.json", "content": "...", "encoding": "utf-8"},
    {"path": "onepagers/sites/curuba/index.html", "content": "...", "encoding": "utf-8"}
  ]
}
```

**Per-slug commit pattern:** upsert `onepagers/data/{slug}.json` + `onepagers/sites/{slug}/index.html` together.

**Shared changes:** commit `styles.css` and/or `build_onepagers.py` separately, then rebuild all slugs and commit each HTML.

**If Composio fails:** retry once; if still failing, use `COMPOSIO_REMOTE_WORKBENCH` with `run_composio_tool("GITHUB_COMMIT_MULTIPLE_FILES", args)`.

**Never commit placeholder content** — a bad Composio commit once wiped `build_onepagers.py` with `PLACEHOLDER`. Always verify file contents before upserting.

---

## Mandatory design rules

### i) Frost panes on text boxes

All content boxes use **frosted glass**, not flat dark fills. Shared CSS: `onepagers/template/styles.css` — class `.frost-panel` and siblings use `var(--panel)` + blur. **Do not revert** stat cards to `rgba(0,0,0,.3)`.

### ii) CleantechHUB site brand (Loom polish)

Fixed top bar, clear of EN/ES toggle:

```css
.site-brand { position: fixed; top: 12px; left: 50%; transform: translateX(-50%); ... }
```

Builder injects: `<div class="site-brand"><span class="brand-text">Cleantech<em>HUB</em></span></div>`

### iii) Problem section — split frost stats (Loom polish)

Problem column uses `.split-frost-stats`: frost panel fills the column; inner stat cards are **transparent** (no nested frost boxes).

### iv) Pitch deck PDF embedded in HTML

Every profile should include the startup pitch deck.

1. Upload PDF to Google Drive folder **Nexus startup decks 2026-08-20** (or copy to `/opt/nexus-onepagers/{slug}/deck.pdf` for self-hosted)
2. Add to JSON:

```json
"deck_pdf": {
  "drive_id": "<file-id>",
  "view_url": "https://drive.google.com/file/d/<id>/view",
  "embed_url": "https://drive.google.com/file/d/<id>/preview",
  "source_file": "StartupName Deck.pdf"
}
```

3. Builder renders **Pitch Deck** section after KPI ribbon:
   - **Prefer self-hosted** `/s/{slug}/deck.pdf` via `<embed>` when file exists on VPS
   - Fallback: Google Drive `/preview` iframe
   - **Deck frame height: 2560px** (2× original) — `.deck-frame { height: 2560px; min-height: 720px; }`
   - CTA footer link: "Pitch deck (PDF)"

Numbers on the page must match the deck only; gaps = `[PENDIENTE]`.

### v) Latin American imagery only

Background photos must fit **Latin American agrifood / cleantech context**.

**Use:** coffee/cacao/banana/plantain harvest, Andean or tropical smallholder farms, LATAM cooperatives, regional ports/cities, local biodiversity.

**Never use:** European temperate forests, US Midwest corn/wheat monoculture, generic North American farm stock.

Verify each Unsplash pick before shipping. Document choices in JSON `bg` fields.

### vi) Builder defaults (Loom polish)

- Sliders: use `"default"` key in JSON; disable input when `min == max`
- Bar charts: pixel heights via `height` field, not `%`

---

## Brand (page canvas)

- Page background: `--page: #fff` (light canvas) — **not** near-black `#051e38`
- Section title blocks: deep blue / forest green overlays on photos
- Colors: `--db #0C498A`, `--cy #B2EEFA`, `--lg #9DC384`, `--fo #669348`, `--sk #69B5FA`

---

## Verification checklist

1. `.site-brand` visible top-center, not overlapping lang toggle
2. Frost panes on cards/panels (blur + light border)
3. Pitch deck embed loads (self-hosted PDF or Drive preview); frame is tall (~2560px)
4. Problem section: single frost panel, transparent inner stat cards
5. All section photos pass LATAM context review
6. EN/ES toggle works
7. Bar charts use pixel heights, not `%`
8. `curl -I https://nexus.cleantechhub.net/s/{slug}` → 200 after deploy
9. GitHub branch has matching JSON + HTML (and shared files if changed)

---

## Reference files

| File | Role |
|------|------|
| `onepagers/template/styles.css` | Design system |
| `onepagers/data/curuba.json` | Pilot JSON (deck + LATAM images + local assets) |
| `scripts/build_onepagers.py` | Generator |
| `skills/nexus-onepager/scripts/setup_startup_media.py` | Extract deck backgrounds + team photos into `onepagers/media/{slug}/` |
| `skills/nexus-onepager/scripts/prepare_github_payload.py` | Composio commit payload helper (text files) |
| `skills/nexus-onepager/scripts/prepare_slug_commit.py` | Composio payload with base64 media batches |
| `/opt/nexus-onepagers/coffee-kreis/index.html` | Legacy live template |
