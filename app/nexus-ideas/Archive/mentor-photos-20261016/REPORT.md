# Mentor directory photos — 2026-10-16

## Source

| Item | Path |
|------|------|
| Live HTML | `/opt/cth-nexus/static/mentor-directory/index.html` (served at `/mentor-directory` via Caddy) |
| Master spreadsheet | `/opt/cth-nexus/data/CTH_Master_Mentors.xlsx` (no `Photo URL` values for published mentors) |
| Backup | `/opt/nexus-idea-browser/Archive/mentor-photos-20261016/originals/` |

## Changes

- Added `photo` (local `/nexus-assets/mentors/<slug>.jpg`) and `desc` (1–2 sentences, Spanish) to each entry in `MENTORS`.
- Added `.card-desc` block in the mentor card renderer.
- JPEG assets under `/var/www/nexus-assets/mentors/` (400×400 center crop).

## Photo sourcing

1. **First pass:** `unavatar.io/linkedin/{slug}` where available (re-hosted locally; not hotlinked).
2. **First-pass fallbacks:** Torre, IDB Invest, KIMSA Wix, PR PARA TODOS, Sched (Diego Prada).
3. **Second pass (2026-10-16):** No unavatar/LinkedIn. Org pages, news, conferences only when name + employer/role matched. Script: `apply_manual_portraits.py`.

### Second-pass portraits added (9)

| Mentor | Source page | Image URL |
|--------|-------------|-----------|
| Juliana Rincón Jaramillo | [Valora Analitik](https://www.valoraanalitik.com/dia-del-reciclaje-el-reciclaje-sera-la-industria-del-futuro/) | `Reciclave-Latam.webp` (caption: Directora Ejecutiva Recicla Latam) |
| Jesus Alberto Cruz Diaz | [El Heraldo](https://www.elheraldo.co/mas-negocios/2019/11/20/organicos-del-caribe-innovara-generando-energia-con-residuos-681850/) | resizer `UFUWHTZHF5D2BEAOXEXU77GIYY.jpg` |
| Iván Dávila Velandia | [Future Lab](https://futurelab.com.co/nuestro-adn/) | `IVAN-DAVILA-FUTURE-LAB-INNOVACION-1-360x360.jpg` |
| Jacopo Deida | [Ambrosetti speaker](https://eventi.ambrosetti.eu/scenarioprofessioni2024/speaker/jacopo-deidda-gagliardo/) | `DEIDDA-GAGLIARDO-Jacopo-TS-2024-1009x1024.jpg` |
| Julián Aponte | [Dementes Brillantes](https://dementesbrillantes.com.co/impulsatuequipo/) | `julian.webp` |
| Alejandro Gaviria | [CNW / RegenEAU](https://www.newswire.ca/news-releases/regeneau-receives-support-from-fondaction-cycle-h2o-c3e-groupe-mcf-and-desjardins-to-advance-wastewater-heat-recovery-in-support-of-building-energy-efficiency-862285457.html) | PR Newswire team photo (crop: left, COO Alejandro Gaviria) |
| Mitchell Jesús Lázaro Díaz | [Microfinanzas.pe](https://microfinanzas.pe/mitchell-lazaro-diaz-el-peru-puede-construir-su-propio-nu-bank-pero-no-lo-hara-por-imitacion-sino-por-reinvencion/) | `43.png` |
| Rayniero Aristizabal Nova | [UP Pacifico plana docente](https://pbs.edu.pe/plana-docente/) | `/images/c0b17997f45a44b1b0ec48b4cc736207.png` |
| Miguel Ñañez Aiscorbe | [Puente Capital trayectoria](https://puentecapitalperu.com/trayectoria/) | `Group-1000001830-e1783473638982.png` (og:image; ex–gerente territorial BBVA) |

## Counts (after second pass)

| Metric | Value |
|--------|------:|
| Total mentors | 36 |
| Photos **FOUND** | **29** |
| **PENDIENTE** | **7** |
| Descriptions | 36 |

**Still PENDIENTE:** Fernando Flores, Luis Osorio, Julián Forero, Luis Betancourt, Carlos Casallas, Renzo Salas, Duilio Aranda Ipince — no confident public portrait found (Circulatam/ eco2biz / Soluenergias team pages lack headshots; name collisions for “Julián Forero”; Fondo Acción / BSF / AID without verified photos).

## Blockers (first pass)

After ~36 unavatar requests, `unavatar.io` returned **HTTP 429** from this VPS. LinkedIn guest pages return **HTTP 999**.

## Artifacts

- `mentors.csv` — full row per mentor
- `descriptions.json` — bio text keyed by mentor id
- `manifest.json` — run summary counts
