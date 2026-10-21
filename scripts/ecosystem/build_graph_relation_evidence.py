#!/usr/bin/env python3
"""Validate curated graph_relation_evidence entries (verbatim quotes + naming)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from relation_source_fetch import (
    challenge_topic_in_evidence,
    fetch_body,
    label_matches_text,
    quote_in_body,
)

ROOT = Path(__file__).resolve().parents[2]
ACTORS_PATH = ROOT / "static/ecosystem/data/actors.json"
OUT_PATH = ROOT / "ops/ecosystem/graph_relation_evidence.json"

PRODUCE_NEWS = (
    "https://www.gob.pe/institucion/produce/noticias/"
    "648295-incubadoras-y-aceleradoras-de-negocios-fortalecidas-por-proinnovate-"
    "impulsaron-el-despegue-comercial-e-internacionalizacion-de-startups"
)
FENOGE = "https://fenoge.gov.co/preguntas-frecuentes/"
PROINNOVATE_PDF = (
    "https://cambioclimatico.proinnovate.gob.pe/wp-content/uploads/2024/11/"
    "Directorio-Web-Incubadoras-y-Aceleradoras-Red-ProInnovate-2024_-1.pdf"
)

COFUND = (
    "Gracias al cofinanciamiento y acompañamiento técnico del programa ProInnóvate, "
    "del Ministerio de la Producción, las incubadoras y aceleradoras de negocios, "
    "USIL Ventures y Emprende UP, impulsaron el despegue comercial y la "
    "internacionalización de emprendimientos innovadores y dinámicos."
)
FENOGE_IPSE = (
    "¿Cuáles son los mecanismos para presentar las propuestas al FENOGE? "
    "1. De forma directa: Ante el IPSE o la UPME, según corresponda para planes, "
    "programas o proyectos de personas jurídicas."
)
FENOGE_UPME = (
    "De forma directa: Ante el IPSE o la UPME, según corresponda para planes, "
    "programas o proyectos de personas jurídicas."
)

RELATIONS: list[dict[str, str]] = [
    {
        "source": "pe-proinnovate-startup-peru",
        "target": "pe-emprende-up-climatech-rein-hub-peru",
        "type": "cofunds",
        "source_url": PRODUCE_NEWS,
        "source_title": "Noticias PRODUCE — incubadoras ProInnóvate",
        "evidence": COFUND,
    },
    {
        "source": "pe-proinnovate-startup-peru",
        "target": "pe-usil-ventures",
        "type": "cofunds",
        "source_url": PRODUCE_NEWS,
        "source_title": "Noticias PRODUCE — incubadoras ProInnóvate",
        "evidence": COFUND,
    },
    {
        "source": "co-fenoge",
        "target": "co-ipse",
        "type": "funds_layer",
        "source_url": FENOGE,
        "source_title": "FENOGE — Preguntas frecuentes",
        "evidence": FENOGE_IPSE,
    },
    {
        "source": "co-upme",
        "target": "co-ipse",
        "type": "regulates_layer",
        "source_url": FENOGE,
        "source_title": "FENOGE — Preguntas frecuentes",
        "evidence": FENOGE_UPME,
    },
    {
        "source": "pe-produce-ministerio-de-la-produccion",
        "target": "pe-proinnovate-startup-peru",
        "type": "runs_program",
        "source_url": "https://www.gob.pe/proinnovate",
        "source_title": "ProInnóvate — Gob.pe",
        "evidence": "Resolución de Dirección Ejecutiva N.° 388-2026-PRODUCE/PROINNÓVATE",
    },
    {
        "source": "pe-universidad-del-pacifico",
        "target": "pe-emprende-up-climatech-rein-hub-peru",
        "type": "hosts",
        "source_url": "https://emprendeup.pe/climatech-impulsando-soluciones-para-un-mundo-sostenible/",
        "source_title": "Emprende UP — ClimaTech",
        "evidence": (
            "El lunes 21 de abril de 2025, la Universidad del Pacífico fue el escenario del "
            "lanzamiento de ClimaTech , una plataforma de Emprende UP dedicada a impulsar "
            "soluciones innovadoras frente al cambio climático."
        ),
    },
    {
        "source": "pe-universidad-peruana-cayetano-heredia",
        "target": "pe-bioincuba-upch",
        "type": "hosts",
        "source_url": "https://bioincuba.cayetano.pe/",
        "source_title": "Bioincuba UPCH",
        "evidence": (
            "Bioincuba es la incubadora de empresas de la Universidad Peruana Cayetano Heredia ."
        ),
    },
    {
        "source": "pe-pucp-pontificia-universidad-catolica-del-peru",
        "target": "pe-nexum-pucp",
        "type": "hosts",
        "source_url": PROINNOVATE_PDF,
        "source_title": "Directorio Red ProInnóvate 2024",
        "evidence": (
            "13 Nexum - Pontificia Universidad Católica del Perú Incubadora Lima "
            "cide.pucp.edu.pe/incubacion-empresas/ incubadora@pucp.edu.pe"
        ),
    },
    {
        "source": "pe-unalm-universidad-nacional-agraria-la-molina",
        "target": "pe-incubagraria-unalm",
        "type": "hosts",
        "source_url": PROINNOVATE_PDF,
        "source_title": "Directorio Red ProInnóvate 2024",
        "evidence": (
            "8 Incubagraria - Universidad Agraria La Molina Incubadora Lima "
            "incubagraria.lamolina.edu.pe/ incubagraria@lamolina.edu.pe"
        ),
    },
    {
        "source": "pe-yakufil",
        "target": "challenge:PE-2-agua",
        "type": "works_on_challenge",
        "source_url": (
            "https://www.unsa.edu.pe/yakufil-emprendimiento-unsa-que-revoluciona-el-"
            "tratamiento-de-aguas-residuales/"
        ),
        "source_title": "UNSA — Yakufil",
        "evidence": (
            "Yakufil Home, un proyecto que ha demostrado un gran potencial para la reutilización "
            "de aguas residuales en zonas urbanas, ha sido uno de los grandes ganadores del "
            "«Premio Orgullo Emprendedor 2024» en la categoría «Emprendedor Joven»."
        ),
    },
    {
        "source": "pe-ana-autoridad-nacional-del-agua",
        "target": "challenge:PE-2-agua",
        "type": "works_on_challenge",
        "source_url": "https://www.gob.pe/ana",
        "source_title": "ANA — Gob.pe",
        "evidence": (
            "ANA impulsa una alianza nacional para llevar la cultura del agua a escuelas y universidades"
        ),
    },
    {
        "source": "sv-grupo-agrisal",
        "target": "sv-snbx-sandbox",
        "type": "created",
        "source_url": "https://snbx.sv/",
        "source_title": "SNBX",
        "evidence": (
            "Somos un proyecto creado por Agrisal e INNBOX apoyados por BIDLab. Experiencia SNBX 360°"
        ),
    },
    {
        "source": "sv-grupo-ternova",
        "target": "sv-recicla503",
        "type": "runs_initiative",
        "source_url": "https://www.ternova.group/circular-solutions",
        "source_title": "Ternova — Circular Solutions",
        "evidence": (
            "Ternova trabaja en diferentes frentes de acción para aumentar su aporte a la "
            "circularidad y la sostenibilidad por medio de su iniciativa Recicla 503."
        ),
    },
    {
        "source": "pe-fundacion-bbva-microfinanzas",
        "target": "pe-financiera-confianza",
        "type": "owns",
        "source_url": "https://www.fundacionmicrofinanzasbbva.org/es/confianza",
        "source_title": "Fundación BBVA — Financiera Confianza",
        "evidence": (
            "El Gerente General de Financiera Confianza, Martín Naranjo Landerer, indicó que fiel "
            "a su misión, y como parte de la Fundación Microfinanzas BBVA, la entidad atendió"
        ),
    },
]


def validate_entry(entry: dict, actors: dict) -> str | None:
    body = fetch_body(entry["source_url"])
    ev = entry["evidence"]
    if not quote_in_body(ev, body):
        return "verbatim quote not on page"
    src = actors.get(entry["source"], {}).get("name") or entry["source"]
    if entry["type"] == "works_on_challenge":
        if not label_matches_text(body, src) or not label_matches_text(ev, src):
            return "works_on_challenge actor naming"
        if not challenge_topic_in_evidence(entry["target"], ev):
            return "works_on_challenge topic"
        return None
    tgt = actors.get(entry["target"], {}).get("name") or entry["target"]
    if not label_matches_text(ev, src) or not label_matches_text(ev, tgt):
        return "dual-actor naming in evidence"
    return None


def main() -> int:
    actors = {a["id"]: a for a in json.loads(ACTORS_PATH.read_text(encoding="utf-8"))}
    errors: list[str] = []
    for entry in RELATIONS:
        err = validate_entry(entry, actors)
        if err:
            errors.append(f"{entry['source']} -> {entry['target']} ({entry['type']}): {err}")
    if errors:
        print("build_graph_relation_evidence FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    payload = {"version": 2, "relations": RELATIONS}
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "relations": len(RELATIONS), "path": str(OUT_PATH)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
