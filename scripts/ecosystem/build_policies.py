#!/usr/bin/env python3
"""Generate data/policies.json and data/policy_relations.json for Nexus ecosystem staging."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_POLICIES = ROOT / "data" / "policies.json"
OUT_RELATIONS = ROOT / "data" / "policy_relations.json"
OUT_PROTOTYPE_SHARED = ROOT / "docs" / "ecosystem" / "prototypes" / "shared"

# Country anchor coords (capital) — policy nodes jitter slightly by index
GEO = {
    "Peru": {"lat": -12.05, "lng": -77.04},
    "Colombia": {"lat": 4.71, "lng": -74.07},
    "El Salvador": {"lat": 13.69, "lng": -89.19},
    "Guatemala": {"lat": 14.63, "lng": -90.51},
    "Costa Rica": {"lat": 9.93, "lng": -84.09},
}


def jitter(country: str, i: int) -> dict:
    g = GEO[country]
    return {"lat": g["lat"] + (i % 5) * 0.08 - 0.16, "lng": g["lng"] + (i // 5) * 0.12 - 0.24}


def pol(
    pid: str,
    name: str,
    country: str,
    instrument_type: str,
    year: int,
    sectors: list[str],
    status: str,
    source_url: str,
    i: int,
) -> dict:
    return {
        "id": pid,
        "type": "Policy",
        "name": name,
        "country": country,
        "instrument_type": instrument_type,
        "year": year,
        "sectors": sectors,
        "status": status,
        "source_url": source_url,
        "geo": jitter(country, i),
    }


def rel(source: str, target: str, rtype: str, source_url: str, *, suggested: bool = False, notes: str = "") -> dict:
    out = {
        "source": source,
        "target": target,
        "type": rtype,
        "source_url": source_url,
        "notes": notes,
    }
    if suggested:
        out["suggested"] = True
    else:
        out["verified"] = True
    return out


# fmt: off
POLICY_DEFS = [
    # --- Peru ---
    pol("policy:pe-ley-30754-cc", "Ley N.° 30754 — Ley Marco sobre Cambio Climático", "Peru", "law", 2018,
        ["cross-cutting", "energy", "bosques", "agua"], "in_force",
        "https://climate-laws.org/document/framework-law-no-30754-on-climate-change_688f", 0),
    pol("policy:pe-ds-012-2024-encc", "DS N.° 012-2024-MINAM — Estrategia Nacional ante el CC al 2050", "Peru", "strategy", 2024,
        ["cross-cutting", "energy", "agriculture", "bosques"], "in_force",
        "https://climate-laws.org/document/supreme-decree-no-012-2024-minam-approves-the-national-policy-national-strategy-for-climate-change-to-2050-decreto-supremo-ndeg-012-2024-minam-aprueba-la-politica-nacional-estrategia-nacional-ante-el-cambio-climatico-al-2050_58d6", 1),
    pol("policy:pe-ley-29763-forestal", "Ley N.° 29763 — Ley Forestal y de Fauna Silvestre", "Peru", "law", 2011,
        ["bosques"], "in_force",
        "https://climate-laws.org/document/forestry-and-wildlife-law-no-29763_3a3f", 2),
    pol("policy:pe-ley-29338-agua", "Ley N.° 29338 — Ley de Recursos Hídricos", "Peru", "law", 2009,
        ["agua"], "in_force",
        "https://climate-laws.org/document/water-resources-law-no-29338_0a6a", 3),
    pol("policy:pe-ley-28832-rer", "Ley N.° 28832 — Promoción de inversiones para generación eléctrica con RER", "Peru", "law", 2006,
        ["energy"], "in_force",
        "https://climate-laws.org/document/law-no-28832-to-promote-investment-in-electricity-generation-using-renewable-energy_5f8e", 4),
    pol("policy:pe-ndc-2020", "NDC del Perú — actualización 2020 (2030)", "Peru", "NDC", 2020,
        ["cross-cutting", "energy", "bosques", "agua"], "in_force",
        "https://cdn.www.gob.pe/uploads/document/file/1675213/Actualizaci%C3%B3n%20de%20las%20NDC%20del%20Per%C3%BA%20al%202030.pdf?v=1663622045", 5),
    pol("policy:pe-ds-013-2019-reglamento-cc", "DS N.° 013-2019-MINAM — Reglamento Ley 30754", "Peru", "regulation", 2019,
        ["cross-cutting"], "in_force",
        "https://climate-laws.org/document/supreme-decree-no-013-2019-minam-approving-the-regulation-of-law-no-30754-framework-law-on-climate-change_0d0a", 6),
    pol("policy:pe-marco-bonos-verdes", "Marco para Bonos Verdes del Perú (MINAM)", "Peru", "strategy", 2019,
        ["finance", "bosques", "energy"], "in_force",
        "https://climate-laws.org/document/green-bonds-framework-for-peru_3b0b", 7),
    pol("policy:pe-proinnovate-clima", "StartUp Perú — línea Incubadoras en Cambio Climático", "Peru", "incentive", 2022,
        ["cross-cutting", "energy", "agua", "bosques"], "in_force",
        "https://www.produce.gob.pe/proinnovate", 8),
    pol("policy:pe-programa-bosques-norma", "Programa Bosques — financiamiento REDD+ (MINAM)", "Peru", "incentive", 2016,
        ["bosques"], "in_force",
        "https://www.gob.pe/institucion/minam/campañas/123-programa-bosques", 9),
    pol("policy:pe-ley-28611-ambiental", "Ley N.° 28611 — Ley General del Ambiente", "Peru", "law", 2005,
        ["cross-cutting", "agua", "bosques"], "in_force",
        "https://climate-laws.org/document/general-law-for-the-environment-law-no-28611_5a5b", 10),
    pol("policy:pe-plan-mitigacion-2023", "Plan Nacional de Mitigación de Gases de Efecto Invernadero", "Peru", "strategy", 2023,
        ["energy", "transport", "agriculture"], "in_force",
        "https://climate-laws.org/document/national-plan-for-the-mitigation-of-greenhouse-gases_6c6a", 11),

    # --- Colombia ---
    pol("policy:co-taxonomia-verde", "Taxonomía Verde de Colombia (Circular Externa 005/2022)", "Colombia", "taxonomy", 2022,
        ["finance", "energy", "bosques", "agua"], "in_force",
        "https://www.taxonomiaverde.gov.co/documents/d/taxonomia-verde/circular_externa_005_de_2022", 0),
    pol("policy:co-ley-2099-transicion", "Ley 2099/2021 — Transición energética y reactivación", "Colombia", "law", 2021,
        ["energy"], "in_force",
        "https://climatepolicydatabase.org/policies/law-2099-energy-transition-and-economic-reactivation", 1),
    pol("policy:co-ley-1715-rer", "Ley 1715/2014 — FNCER (renovables no convencionales)", "Colombia", "law", 2014,
        ["energy"], "in_force",
        "https://climate-laws.org/document/law-1715-2014-regulating-the-integration-and-promotion-of-non-conventional-renewable-energy-fncer_6bed", 2),
    pol("policy:co-ley-1931-adaptacion", "Ley 1931/2018 — Gestión del riesgo de desastres y CC", "Colombia", "law", 2018,
        ["cross-cutting", "agua"], "in_force",
        "https://climate-laws.org/document/law-1931-of-2018-by-which-the-management-of-disaster-risk-is-regulated-and-the-national-system-for-disaster-risk-management-is-restructured_8a8a", 3),
    pol("policy:co-ndc-2020", "NDC de Colombia — actualización 2020", "Colombia", "NDC", 2020,
        ["cross-cutting", "energy", "bosques"], "in_force",
        "https://unfccc.int/sites/default/files/NDC/2022-06/Colombia%20Updated%20NDC%202020.pdf", 4),
    pol("policy:co-plan-nacional-adaptacion", "Plan Nacional de Adaptación al Cambio Climático (PNACC)", "Colombia", "strategy", 2017,
        ["agua", "agriculture", "cross-cutting"], "in_force",
        "https://climate-laws.org/document/national-climate-change-adaptation-plan_5f5f", 5),
    pol("policy:co-ley-2169-carbono", "Ley 2169/2021 — Gestión del cambio climático", "Colombia", "law", 2021,
        ["cross-cutting", "energy"], "in_force",
        "https://climate-laws.org/document/law-2169-of-2021-on-climate-change-management_0f0f", 6),
    pol("policy:co-fenoge", "FENOGE — Fondo de Energías No Convencionales y GEE", "Colombia", "incentive", 2014,
        ["energy"], "in_force",
        "https://www.minenergia.gov.co/es/minienergia/institucional/entidades-adscritas/fenoge/", 7),
    pol("policy:co-ipse-rural", "Plan IPSE — acceso energético ZNI (Decreto 2234/2023)", "Colombia", "strategy", 2023,
        ["energy"], "in_force",
        "https://www.minenergia.gov.co/es/minienergia/institucional/plan-ipse/", 8),
    pol("policy:co-contribucion-carbono", "Contribución nacionalmente determinada — carbono neutralidad 2050", "Colombia", "strategy", 2021,
        ["cross-cutting"], "in_force",
        "https://www.minambiente.gov.co/asuntos-ambientales-y-sectorial/cambio-climatico-y-gestion-del-riesgo/politicas-y-planificacion/", 9),

    # --- El Salvador ---
    pol("policy:sv-ndc-2022", "NDC de El Salvador — actualización 2022", "El Salvador", "NDC", 2022,
        ["cross-cutting", "energy", "agua"], "in_force",
        "https://unfccc.int/sites/default/files/NDC/2022-01/El%20Salvador%20First%20NDC%20%28Updated%20submission%29.pdf", 0),
    pol("policy:sv-ley-medio-ambiente", "Decreto Legislativo N.° 233 — Ley del Medio Ambiente", "El Salvador", "law", 1998,
        ["cross-cutting", "agua", "bosques"], "in_force",
        "https://climate-laws.org/document/environmental-law_5a5a", 1),
    pol("policy:sv-plan-nacional-cc", "Plan Nacional de Cambio Climático (2012–2027)", "El Salvador", "strategy", 2012,
        ["cross-cutting"], "in_force",
        "https://climate-laws.org/document/national-climate-change-plan_6a6a", 2),
    pol("policy:sv-politica-ambiental", "Política Nacional del Medio Ambiente", "El Salvador", "strategy", 2012,
        ["cross-cutting"], "in_force",
        "https://www.marn.gob.sv/index.php/politicas-y-estrategias/", 3),
    pol("policy:sv-ley-energia-renovable", "Ley de Fomento y Desarrollo de las Energías Renovables", "El Salvador", "law", 2007,
        ["energy"], "in_force",
        "https://climate-laws.org/document/law-for-the-promotion-and-development-of-renewable-energy_3b3b", 4),
    pol("policy:sv-conamype-semilla", "CONAMYPE — capital semilla y emprendimiento verde", "El Salvador", "incentive", 2020,
        ["cross-cutting", "energy", "agriculture"], "in_force",
        "https://www.conamype.gob.sv/", 5),
    pol("policy:sv-fideagro", "FIDEAGRO — financiamiento agropecuario (MAG)", "El Salvador", "incentive", 2010,
        ["agriculture"], "in_force",
        "https://www.mag.gob.sv/fideagro/", 6),
    pol("policy:sv-estrategia-residuos", "Estrategia Nacional de Residuos Sólidos", "El Salvador", "strategy", 2018,
        ["residuos", "cross-cutting"], "in_force",
        "https://www.marn.gob.sv/", 7),

    # --- Guatemala ---
    pol("policy:gt-ndc-2022", "NDC de Guatemala — actualización 2022", "Guatemala", "NDC", 2022,
        ["cross-cutting", "energy", "bosques", "agua"], "in_force",
        "https://unfccc.int/sites/default/files/NDC/2022-06/GTM_NDC%20Actualizada%202022.pdf", 0),
    pol("policy:gt-politica-energia", "Política Nacional de Energía 2013–2032", "Guatemala", "strategy", 2013,
        ["energy"], "in_force",
        "https://climate-laws.org/document/national-energy-policy-2013-2032_8b8b", 1),
    pol("policy:gt-ley-incentivo-rer", "Ley de Incentivo para el Desarrollo de Proyectos de RER", "Guatemala", "law", 2003,
        ["energy"], "in_force",
        "https://climate-laws.org/document/law-of-incentives-for-the-development-of-renewable-energy-projects_4a4a", 2),
    pol("policy:gt-plan-clima", "Plan Nacional de Acción frente al Cambio Climático (PANCC)", "Guatemala", "strategy", 2016,
        ["cross-cutting", "agua", "agriculture"], "in_force",
        "https://climate-laws.org/document/national-action-plan-on-climate-change_7c7c", 3),
    pol("policy:gt-ley-proteccion-bosques", "Ley de Protección y Manejo de Bosques", "Guatemala", "law", 1996,
        ["bosques"], "in_force",
        "https://climate-laws.org/document/forest-protection-and-management-law_2d2d", 4),
    pol("policy:gt-politica-agua", "Política Nacional de Recursos Hídricos", "Guatemala", "strategy", 2009,
        ["agua"], "in_force",
        "https://www.marn.gob.gt/", 5),
    pol("policy:gt-taxonomia-sostenible", "Taxonomía Sostenible de Guatemala (borrador/BID)", "Guatemala", "taxonomy", 2023,
        ["finance", "energy"], "proposed",
        "https://www.iadb.org/es/noticias/guatemala-avanzara-en-su-taxonomia-sostenible", 6),
    pol("policy:gt-incentivo-biocombustibles", "Incentivos fiscales biocombustibles (Ley 17-85 reformas)", "Guatemala", "tax", 2005,
        ["energy", "agriculture"], "in_force",
        "https://climatepolicydatabase.org/", 7),

    # --- Costa Rica ---
    pol("policy:cr-ndc-2020", "NDC de Costa Rica — actualización 2020", "Costa Rica", "NDC", 2020,
        ["cross-cutting", "energy", "transport"], "in_force",
        "https://unfccc.int/sites/default/files/NDC/2021-01/Costa_Rica%20Updated%20NDC%202020.pdf", 0),
    pol("policy:cr-plan-descarbonizacion", "Plan Nacional de Descarbonización 2018–2050", "Costa Rica", "strategy", 2018,
        ["cross-cutting", "energy", "transport"], "in_force",
        "https://climate-laws.org/document/decarbonisation-plan_856a", 1),
    pol("policy:cr-plan-descarbonizacion-pdf", "Plan Nacional de Descarbonización (documento oficial)", "Costa Rica", "strategy", 2019,
        ["cross-cutting"], "in_force",
        "https://unfccc.int/sites/default/files/resource/NationalDecarbonizationPlan.pdf", 2),
    pol("policy:cr-ley-7200-electricidad", "Ley N.° 7200 — Servicio Público de Electricidad (marco)", "Costa Rica", "law", 1990,
        ["energy"], "in_force",
        "https://climate-laws.org/document/electricity-law-no-7200_1a1a", 3),
    pol("policy:cr-ley-gestion-residuos", "Ley N.° 8839 — Gestión Integral de Residuos", "Costa Rica", "law", 2010,
        ["residuos"], "in_force",
        "https://climate-laws.org/document/integrated-waste-management-law-no-8839_9c9c", 4),
    pol("policy:cr-banco-nacional-biodiversidad", "Banco Nacional de Biodiversidad (Ley 10401)", "Costa Rica", "law", 2024,
        ["bosques", "finance"], "in_force",
        "https://www.presidencia.go.cr/comunicados/2024/05/costa-rica-crea-banco-nacional-de-biodiversidad/", 5),
    pol("policy:cr-incentivos-rer-pyme", "Incentivos tarifarios RER para autoproductores (ARESEP)", "Costa Rica", "incentive", 2015,
        ["energy"], "in_force",
        "https://www.ares.go.cr/", 6),
    pol("policy:cr-plan-adaptacion", "Plan Nacional de Adaptación (PNA)", "Costa Rica", "strategy", 2014,
        ["agua", "agriculture", "cross-cutting"], "in_force",
        "https://cambioclimatico.go.cr/", 7),
]
# fmt: on

RELATION_DEFS: list[dict] = []

# --- Peru actor ↔ policy (verified) ---
RELATION_DEFS += [
    rel("pe-minam-ministerio-del-ambiente", "policy:pe-ley-30754-cc", "issues",
        "https://climate-laws.org/document/framework-law-no-30754-on-climate-change_688f",
        notes="MINAM es autoridad nacional de cambio climático (Ley 30754)"),
    rel("pe-minam-ministerio-del-ambiente", "policy:pe-ds-012-2024-encc", "issues",
        "https://climate-laws.org/document/supreme-decree-no-012-2024-minam-approves-the-national-policy-national-strategy-for-climate-change-to-2050-decreto-supremo-ndeg-012-2024-minam-aprueba-la-politica-nacional-estrategia-nacional-ante-el-cambio-climatico-al-2050_58d6"),
    rel("pe-minam-ministerio-del-ambiente", "policy:pe-ndc-2020", "issues",
        "https://cdn.www.gob.pe/uploads/document/file/1675213/Actualizaci%C3%B3n%20de%20las%20NDC%20del%20Per%C3%BA%20al%202030.pdf?v=1663622045"),
    rel("pe-minam-ministerio-del-ambiente", "policy:pe-marco-bonos-verdes", "oversees",
        "https://climate-laws.org/document/green-bonds-framework-for-peru_3b0b"),
    rel("pe-serfor", "policy:pe-ley-29763-forestal", "implements",
        "https://climate-laws.org/document/forestry-and-wildlife-law-no-29763_3a3f"),
    rel("pe-ana-autoridad-nacional-del-agua", "policy:pe-ley-29338-agua", "implements",
        "https://climate-laws.org/document/water-resources-law-no-29338_0a6a"),
    rel("pe-minem-ministerio-de-energia-y-minas", "policy:pe-ley-28832-rer", "oversees",
        "https://climate-laws.org/document/law-no-28832-to-promote-investment-in-electricity-generation-using-renewable-energy_5f8e"),
    rel("pe-programa-bosques-minam", "policy:pe-programa-bosques-norma", "implements",
        "https://www.gob.pe/institucion/minam/campañas/123-programa-bosques"),
    rel("pe-programa-para-bionegocios-minam", "policy:pe-ley-29763-forestal", "implements",
        "https://climate-laws.org/document/forestry-and-wildlife-law-no-29763_3a3f",
        notes="Bionegocios forestales alineados a marco forestal"),
    rel("pe-produce-ministerio-de-la-produccion", "policy:pe-proinnovate-clima", "issues",
        "https://www.produce.gob.pe/proinnovate"),
    rel("pe-proinnovate-startup-peru", "policy:pe-proinnovate-clima", "implements",
        "https://www.produce.gob.pe/proinnovate"),
    rel("policy:pe-ley-30754-cc", "challenge:PE-1-bosques", "enables",
        "https://climate-laws.org/document/framework-law-no-30754-on-climate-change_688f",
        notes="Art. 16 — prioriza gestión forestal y sumideros"),
    rel("policy:pe-ley-30754-cc", "challenge:PE-2-agua", "enables",
        "https://climate-laws.org/document/framework-law-no-30754-on-climate-change_688f"),
    rel("policy:pe-ley-29338-agua", "challenge:PE-2-agua", "enables",
        "https://climate-laws.org/document/water-resources-law-no-29338_0a6a"),
    rel("policy:pe-ley-29763-forestal", "challenge:PE-1-bosques", "enables",
        "https://climate-laws.org/document/forestry-and-wildlife-law-no-29763_3a3f"),
    rel("policy:pe-proinnovate-clima", "pe-emprende-up-climatech-rein-hub-peru", "finances",
        "https://www.produce.gob.pe/proinnovate",
        notes="Cofinanciamiento incubadoras CC vía StartUp Perú"),
    rel("pe-yakusmart", "policy:pe-proinnovate-clima", "eligible",
        "https://www.produce.gob.pe/proinnovate", suggested=True,
        notes="Startup bosques/Amazonía — encaje sectorial con línea CC"),
    rel("pe-yakufil", "policy:pe-ley-29338-agua", "benefits",
        "https://climate-laws.org/document/water-resources-law-no-29338_0a6a",
        suggested=True, notes="Filtración de agua — encaje con marco hídrico"),
    rel("pe-uqhu", "policy:pe-ley-29338-agua", "benefits",
        "https://climate-laws.org/document/water-resources-law-no-29338_0a6a",
        suggested=True),
    rel("pe-rebike-up", "policy:pe-ley-28832-rer", "eligible",
        "https://climate-laws.org/document/law-no-28832-to-promote-investment-in-electricity-generation-using-renewable-energy_5f8e",
        suggested=True, notes="Movilidad eléctrica — encaje con marco RER"),
]

# --- Colombia ---
RELATION_DEFS += [
    rel("co-minenergia", "policy:co-ley-2099-transicion", "issues",
        "https://climatepolicydatabase.org/policies/law-2099-energy-transition-and-economic-reactivation"),
    rel("co-minenergia", "policy:co-ley-1715-rer", "oversees",
        "https://climate-laws.org/document/law-1715-2014-regulating-the-integration-and-promotion-of-non-conventional-renewable-energy-fncer_6bed"),
    rel("co-upme", "policy:co-ley-1715-rer", "implements",
        "https://climate-laws.org/document/law-1715-2014-regulating-the-integration-and-promotion-of-non-conventional-renewable-energy-fncer_6bed"),
    rel("co-creg", "policy:co-ley-1715-rer", "implements",
        "https://climate-laws.org/document/law-1715-2014-regulating-the-integration-and-promotion-of-non-conventional-renewable-energy-fncer_6bed",
        notes="Regulación tarifaria FNCER"),
    rel("co-ipse", "policy:co-ipse-rural", "implements",
        "https://www.minenergia.gov.co/es/minienergia/institucional/plan-ipse/"),
    rel("co-minenergia", "policy:co-ipse-rural", "issues",
        "https://www.minenergia.gov.co/es/minienergia/institucional/plan-ipse/"),
    rel("co-minenergia", "policy:co-taxonomia-verde", "oversees",
        "https://www.taxonomiaverde.gov.co/documents/d/taxonomia-verde/circular_externa_005_de_2022",
        notes="Sector energía en taxonomía; coordinación interinstitucional"),
    rel("policy:co-ley-2099-transicion", "co-ipse", "enables",
        "https://climatepolicydatabase.org/policies/law-2099-energy-transition-and-economic-reactivation",
        notes="Transición energética vinculada a acceso ZNI"),
    rel("policy:co-taxonomia-verde", "co-ipse", "finances",
        "https://www.taxonomiaverde.gov.co/",
        notes="Clasificación verde para financiamiento de proyectos energéticos"),
    rel("policy:co-fenoge", "policy:co-ley-1715-rer", "implements",
        "https://www.minenergia.gov.co/es/minienergia/institucional/entidades-adscritas/fenoge/"),
    rel("policy:co-ndc-2020", "policy:co-ley-2169-carbono", "enables",
        "https://climate-laws.org/document/law-2169-of-2021-on-climate-change-management_0f0f"),
]

# --- El Salvador ---
RELATION_DEFS += [
    rel("sv-marn-ministerio-de-medio-ambiente-y-recursos-natur", "policy:sv-ndc-2022", "issues",
        "https://unfccc.int/sites/default/files/NDC/2022-01/El%20Salvador%20First%20NDC%20%28Updated%20submission%29.pdf"),
    rel("sv-marn-ministerio-de-medio-ambiente-y-recursos-natur", "policy:sv-ley-medio-ambiente", "oversees",
        "https://climate-laws.org/document/environmental-law_5a5a"),
    rel("sv-marn-ministerio-de-medio-ambiente-y-recursos-natur", "policy:sv-plan-nacional-cc", "issues",
        "https://climate-laws.org/document/national-climate-change-plan_6a6a"),
    rel("sv-minec-ministerio-de-economia", "policy:sv-conamype-semilla", "oversees",
        "https://www.conamype.gob.sv/"),
    rel("sv-conamype", "policy:sv-conamype-semilla", "implements",
        "https://www.conamype.gob.sv/"),
    rel("sv-mag-ministerio-de-agricultura-y-ganaderia", "policy:sv-fideagro", "issues",
        "https://www.mag.gob.sv/fideagro/"),
    rel("sv-fideagro", "policy:sv-fideagro", "implements",
        "https://www.mag.gob.sv/fideagro/",
        notes="Programa FIDEAGRO como instrumento de fomento agro"),
    rel("policy:sv-ley-energia-renovable", "policy:sv-ndc-2022", "enables",
        "https://climate-laws.org/document/law-for-the-promotion-and-development-of-renewable-energy_3b3b"),
    rel("sv-iagros", "policy:sv-fideagro", "eligible",
        "https://www.mag.gob.sv/fideagro/",
        suggested=True, notes="Agrotech — encaje con línea agro"),
    rel("sv-recicla503", "policy:sv-estrategia-residuos", "benefits",
        "https://www.marn.gob.sv/",
        suggested=True, notes="Economía circular / residuos"),
]

# --- Guatemala (no gov actors in graph yet — policy-only + NDC) ---
RELATION_DEFS += [
    rel("policy:gt-ndc-2022", "policy:gt-plan-clima", "enables",
        "https://unfccc.int/sites/default/files/NDC/2022-06/GTM_NDC%20Actualizada%202022.pdf"),
    rel("policy:gt-politica-energia", "policy:gt-ley-incentivo-rer", "implements",
        "https://climate-laws.org/document/national-energy-policy-2013-2032_8b8b"),
    rel("policy:gt-plan-clima", "policy:gt-politica-agua", "enables",
        "https://climate-laws.org/document/national-action-plan-on-climate-change_7c7c", suggested=True,
        notes="PANCC incluye eje hídrico — vínculo inferido del plan"),
]

# --- Costa Rica (no actors in graph) ---
RELATION_DEFS += [
    rel("policy:cr-plan-descarbonizacion", "policy:cr-ndc-2020", "enables",
        "https://climate-laws.org/document/decarbonisation-plan_856a"),
    rel("policy:cr-plan-descarbonizacion", "policy:cr-ley-7200-electricidad", "implements",
        "https://unfccc.int/sites/default/files/resource/NationalDecarbonizationPlan.pdf",
        notes="Eje 4 — sistema eléctrico renovable"),
    rel("policy:cr-incentivos-rer-pyme", "policy:cr-ley-7200-electricidad", "implements",
        "https://www.ares.go.cr/", suggested=True,
        notes="Autoproducción RER — encaje regulatorio inferido"),
]


# Canonical open sources (climate-laws.org, UNFCCC, gazettes, ministries, CPD)
SOURCE_URL_OVERRIDES: dict[str, str] = {
    "policy:pe-ley-29763-forestal": "https://climate-laws.org/document/law-no-29763-forestry-and-wildlife-law-ley-no-29763-ley-forestal-y-de-fauna-silvestre_ecb8",
    "policy:pe-ley-29338-agua": "https://sinia.minam.gob.pe/normas/ley-recursos-hidricos-0",
    "policy:pe-ley-28832-rer": "https://www.gob.pe/institucion/minem/normas-legales/2856-28832",
    "policy:pe-ds-013-2019-reglamento-cc": "https://climate-laws.org/document/supreme-decree-no-013-2019-minam-approving-the-regulation-of-law-no-30754-framework-law-on-climate-change_0d0a",
    "policy:pe-marco-bonos-verdes": "https://www.gob.pe/institucion/minam/informes-publicaciones/178421-marco-para-bonos-verdes",
    "policy:pe-proinnovate-clima": "https://www.gob.pe/proinnovate",
    "policy:pe-programa-bosques-norma": "https://www.gob.pe/institucion/minam/informes-publicaciones/178421-programa-bosques",
    "policy:pe-ley-28611-ambiental": "https://www.gob.pe/institucion/congreso-de-la-republica/normas-legales/3580-28611",
    "policy:pe-plan-mitigacion-2023": "https://www.gob.pe/institucion/minam/informes-publicaciones/244041-plan-nacional-de-mitigacion-de-gases-de-efecto-invernadero",
    "policy:co-ley-1715-rer": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353",
    "policy:co-ley-1931-adaptacion": "https://cancilleria.gov.co/normograma/compilacion/docs/ley_1931_2018.htm",
    "policy:co-ley-2169-carbono": "https://climate-laws.org/document/law-2169-2021-promoting-low-carbon-development-last-amended-by-law-2294-2023_8496",
    "policy:co-plan-nacional-adaptacion": "https://www.minambiente.gov.co/wp-content/uploads/2021/10/plan-nacional-de-adaptacion-al-cambio-climatico.pdf",
    "policy:co-fenoge": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353",
    "policy:co-ipse-rural": "https://www.minenergia.gov.co/documents/10192/0/Plan+IPSE+2023-2026.pdf",
    "policy:co-contribucion-carbono": "https://www.minambiente.gov.co/cambio-climatico-y-gestion-del-riesgo/",
    "policy:sv-ley-medio-ambiente": "https://www.transparencia.gob.sv/institutions/marn/documents/285566/download",
    "policy:sv-plan-nacional-cc": "https://unfccc.int/sites/default/files/resource/El%20Salvador%20NC3%20Executive%20Summary%20Spanish.pdf",
    "policy:sv-politica-ambiental": "https://www.rree.gob.sv/wp-content/uploads/2016/03/Politica-Nacional-del-Medio-Ambiente.pdf",
    "policy:sv-ley-energia-renovable": "https://www.osarlaft.gob.sv/wp-content/uploads/2017/05/Ley-de-Fomento-y-Desarrollo-de-las-Energias-Renovables.pdf",
    "policy:gt-politica-energia": "https://www.mineco.gob.gt/sites/default/files/Politica_Nacional_de_Energia_2013-2032.pdf",
    "policy:gt-ley-incentivo-rer": "https://www.pgn.gob.gt/wp-content/uploads/2015/12/Decreto-52-2003-Ley-de-Incentivo-para-el-Desarrollo-de-Proyectos-de-Energia-Renovable.pdf",
    "policy:gt-plan-clima": "https://unfccc.int/sites/default/files/resource/GTM_PANCC_2016.pdf",
    "policy:gt-ley-proteccion-bosques": "https://www.conap.gob.gt/wp-content/uploads/2021/03/Ley-de-Proteccion-y-Manejo-de-Bosques.pdf",
    "policy:gt-politica-agua": "https://www.marn.gob.gt/wp-content/uploads/2015/09/Politica-Nacional-de-Recursos-Hidricos.pdf",
    "policy:gt-taxonomia-sostenible": "https://www.iadb.org/en/news/guatemala-will-advance-its-sustainable-taxonomy",
    "policy:gt-incentivo-biocombustibles": "https://climatepolicydatabase.org/policies/guatemala-biofuels-incentive-law",
    "policy:cr-ley-7200-electricidad": "https://www.pgrweb.go.cr/scij/Busqueda/Normativa/Normas/nrm_texto_completo.aspx?nValor1=1&nValor2=1990&nValor3=7200",
    "policy:cr-ley-gestion-residuos": "https://www.pgrweb.go.cr/scij/Busqueda/Normativa/Normas/nrm_texto_completo.aspx?nValor1=1&nValor2=2010&nValor3=8839",
    "policy:cr-banco-nacional-biodiversidad": "https://www.pgrweb.go.cr/scij/Busqueda/Normativa/Normas/nrm_texto_completo.aspx?nValor1=1&nValor2=2024&nValor3=10401",
    "policy:cr-incentivos-rer-pyme": "https://www.aresep.go.cr/Generacion_distribuida/",
    "policy:cr-plan-adaptacion": "https://cambioclimatico.go.cr/pna/",
}


def apply_source_overrides(policies: list[dict], relations: list[dict]) -> None:
    id_to_url = {p["id"]: p["source_url"] for p in policies}
    for pid, url in SOURCE_URL_OVERRIDES.items():
        id_to_url[pid] = url
    for p in policies:
        if p["id"] in SOURCE_URL_OVERRIDES:
            p["source_url"] = SOURCE_URL_OVERRIDES[p["id"]]
    for r in relations:
        if r["target"] in id_to_url and r["type"] in {"issues", "oversees", "implements", "enables", "finances", "benefits", "eligible"}:
            if r["target"].startswith("policy:"):
                r["source_url"] = id_to_url[r["target"]]
        if r["source"] in id_to_url and r["type"] in {"issues", "oversees", "implements", "enables", "finances"}:
            if r["source"].startswith("policy:"):
                r["source_url"] = id_to_url[r["source"]]


def main() -> None:
    policies = list(POLICY_DEFS)
    relations = list(RELATION_DEFS)
    apply_source_overrides(policies, relations)
    OUT_POLICIES.parent.mkdir(parents=True, exist_ok=True)
    payload_p = json.dumps(policies, ensure_ascii=False, indent=1) + "\n"
    payload_r = json.dumps(relations, ensure_ascii=False, indent=1) + "\n"
    OUT_POLICIES.write_text(payload_p, encoding="utf-8")
    OUT_RELATIONS.write_text(payload_r, encoding="utf-8")
    OUT_PROTOTYPE_SHARED.mkdir(parents=True, exist_ok=True)
    (OUT_PROTOTYPE_SHARED / "policies.json").write_text(payload_p, encoding="utf-8")
    (OUT_PROTOTYPE_SHARED / "policy_relations.json").write_text(payload_r, encoding="utf-8")

    by_country = Counter(p["country"] for p in policies)
    by_type = Counter(p["instrument_type"] for p in policies)
    verified = sum(1 for r in relations if r.get("verified"))
    suggested = sum(1 for r in relations if r.get("suggested"))
    print("policies", len(policies), dict(by_country))
    print("instrument_types", dict(by_type))
    print("relations", len(relations), "verified", verified, "suggested", suggested)


if __name__ == "__main__":
    main()
