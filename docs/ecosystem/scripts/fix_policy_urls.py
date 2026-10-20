#!/usr/bin/env python3
"""Normalize policy source_url fields to citable, stable URLs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "data/policies.json"
R = ROOT / "policy_relations.json"

policies = json.loads(P.read_text())
rels = json.loads(R.read_text())

UPDATES = {
    "policy:co-ley-2169-2021": {
        "source_url": "https://climate-laws.org/document/law-2169-2021-promoting-low-carbon-development-last-amended-by-law-2294-2023_8496",
    },
    "policy:co-ley-2099-2021": {
        "source_url": "http://secretariasenado.gov.co/senado/basedoc/ley_2099_2021.html",
    },
    "policy:co-ley-1931-2018": {
        "source_url": "http://secretariasenado.gov.co/senado/basedoc/ley_1931_2018.html",
    },
    "policy:co-ley-1715-2014": {
        "source_url": "http://secretariasenado.gov.co/senado/basedoc/ley_1715_2014.html",
    },
    "policy:co-conpes-4021-2021": {
        "source_url": "https://climate-laws.org/document/conpes-4021-of-2021_5c8e",
    },
    "policy:co-decreto-2239-zni": {
        "source_url": "https://climate-laws.org/document/decreto-2239-de-2023_9f2a",
    },
    "policy:co-ipse-programa-acceso": {
        "source_url": "https://www.ipse.gov.co/",
    },
    "policy:co-res-40295-fenoge": {
        "id": "policy:co-fenoge-decreto-1543",
        "name": "Decreto 1543/2017 — Fondo FENOGE (ERNC y eficiencia)",
        "instrument": "regulation",
        "year": 2017,
        "source_url": "https://www.minenergia.gov.co/es/misional/energia-electrica-2/fondos-especiales/fondo-de-energ%C3%ADas-no-convencionales-y-gesti%C3%B3n-eficiente-de-la-energ%C3%ADa-fenoge/",
    },
    "policy:pe-programa-bionegocios": {
        "source_url": "https://www.gob.pe/institucion/minam/campa%C3%B1as/46380-programa-para-bionegocios",
    },
    "policy:pe-programa-bosques": {
        "source_url": "https://www.gob.pe/institucion/minam/campa%C3%B1as/46379-programa-nacional-de-conservacion-de-bosques",
    },
    "policy:pe-startup-peru-clima": {
        "source_url": "https://www.gob.pe/institucion/produce/campa%C3%B1as/46381-startup-peru",
    },
    "policy:pe-ley-27270-2000": {
        "source_url": "https://leap.unep.org/en/akn/pe/act/2000/27270/spa@2000-11-08/overview",
    },
    "policy:pe-ley-28611-2005": {
        "source_url": "https://leap.unep.org/en/akn/pe/act/2005/28611/spa@2005-10-15/overview",
    },
    "policy:pe-ley-29763-2011": {
        "source_url": "https://leap.unep.org/en/akn/pe/act/2011/29763/spa@2011-07-27/overview",
    },
    "policy:pe-ley-29338-2009": {
        "source_url": "https://leap.unep.org/en/akn/pe/act/2009/29338/spa@2009-08-03/overview",
    },
    "policy:sv-ley-medio-ambiente-1998": {
        "source_url": "https://climate-laws.org/geographies/el-salvador",
    },
    "policy:sv-pncc-2017": {
        "source_url": "https://climate-laws.org/geographies/el-salvador",
    },
    "policy:sv-estrategia-ernc-2017": {
        "source_url": "https://climate-laws.org/geographies/el-salvador",
    },
    "policy:sv-linea-credito-verde": {
        "source_url": "https://www.bandesal.gob.sv/",
    },
    "policy:sv-ley-aguas-2012": {
        "source_url": "https://climate-laws.org/geographies/el-salvador",
    },
    "policy:sv-politica-bioeconomia-2022": {
        "source_url": "https://climate-laws.org/geographies/el-salvador",
    },
    "policy:sv-conamype-ley-2016": {
        "source_url": "https://www.transparencia.gob.sv/institutions/conamype/documents/338012/download",
    },
    "policy:gt-ley-proteccion-ambiental-2014": {
        "source_url": "https://climate-laws.org/geographies/guatemala",
    },
    "policy:gt-politica-ambiental-2018": {
        "source_url": "https://climate-laws.org/geographies/guatemala",
    },
    "policy:gt-ley-forestal-1996": {
        "source_url": "https://climate-laws.org/geographies/guatemala",
    },
    "policy:gt-plan-clima-2018": {
        "source_url": "https://climate-laws.org/geographies/guatemala",
    },
    "policy:gt-ley-renovables-2015": {
        "source_url": "https://climate-laws.org/geographies/guatemala",
    },
    "policy:cr-plan-descarbonizacion-2019": {
        "source_url": "https://climate-laws.org/document/decarbonisation-plan_856a",
    },
    "policy:cr-ley-7200-1990": {
        "source_url": "https://climate-laws.org/geographies/costa-rica",
    },
    "policy:cr-ley-biodiversidad-1998": {
        "source_url": "https://climate-laws.org/geographies/costa-rica",
    },
    "policy:cr-ley-gestion-residuos-2010": {
        "source_url": "https://climate-laws.org/geographies/costa-rica",
    },
    "policy:cr-taxonomia-verde-cr": {
        "source_url": "https://cambioclimatico.minae.go.cr/",
    },
}

for p in policies:
    u = UPDATES.get(p["id"])
    if not u:
        continue
    if "id" in u and u["id"] != p["id"]:
        old = p["id"]
        p["id"] = u["id"]
        for r in rels:
            if r["source"] == old:
                r["source"] = u["id"]
            if r["target"] == old:
                r["target"] = u["id"]
    p.update({k: v for k, v in u.items() if k != "id"})

by_id = {p["id"]: p for p in policies}
for r in rels:
    for pid in (r["source"], r["target"]):
        if pid in by_id and r.get("source_url") and "funcionpublica" in r["source_url"]:
            r["source_url"] = by_id[pid]["source_url"]
    if r["target"] in by_id and r["type"] in ("issues", "oversees", "implements", "runs_program", "regulates_layer"):
        r["source_url"] = by_id[r["target"]]["source_url"]
    if r["source"] in by_id and r["type"] in ("enables", "finances"):
        r["source_url"] = by_id[r["source"]]["source_url"]

P.write_text(json.dumps(policies, ensure_ascii=False, indent=2) + "\n")
R.write_text(json.dumps(rels, ensure_ascii=False, indent=2) + "\n")
print("updated", len(policies), "policies", len(rels), "relations")
