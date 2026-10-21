# Peru open water data — verification (Chapter 4)

Verification date: **2026-10-21**. Methods: CKAN `package_show` / `resource_show` on `datosabiertos.gob.pe` (where WAF allowed), plus portal pages for SENAMHI/SNIRH/INEI.

## Included in `data_relations.json` + `story-chapters.json`

| Dataset | Publisher (actor) | URL (catalog) | Format / API | License | Update frequency |
| --- | --- | --- | --- | --- | --- |
| Número de conexiones activas de agua potable | SUNASS (`pe-sunass`) | https://www.datosabiertos.gob.pe/dataset/n%C3%BAmero-de-conexiones-activas-de-agua-potable-sunass | **CSV** direct: `Conexiones_activas_Dataset.csv` (CKAN `package_show`) | ODC-By | Monthly (provider reporting; metadata modified 2023-10-27) |
| Fajas marginales | ANA (`pe-ana-autoridad-nacional-del-agua`) | https://www.datosabiertos.gob.pe/dataset/resource/33ba82b5-68b2-4fb8-92ec-fd51771b9a63 | **CSV** direct: `Faja_Marginal_Datos_Abiertos_Act31082026.csv` (CKAN `resource_show`) | ODC-By (portal standard; package `license_title` not resolved) | Ad hoc (resource last modified 2026-08-31) |

Graph node IDs: `dataset:pe-sunass-conexiones-activas-agua-potable`, `dataset:pe-ana-fajas-marginales-csv`.

## Dropped (viewer-only, portal-only, or unverifiable here)

| Source | Reason |
| --- | --- |
| **ANA · Observatorio del Agua** (datosabiertos resource / SNIRH dashboard) | Interactive viewer; catalog shows “Data preview unavailable”; no bulk file/API in CKAN resource |
| **ANA · GeoSNIRH / SNIRH** (`geosnirh.ana.gob.pe`, `snirh.ana.gob.pe`) | WMS/ArcGIS documented on [IDEP ANA WMS catalog](https://www.idep.gob.pe/wms/wms_ana1.html) but **GetCapabilities timed out** from verification environment; treated as unverified live API |
| **SENAMHI hydromet** (CKAN `datos-hidrometeorológicos-de-libre-acceso`) | Only **HTML** resources linking to `senamhi.gob.pe` download/consulta portals; no direct open file in catalog; license not specified in CKAN |
| **INEI · ENAPRES 2024 / water access** (datosabiertos + `inei.gob.pe` microdatos) | **CSV/ZIP verified in CKAN** (`package_show` ENAPRES 2024) but **`pe-inei` not in `actors.json`** — no `published_dataset` edge per graph rules |
| **INEI · Boletín agua 2024** (PDF) | Report PDF only, not a reusable dataset node for the ecosystem graph |

## Notes

- Automated `curl` without browser-like headers often receives **HTTP 418** from `datosabiertos.gob.pe`; CKAN `package_show` / `resource_show` with standard clients worked for verification.
- **INEI** datasets remain documented here for a future `pe-inei` actor row.
