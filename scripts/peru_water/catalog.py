"""Source metadata (open-data only)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpec:
    id: str
    name: str
    publisher: str
    url: str
    license: str
    format: str
    update_frequency: str


# Pulled programmatically by ingesters
ACTIVE: list[SourceSpec] = [
    SourceSpec(
        id="ana_snirh_stations_idep",
        name="ANA hidrometeorological station registry (SNIRH mirror via IDEP)",
        publisher="ANA / IGN-Peru IDEP",
        url="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/MapServer/4",
        license="Open government spatial data (verify per layer metadata)",
        format="ArcGIS MapServer JSON",
        update_frequency="Ad hoc (no published SLA)",
    ),
    SourceSpec(
        id="ana_fajas_marginales_datosabiertos",
        name="Fajas marginales (ANA)",
        publisher="ANA via datosabiertos.gob.pe",
        url="https://www.datosabiertos.gob.pe/dataset/fm",
        license="Open Data Commons Attribution (ODC-By)",
        format="CSV",
        update_frequency="Irregular (resource metadata)",
    ),
    SourceSpec(
        id="sunass_conexiones_activas",
        name="Conexiones activas de agua potable",
        publisher="SUNASS",
        url="https://www.datosabiertos.gob.pe/dataset/número-de-conexiones-activas-de-agua-potable-sunass",
        license="Open Data Commons Attribution (ODC-By)",
        format="CSV",
        update_frequency="Monthly",
    ),
    SourceSpec(
        id="sunass_estructuras_tarifarias",
        name="Estructuras tarifarias de saneamiento",
        publisher="SUNASS",
        url="https://www.datosabiertos.gob.pe/dataset/estructuras-tarifarias-de-los-servicios-de-saneamiento-regulados-por-la-sunass-3",
        license="Open Data Commons Attribution (ODC-By)",
        format="CSV (semicolon)",
        update_frequency="Monthly",
    ),
    SourceSpec(
        id="sunass_distritos_emergencia_hidrica",
        name="Distritos en emergencia por riesgo hídrico",
        publisher="SUNASS",
        url="https://www.datosabiertos.gob.pe/dataset/distritos-declarados-en-estado-de-emergencia-por-riesgos-asociados-recursos-hídricos-sunass",
        license="Open Data Commons Attribution (ODC-By)",
        format="CSV",
        update_frequency="As decrees are issued",
    ),
    SourceSpec(
        id="senamhi_estaciones_automaticas",
        name="Variables meteorológicas — estaciones automáticas de intercambio internacional",
        publisher="SENAMHI via datosabiertos.gob.pe",
        url="https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-automáticas-de-intercambio-internacional-servicio",
        license="Open Data Commons Attribution (ODC-By)",
        format="CSV",
        update_frequency="Daily (FECHA_CORTE in file)",
    ),
    SourceSpec(
        id="inei_enapres_2024_access",
        name="ENAPRES 2024 — agua/saneamiento (hogar, CAP 300)",
        publisher="INEI",
        url="https://www.inei.gob.pe/media/DATOS_ABIERTOS/ENAPRES/DATA/2024.zip",
        license="INEI open microdata terms (public use, attribution)",
        format="ZIP/CSV microdata",
        update_frequency="Annual",
    ),
]

# Not ingested — documented in README / sources.status=skipped
SKIPPED: list[tuple[SourceSpec, str]] = [
    (
        SourceSpec(
            id="snirh_observatorio_dashboard",
            name="SNIRH Observatorio del Agua (interactive export)",
            publisher="ANA",
            url="https://snirh.ana.gob.pe/observatoriosnirh/",
            license="N/A (viewer)",
            format="Web dashboard",
            update_frequency="Unknown",
        ),
        "Viewer-only export; snirh.ana.gob.pe times out from this VPS egress.",
    ),
    (
        SourceSpec(
            id="geosnirh_arcgis",
            name="GeoSNIRH ArcGIS REST services",
            publisher="ANA",
            url="https://geosnirh.ana.gob.pe/server/rest/services",
            license="Unknown",
            format="ArcGIS REST",
            update_frequency="Unknown",
        ),
        "Host unreachable (timeout) from VPS; using IDEP MapServer mirror for station geometry.",
    ),
    (
        SourceSpec(
            id="senamhi_portal_descargas",
            name="SENAMHI hidrometeorological download portal",
            publisher="SENAMHI",
            url="https://www.senamhi.gob.pe/?&p=descarga-datos-hidrometeorologicos",
            license="N/A",
            format="HTML portal",
            update_frequency="Unknown",
        ),
        "No direct bulk API; senamhi.gob.pe unstable from VPS. Using datosabiertos CSV subset.",
    ),
    (
        SourceSpec(
            id="sunass_observatorio_mvcs",
            name="MVCS / SUNASS statistical repository UI",
            publisher="SUNASS / MVCS",
            url="https://ww3.vivienda.gob.pe/repositorioestadistico/IndicadoresSUNASS.aspx",
            license="N/A",
            format="Web UI",
            update_frequency="Unknown",
        ),
        "WAF 418 from VPS; SUNASS indicators pulled via datosabiertos.gob.pe instead.",
    ),
]
