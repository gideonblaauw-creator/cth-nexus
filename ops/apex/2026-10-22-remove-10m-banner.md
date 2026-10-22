# Remove the apex “+10 Millons Capital Raised” banner

Date: 2026-10-22

Site: https://cleantechhub.net/ (WordPress, not hosted on this VPS). The edit uses the WordPress REST API with `cth-agents` / `prod` keys `WP_BASE_URL`, `WP_USER`, and `WP_APP_PASSWORD`.

## What changed

The static front page is page **347** (`home-2`, last modified 2026-05-21T17:52:41). Its Elementor row `8616bbd` holds six 33.33% columns. This change removes only the last column, `9f4fdc7`, and the icon-box inside it, widget **2094605**, whose `title_text` is `+10 Millons Capital Raised`.

These five columns stay:

| Column | Widget | Title |
| --- | --- | --- |
| `0afeaa0` | `79ced18` | + 8 países |
| `6f2a8ae` | `b2ba7da` | +5 Megatons to CO2 save |
| `cc21d14` | `4e9e0b3` | +40 Ecosystem partners |
| `6682009` | `b9671e8` | +1000 Climate solutions supported |
| `9bd3563` | `22b8fd3` | +50 Millions Capital Leveraged |

After this note is on `main`, the live edit writes the updated `_elementor_data` to page 347, then calls `DELETE /wp-json/elementor/v1/cache` and `POST /wp-json/elementor/v1/design-system-sync/stylesheet`.

## Backup

`/var/backups/cth-apex-20261022T145427Z/`

- `page-347-elementor-data.json` — homepage `_elementor_data` before the edit (`sha256 fd277b63b8b4918722cb92efe393ef35cfebcb0352d2f53f00d2821dcdf927cf`)
- `revision-1860.json` — post revision 1860 (parent 347). Its Elementor data matches the page meta.
- `manifest.json`
- `rollback.sh`

## Rollback

```bash
sudo bash /var/backups/cth-apex-20261022T145427Z/rollback.sh
```

The script reads the WordPress credentials from Infisical at runtime, writes the saved `_elementor_data` back to page 347, and clears the Elementor cache. It does not contain secret values.
