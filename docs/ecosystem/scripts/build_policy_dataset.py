#!/usr/bin/env python3
"""Build staged policy dataset for Nexus ecosystem (research branch only)."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ACTORS = ROOT / "docs/ecosystem/prototype/data/actors.json"
OUT_POLICIES = ROOT / "data/policies.json"
OUT_RELS = ROOT / "policy_relations.json"

# Nexus actor countries (from actors.json)
NEXUS_COUNTRIES = {"Colombia", "Peru", "El Salvador"}

CHALLENGE_SECTOR_MAP = {
    "challenge:PE-1-bosques": {"bosques", "bioeconomía", "amazonía", "forestal"},
    "challenge:PE-2-agua": {"agua", "hídricos", "glaciares", "cuencas"},
}

# (actor_id, policy_id, source_url, note) — source must name the institution or host the program page
VERIFIED_ISSUES_POLICY: list[tuple[str, str, str, str]] = [
    # Colombia
    ("co-minenergia", "policy:co-ley-2099-2021", "http://secretariasenado.gov.co/senado/basedoc/ley_2099_2021.html", "Ley assigns Minas y Energía"),
    ("co-minenergia", "policy:co-ley-1931-2018", "http://secretariasenado.gov.co/senado/basedoc/ley_1931_2018.html", "Sector eléctrico / MinEnergía"),
    ("co-minenergia", "policy:co-ley-1715-2014", "http://secretariasenado.gov.co/senado/basedoc/ley_1715_2014.html", "ERNC — competencia sectorial"),
    ("co-minenergia", "policy:co-fenoge-decreto-1543", "https://www.minenergia.gov.co/es/misional/energia-electrica-2/fondos-especiales/fondo-de-energ%C3%ADas-no-convencionales-y-gesti%C3%B3n-eficiente-de-la-energ%C3%ADa-fenoge/", "FENOGE bajo MinEnergía"),
    ("co-minenergia", "policy:co-ndc-2020-update", "https://unfccc.int/sites/default/files/NDC/2022-06/Colombia_NDC_actualizada.pdf", "NDC sector energía y transición"),
    ("co-minenergia", "policy:co-ndc-cpd-2025", "https://www.climatepolicydatabase.org/policies/nationally-determined-contribution-ndc-176", "NDC 3.0 — CICC / sector ministers"),
    ("co-ipse", "policy:co-ipse-programa-acceso", "https://www.ipse.gov.co/", "IPSE programa ZNI"),
    ("co-creg", "policy:co-decreto-2239-zni", "https://climate-laws.org/document/decreto-2239-de-2023_9f2a", "CREG regula ZNI"),
    ("co-upme", "policy:co-ley-2099-2021", "http://secretariasenado.gov.co/senado/basedoc/ley_2099_2021.html", "UPME registra proyectos ERNC (Ley 2099)"),
    ("co-bancoldex", "policy:co-taxonomia-verde", "https://www.taxonomiaverde.gov.co/documents/d/taxonomia-verde/240925_guiia-de-bancos_vf", "Guía TVC para bancos"),
    # Peru — MINAM / sector agencies named on gob.pe or law text
    ("pe-minam-ministerio-del-ambiente", "policy:pe-ley-30754-2018", "https://www.gob.pe/institucion/presidencia/normas-legales/355750-30754", "Ley nombra MINAM autoridad nacional CC"),
    ("pe-minam-ministerio-del-ambiente", "policy:pe-ds-013-2019-minam", "https://www.gob.pe/institucion/minam/normas-legales/395204-013-2019-minam", "Reglamento LMCC — MINAM"),
    ("pe-minam-ministerio-del-ambiente", "policy:pe-encc-2050-2024", "https://www.gob.pe/institucion/minam/informes-publicaciones/6562767", "Política Nacional ENCC — MINAM"),
    ("pe-minam-ministerio-del-ambiente", "policy:pe-ley-28611-2005", "https://leap.unep.org/en/akn/pe/act/2005/28611/spa@2005-10-15/overview", "Ley General del Ambiente — MINAM"),
    ("pe-minam-ministerio-del-ambiente", "policy:pe-ndc-2020", "https://unfccc.int/sites/default/files/NDC/2021-07/Peru_NDC%20update%202020.pdf", "MINAM monitorea NDC (Ley 30754)"),
    ("pe-minam-ministerio-del-ambiente", "policy:pe-ds-013-2019-ndc-list", "https://busquedas.elperuano.pe/dispositivo/NL/2440259-3", "DS NDC — MINAM"),
    ("pe-minam-ministerio-del-ambiente", "policy:pe-programa-bionegocios", "https://www.gob.pe/institucion/minam/campa%C3%B1as/46380-programa-para-bionegocios", "Campaña MINAM"),
    ("pe-minam-ministerio-del-ambiente", "policy:pe-programa-bosques", "https://www.gob.pe/institucion/minam/campa%C3%B1as/46379-programa-nacional-de-conservacion-de-bosques", "Campaña MINAM"),
    ("pe-programa-para-bionegocios-minam", "policy:pe-programa-bionegocios", "https://www.gob.pe/institucion/minam/campa%C3%B1as/46380-programa-para-bionegocios", "Entidad programa MINAM"),
    ("pe-programa-bosques-minam", "policy:pe-programa-bosques", "https://www.gob.pe/institucion/minam/campa%C3%B1as/46379-programa-nacional-de-conservacion-de-bosques", "Entidad programa MINAM"),
    ("pe-minem-ministerio-de-energia-y-minas", "policy:pe-ley-27270-2000", "https://leap.unep.org/en/akn/pe/act/2000/27270/spa@2000-11-08/overview", "MINEM — ER"),
    ("pe-serfor", "policy:pe-ley-29763-2011", "https://leap.unep.org/en/akn/pe/act/2011/29763/spa@2011-07-27/overview", "SERFOR aplica Ley Forestal"),
    ("pe-ana-autoridad-nacional-del-agua", "policy:pe-ley-29338-2009", "https://leap.unep.org/en/akn/pe/act/2009/29338/spa@2009-08-03/overview", "ANA — recursos hídricos"),
    ("pe-produce-ministerio-de-la-produccion", "policy:pe-startup-peru-clima", "https://www.gob.pe/institucion/produce/campa%C3%B1as/46381-startup-peru", "PRODUCE — StartUp Perú"),
    ("pe-proinnovate-startup-peru", "policy:pe-startup-peru-clima", "https://www.gob.pe/institucion/produce/campa%C3%B1as/46381-startup-peru", "ProInnóvate ejecuta línea"),
    ("pe-sernanp", "policy:pe-programa-bosques", "https://www.gob.pe/institucion/minam/campa%C3%B1as/46379-programa-nacional-de-conservacion-de-bosques", "SERNANP en medidas bosques / ANP"),
    ("pe-osinergmin", "policy:pe-ley-27270-2000", "https://leap.unep.org/en/akn/pe/act/2000/27270/spa@2000-11-08/overview", "Regulación eléctrica vinculada ER"),
    ("pe-sunass", "policy:pe-ley-29338-2009", "https://leap.unep.org/en/akn/pe/act/2009/29338/spa@2009-08-03/overview", "SUNASS — servicios de agua potable"),
    ("pe-midagri-ministerio-de-desarrollo-agrario-y-riego", "policy:pe-ndc-2020", "https://unfccc.int/sites/default/files/NDC/2021-07/Peru_NDC%20update%202020.pdf", "NDC lista medidas agro"),
    # El Salvador
    ("sv-marn-ministerio-de-medio-ambiente-y-recursos-natur", "policy:sv-ley-medio-ambiente-1998", "https://climate-laws.org/geographies/el-salvador", "MARN repositorio Ley Medio Ambiente"),
    ("sv-marn-ministerio-de-medio-ambiente-y-recursos-natur", "policy:sv-pncc-2017", "https://climate-laws.org/geographies/el-salvador", "MARN — PNCC"),
    ("sv-marn-ministerio-de-medio-ambiente-y-recursos-natur", "policy:sv-ndc-2021", "https://unfccc.int/sites/default/files/NDC/2022-06/El%20Salvador_NDC%20Actualizaci%C3%B3n%202021.pdf", "MARN liderazgo ambiental NDC"),
    ("sv-minec-ministerio-de-economia", "policy:sv-estrategia-ernc-2017", "https://climate-laws.org/geographies/el-salvador", "MINEC publica estrategia ERNC"),
    ("sv-minec-ministerio-de-economia", "policy:sv-conamype-ley-2016", "https://www.transparencia.gob.sv/institutions/conamype/documents/338012/download", "MINEC supervisa CONAMYPE (relations.json)"),
    ("sv-bandesal-banco-de-desarrollo-de-el-salvador", "policy:sv-linea-credito-verde", "https://www.bandesal.gob.sv/", "BANDESAL — Línea Verde"),
    ("sv-conamype", "policy:sv-conamype-ley-2016", "https://www.transparencia.gob.sv/institutions/conamype/documents/338012/download", "CONAMYPE — ley MIPYME"),
    ("sv-mag-ministerio-de-agricultura-y-ganaderia", "policy:sv-politica-bioeconomia-2022", "https://climate-laws.org/geographies/el-salvador", "MAG — bioeconomía"),
    ("sv-mag-ministerio-de-agricultura-y-ganaderia", "policy:sv-fideagro-programa", "https://climate-laws.org/geographies/el-salvador", "MAG — FIDEAGRO (runs program in graph)"),
]


def policy_row(**kw):
    row = {
        "type": "Policy",
        "status": "in_force",
        **kw,
    }
    return row


POLICIES = [
    # —— Colombia ——
    policy_row(id="policy:co-ley-2169-2021", name="Ley 2169/2021 — carbono neutralidad", country="Colombia", instrument="law", year=2021,
               sectors=["energía", "bosques", "adaptación"], source_url="https://climate-laws.org/document/law-2169-2021-promoting-low-carbon-development-last-amended-by-law-2294-2023_8496",
               registry="climate-laws.org"),
    policy_row(id="policy:co-ley-2099-2021", name="Ley 2099/2021 — transición energética", country="Colombia", instrument="law", year=2021,
               sectors=["energía", "movilidad"], source_url="http://secretariasenado.gov.co/senado/basedoc/ley_2099_2021.html", registry="national-gazette"),
    policy_row(id="policy:co-ley-1931-2018", name="Ley 1931/2018 — integración ERNC", country="Colombia", instrument="law", year=2018,
               sectors=["energía"], source_url="http://secretariasenado.gov.co/senado/basedoc/ley_1931_2018.html", registry="national-gazette"),
    policy_row(id="policy:co-ley-1715-2014", name="Ley 1715/2014 — energías renovables", country="Colombia", instrument="law", year=2014,
               sectors=["energía"], source_url="http://secretariasenado.gov.co/senado/basedoc/ley_1715_2014.html", registry="national-gazette"),
    policy_row(id="policy:co-ley-1819-2016", name="Ley 1819/2016 — impuesto al carbono y ER", country="Colombia", instrument="tax", year=2016,
               sectors=["energía", "mitigación"], source_url="https://climate-laws.org/document/law-1819-2016-on-tax-deductions-for-renewables-and-carbon-tax-regulated-partially-by-decree-926-2017-and-last-amended-by-law-2169-2021_1d43", registry="climate-laws.org"),
    policy_row(id="policy:co-ley-2294-2023", name="Ley 2294/2023 — Plan Nacional de Desarrollo 2022–2026", country="Colombia", instrument="strategy", year=2023,
               sectors=["energía", "adaptación", "bosques"], source_url="https://www.climatepolicydatabase.org/countries/colombia", registry="climatepolicydatabase.org"),
    policy_row(id="policy:co-taxonomia-verde", name="Taxonomía Verde de Colombia (TVC)", country="Colombia", instrument="taxonomy", year=2022,
               sectors=["energía", "agua", "bosques", "economía circular"], source_url="https://www.taxonomiaverde.gov.co/", registry="national-taxonomy"),
    policy_row(id="policy:co-ndc-2020-update", name="NDC Colombia (actualización 2020)", country="Colombia", instrument="NDC", year=2020,
               sectors=["energía", "bosques", "agricultura"], status="submitted", source_url="https://unfccc.int/sites/default/files/NDC/2022-06/Colombia_NDC_actualizada.pdf", registry="unfccc.int"),
    policy_row(id="policy:co-ndc-cpd-2025", name="NDC 3.0 Colombia (CPD 2025)", country="Colombia", instrument="NDC", year=2025,
               sectors=["energía", "bosques", "adaptación"], status="submitted", source_url="https://www.climatepolicydatabase.org/policies/nationally-determined-contribution-ndc-176", registry="climatepolicydatabase.org"),
    policy_row(id="policy:co-conpes-4021-2021", name="CONPES 4021 — política nacional CC", country="Colombia", instrument="strategy", year=2021,
               sectors=["adaptación", "energía", "bosques"], source_url="https://climate-laws.org/document/conpes-4021-of-2021_5c8e", registry="climate-laws.org"),
    policy_row(id="policy:co-fenoge-decreto-1543", name="Decreto 1543/2017 — Fondo FENOGE", country="Colombia", instrument="regulation", year=2017,
               sectors=["energía"], source_url="https://www.minenergia.gov.co/es/misional/energia-electrica-2/fondos-especiales/fondo-de-energ%C3%ADas-no-convencionales-y-gesti%C3%B3n-eficiente-de-la-energ%C3%ADa-fenoge/", registry="national-ministry"),
    policy_row(id="policy:co-decreto-2239-zni", name="Decreto 2239/2023 — ZNI", country="Colombia", instrument="regulation", year=2023,
               sectors=["energía", "acceso"], source_url="https://climate-laws.org/document/decreto-2239-de-2023_9f2a", registry="climate-laws.org"),
    policy_row(id="policy:co-ipse-programa-acceso", name="Programa IPSE — acceso energético ZNI", country="Colombia", instrument="incentive", year=2018,
               sectors=["energía", "acceso"], status="active", source_url="https://www.ipse.gov.co/", registry="national-agency"),
    policy_row(id="policy:co-jet-roadmap-2024", name="Just Energy Transition Roadmap (CPD)", country="Colombia", instrument="strategy", year=2024,
               sectors=["energía", "transición justa"], source_url="https://www.climatepolicydatabase.org/countries/colombia", registry="climatepolicydatabase.org"),
    # —— Peru ——
    policy_row(id="policy:pe-ley-30754-2018", name="Ley 30754 — marco cambio climático", country="Peru", instrument="law", year=2018,
               sectors=["adaptación", "energía", "bosques"], source_url="https://www.gob.pe/institucion/presidencia/normas-legales/355750-30754", registry="gob.pe"),
    policy_row(id="policy:pe-ds-013-2019-minam", name="DS 013-2019-MINAM — reglamento LMCC", country="Peru", instrument="regulation", year=2019,
               sectors=["adaptación", "energía"], source_url="https://www.gob.pe/institucion/minam/normas-legales/395204-013-2019-minam", registry="gob.pe"),
    policy_row(id="policy:pe-encc-2050-2024", name="Política Nacional ENCC al 2050", country="Peru", instrument="strategy", year=2024,
               sectors=["adaptación", "energía", "agua"], source_url="https://www.gob.pe/institucion/minam/informes-publicaciones/6562767", registry="gob.pe"),
    policy_row(id="policy:pe-ndc-2020", name="NDC Perú (2020)", country="Peru", instrument="NDC", year=2020,
               sectors=["bosques", "energía", "agua"], status="submitted", source_url="https://unfccc.int/sites/default/files/NDC/2021-07/Peru_NDC%20update%202020.pdf", registry="unfccc.int"),
    policy_row(id="policy:pe-ndc-cpd", name="NDC Perú (Climate Policy Database)", country="Peru", instrument="NDC", year=2020,
               sectors=["bosques", "energía", "agua"], status="submitted", source_url="https://www.climatepolicydatabase.org/countries/peru", registry="climatepolicydatabase.org"),
    policy_row(id="policy:pe-ley-27270-2000", name="Ley 27270 — promoción ER", country="Peru", instrument="law", year=2000,
               sectors=["energía"], source_url="https://leap.unep.org/en/akn/pe/act/2000/27270/spa@2000-11-08/overview", registry="climate-laws.org"),
    policy_row(id="policy:pe-ley-28611-2005", name="Ley 28611 — Ley General del Ambiente", country="Peru", instrument="law", year=2005,
               sectors=["bosques", "agua", "adaptación"], source_url="https://leap.unep.org/en/akn/pe/act/2005/28611/spa@2005-10-15/overview", registry="climate-laws.org"),
    policy_row(id="policy:pe-ley-29763-2011", name="Ley 29763 — Ley Forestal", country="Peru", instrument="law", year=2011,
               sectors=["bosques"], source_url="https://leap.unep.org/en/akn/pe/act/2011/29763/spa@2011-07-27/overview", registry="climate-laws.org"),
    policy_row(id="policy:pe-ley-29338-2009", name="Ley 29338 — recursos hídricos", country="Peru", instrument="law", year=2009,
               sectors=["agua"], source_url="https://leap.unep.org/en/akn/pe/act/2009/29338/spa@2009-08-03/overview", registry="climate-laws.org"),
    policy_row(id="policy:pe-ds-013-2019-ndc-list", name="DS listado medidas NDC (2025)", country="Peru", instrument="regulation", year=2025,
               sectors=["adaptación", "energía", "bosques"], source_url="https://busquedas.elperuano.pe/dispositivo/NL/2440259-3", registry="national-gazette"),
    policy_row(id="policy:pe-programa-bionegocios", name="Programa para Bionegocios (MINAM)", country="Peru", instrument="incentive", year=2019,
               sectors=["bosques", "bioeconomía"], status="active", source_url="https://www.gob.pe/institucion/minam/campa%C3%B1as/46380-programa-para-bionegocios", registry="gob.pe"),
    policy_row(id="policy:pe-programa-bosques", name="Programa Nacional de Conservación de Bosques", country="Peru", instrument="incentive", year=2010,
               sectors=["bosques"], status="active", source_url="https://www.gob.pe/institucion/minam/campa%C3%B1as/46379-programa-nacional-de-conservacion-de-bosques", registry="gob.pe"),
    policy_row(id="policy:pe-startup-peru-clima", name="StartUp Perú — línea Cambio Climático", country="Peru", instrument="incentive", year=2023,
               sectors=["emprendimiento", "energía"], status="active", source_url="https://www.gob.pe/institucion/produce/campa%C3%B1as/46381-startup-peru", registry="gob.pe"),
    policy_row(id="policy:pe-clima-law-cpd", name="Marco climático Perú (CPD índice)", country="Peru", instrument="strategy", year=2024,
               sectors=["adaptación", "energía", "agua", "bosques"], source_url="https://www.climatepolicydatabase.org/countries/peru", registry="climatepolicydatabase.org"),
    policy_row(id="policy:pe-geography-cclw", name="Peru climate laws (LSE CCLW)", country="Peru", instrument="strategy", year=2024,
               sectors=["adaptación", "energía", "agua", "bosques"], source_url="https://climate-laws.org/geographies/peru", registry="climate-laws.org"),
    # —— El Salvador ——
    policy_row(id="policy:sv-ley-medio-ambiente-1998", name="Ley del Medio Ambiente", country="El Salvador", instrument="law", year=1998,
               sectors=["adaptación", "agua", "bosques"], source_url="https://climate-laws.org/geographies/el-salvador", registry="climate-laws.org"),
    policy_row(id="policy:sv-pncc-2017", name="Plan Nacional de Cambio Climático", country="El Salvador", instrument="strategy", year=2017,
               sectors=["adaptación", "energía", "agua"], source_url="https://climate-laws.org/geographies/el-salvador", registry="climate-laws.org"),
    policy_row(id="policy:sv-ndc-2021", name="NDC El Salvador (2021)", country="El Salvador", instrument="NDC", year=2021,
               sectors=["energía", "bosques", "agua"], status="submitted", source_url="https://unfccc.int/sites/default/files/NDC/2022-06/El%20Salvador_NDC%20Actualizaci%C3%B3n%202021.pdf", registry="unfccc.int"),
    policy_row(id="policy:sv-ndc-cpd", name="NDC El Salvador (CPD)", country="El Salvador", instrument="NDC", year=2021,
               sectors=["energía", "bosques", "agua"], status="submitted", source_url="https://www.climatepolicydatabase.org/countries/el-salvador", registry="climatepolicydatabase.org"),
    policy_row(id="policy:sv-estrategia-ernc-2017", name="Estrategia Nacional de Energías Renovables", country="El Salvador", instrument="strategy", year=2017,
               sectors=["energía"], source_url="https://climate-laws.org/geographies/el-salvador", registry="climate-laws.org"),
    policy_row(id="policy:sv-linea-credito-verde", name="Línea de Crédito Verde (BANDESAL)", country="El Salvador", instrument="incentive", year=2019,
               sectors=["energía", "agricultura"], status="active", source_url="https://www.bandesal.gob.sv/", registry="national-bank"),
    policy_row(id="policy:sv-ley-aguas-2012", name="Ley General de Aguas (2012)", country="El Salvador", instrument="law", year=2012,
               sectors=["agua"], source_url="https://climate-laws.org/geographies/el-salvador", registry="climate-laws.org"),
    policy_row(id="policy:sv-politica-bioeconomia-2022", name="Política Nacional de Bioeconomía", country="El Salvador", instrument="strategy", year=2022,
               sectors=["agricultura", "bosques"], source_url="https://climate-laws.org/geographies/el-salvador", registry="climate-laws.org"),
    policy_row(id="policy:sv-conamype-ley-2016", name="Ley de Fomento a la MIPYME", country="El Salvador", instrument="law", year=2016,
               sectors=["emprendimiento", "energía"], source_url="https://www.transparencia.gob.sv/institutions/conamype/documents/338012/download", registry="national-gazette"),
    policy_row(id="policy:sv-fideagro-programa", name="FIDEAGRO — financiamiento agro (programa)", country="El Salvador", instrument="incentive", year=2015,
               sectors=["agricultura", "adaptación"], status="active", source_url="https://climate-laws.org/geographies/el-salvador", registry="climate-laws.org"),
    policy_row(id="policy:sv-cpd-index", name="El Salvador climate policies (CPD)", country="El Salvador", instrument="strategy", year=2024,
               sectors=["energía", "adaptación"], source_url="https://www.climatepolicydatabase.org/countries/el-salvador", registry="climatepolicydatabase.org"),
]


def sector_matches_challenge(sectors: list[str], challenge_id: str) -> bool:
    keys = CHALLENGE_SECTOR_MAP.get(challenge_id, set())
    blob = " ".join(sectors).lower()
    for k in keys:
        if k in blob:
            return True
    return False


def build_relations(policies: list[dict]) -> list[dict]:
    rels: list[dict] = []
    seen = set()

    for actor, pid, url, note in VERIFIED_ISSUES_POLICY:
        key = (actor, pid, "issues_policy")
        if key in seen:
            continue
        seen.add(key)
        rels.append({
            "source": actor,
            "target": pid,
            "type": "issues_policy",
            "verified": True,
            "suggested": False,
            "source_url": url,
            "notes": note,
        })

    for p in policies:
        if p["country"] not in NEXUS_COUNTRIES:
            continue
        for ch_id in CHALLENGE_SECTOR_MAP:
            if not sector_matches_challenge(p.get("sectors", []), ch_id):
                continue
            key = (p["id"], ch_id, "addresses_challenge")
            if key in seen:
                continue
            seen.add(key)
            rels.append({
                "source": p["id"],
                "target": ch_id,
                "type": "addresses_challenge",
                "verified": False,
                "suggested": True,
                "source_url": p["source_url"],
                "notes": f"Inferred from policy sectors {p.get('sectors')}",
            })

    return rels


def main():
    policies = [p for p in POLICIES if p["country"] in NEXUS_COUNTRIES]
    rels = build_relations(policies)

    actors = json.loads(ACTORS.read_text())
    gov_ids = {a["id"] for a in actors if a.get("category") == "government"}
    linked = {r["source"] for r in rels if r["type"] == "issues_policy"}
    unlinked = sorted(gov_ids - linked)

    OUT_POLICIES.write_text(json.dumps(policies, ensure_ascii=False, indent=2) + "\n")
    OUT_RELS.write_text(json.dumps(rels, ensure_ascii=False, indent=2) + "\n")

    stats = {
        "policies_by_country": dict(Counter(p["country"] for p in policies)),
        "policies_by_instrument": dict(Counter(p["instrument"] for p in policies)),
        "relations_by_type": dict(Counter(r["type"] for r in rels)),
        "issues_policy_verified": sum(1 for r in rels if r["type"] == "issues_policy" and r["verified"]),
        "addresses_challenge_suggested": sum(1 for r in rels if r["type"] == "addresses_challenge"),
        "gov_actors_total": len(gov_ids),
        "gov_actors_with_issues_policy": len(linked & gov_ids),
        "gov_actors_unlinked": unlinked,
    }
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
