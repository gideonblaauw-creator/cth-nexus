#!/usr/bin/env python3
"""Insert Wave 1 round-1 batch 1–2 Colombia corporates into actors.raw.json + geocode-by-id."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "static" / "ecosystem" / "data" / "actors.raw.json"
GEO_BY_ID = ROOT / "ops" / "ecosystem" / "geocode-by-id.json"
SOURCE = "Datalab Nexus Wave 1 Colombia (Move 4)"
UA = "CleantechHUB-Nexus-Ecosystem/1.0 (ops@cleantechhub.net)"

WAVE1 = [
    {
        "id": "co-isa",
        "name": "ISA",
        "website": "https://www.isa.co",
        "city": "Medellín",
        "challenges": ["ENE"],
        "card": {
            "ecosystem_role": "Transmisión eléctrica y conexión de mercados energéticos.",
            "description": "Interconexión Eléctrica S.A. (ISA) opera infraestructura de transmisión y conexión eléctrica en Colombia y la región.",
        },
        "linkedin": "https://www.linkedin.com/company/isaconexiones/",
        "geo_seed": {
            "precision": "address",
            "address": "Calle 12 sur No. 18-168",
            "city": "Medellín",
            "country": "Colombia",
            "source_url": "https://www.isa.co/es/",
        },
    },
    {
        "id": "co-geb-grupo-energia-bogota",
        "name": "GEB (Grupo Energía Bogotá)",
        "website": "https://www.grupoenergiabogota.com",
        "city": "Bogotá",
        "challenges": ["ENE"],
        "card": {
            "ecosystem_role": "Grupo integrado de energía, gas y conectividad.",
            "description": "Grupo Energía Bogotá (GEB) agrupa negocios de transmisión, gas natural y telecomunicaciones en Colombia y Latinoamérica.",
        },
        "linkedin": "https://www.linkedin.com/company/grupo-energia-bogota",
        "geo_seed": {
            "precision": "address",
            "address": "Carrera 9 No. 73-44, piso 6",
            "city": "Bogotá",
            "country": "Colombia",
            "source_url": "https://www.grupoenergiabogota.com",
        },
    },
    {
        "id": "co-enel-colombia",
        "name": "Enel Colombia",
        "website": "https://www.enel.com.co",
        "city": "Bogotá",
        "challenges": ["ENE"],
        "card": {
            "ecosystem_role": "Generación, distribución y soluciones energéticas.",
            "description": "Enel Colombia participa en generación y comercialización de energía y servicios eléctricos para clientes residenciales y empresariales.",
        },
        "geo_seed": {
            "precision": "address",
            "address": "Carrera 13A No. 93-66, piso 4",
            "city": "Bogotá",
            "country": "Colombia",
            "source_url": "https://www.enel.com.co/es/contactanos.html",
        },
    },
    {
        "id": "co-celsia",
        "name": "Celsia",
        "website": "https://www.celsia.com",
        "city": "Medellín",
        "challenges": ["ENE"],
        "card": {
            "ecosystem_role": "Generación y comercialización de energía eléctrica.",
            "description": "Celsia S.A. genera y comercializa energía eléctrica en Colombia, Panamá y Costa Rica.",
        },
        "linkedin": "https://www.linkedin.com/company/celsiaenergia",
        "geo_seed": {
            "precision": "address",
            "address": "Carrera 48 No. 26-85, piso 1",
            "city": "Medellín",
            "country": "Colombia",
            "source_url": "https://www.celsia.com/es/contactenos/",
        },
    },
    {
        "id": "co-epm",
        "name": "EPM",
        "website": "https://www.epm.com.co",
        "city": "Medellín",
        "challenges": ["ENE"],
        "card": {
            "ecosystem_role": "Empresa de servicios públicos multiutilities.",
            "description": "Empresas Públicas de Medellín (EPM) presta energía, agua, gas y telecomunicaciones en Colombia.",
        },
        "geo_seed": {
            "precision": "address",
            "address": "Carrera 58 No. 42-125",
            "city": "Medellín",
            "country": "Colombia",
            "source_url": "https://www.epm.com.co",
        },
    },
    {
        "id": "co-promigas",
        "name": "Promigas",
        "website": "https://www.promigas.com",
        "city": "Barranquilla",
        "challenges": ["ENE"],
        "card": {
            "ecosystem_role": "Transporte y distribución de gas natural.",
            "description": "Promigas S.A. E.S.P. opera infraestructura de gas natural en la costa Caribe colombiana.",
        },
        "geo_seed": {
            "precision": "address",
            "address": "Calle 66 No. 67-123",
            "city": "Barranquilla",
            "country": "Colombia",
            "source_url": "https://www.promigas.com/es/contacto/",
        },
    },
    {
        "id": "co-alqueria",
        "name": "Alquería",
        "website": "https://www.alqueria.com.co",
        "city": "Bogotá",
        "challenges": ["AGR"],
        "card": {
            "ecosystem_role": "Empresa de alimentos y lácteos.",
            "description": "Alquería produce y comercializa lácteos y alimentos para el mercado colombiano.",
        },
        "linkedin": "https://www.linkedin.com/company/alquer-a-colombia/",
        "geo_seed": {"precision": "country", "country": "Colombia"},
    },
    {
        "id": "co-grupo-nutresa",
        "name": "Grupo Nutresa",
        "website": "https://www.gruponutresa.com",
        "city": "Medellín",
        "challenges": ["AGR"],
        "card": {
            "ecosystem_role": "Conglomerado de alimentos procesados.",
            "description": "Grupo Nutresa agrupa marcas de alimentos procesados con operación en Colombia y exportación regional.",
        },
        "geo_seed": {
            "precision": "address",
            "address": "Carrera 43A No. 1A sur-143",
            "city": "Medellín",
            "country": "Colombia",
            "source_url": "https://gruponutresa.com/es/contacto/",
        },
    },
    {
        "id": "co-juan-valdez",
        "name": "Juan Valdez",
        "website": "https://www.juanvaldez.com",
        "city": "Bogotá",
        "challenges": ["AGR"],
        "card": {
            "ecosystem_role": "Marca de café colombiano y retail especializado.",
            "description": "Juan Valdez comercializa café colombiano y opera tiendas de la marca en Colombia y el exterior.",
        },
        "linkedin": "https://www.linkedin.com/company/juan-valdez-cafe/",
        "geo_seed": {
            "precision": "address",
            "address": "Calle 73 No. 8-13",
            "city": "Bogotá",
            "country": "Colombia",
            "source_url": "https://www.juanvaldez.com/contacto",
        },
    },
    {
        "id": "co-alpina",
        "name": "Alpina",
        "website": "https://www.alpina.com",
        "city": "Sopó",
        "challenges": ["AGR"],
        "card": {
            "ecosystem_role": "Empresa de alimentos y bebidas.",
            "description": "Alpina Productos Alimenticios produce lácteos y alimentos con operación en Colombia.",
        },
        "linkedin": "https://www.linkedin.com/company/alpina/",
        "geo_seed": {
            "precision": "address",
            "address": "Carrera 4 Bis No. 9-24",
            "city": "Sopó",
            "country": "Colombia",
            "source_url": "https://www.alpina.com/co/",
        },
    },
]


def nominatim(street: str, city: str) -> tuple[float, float] | None:
    q = f"{street}, {city}, Colombia"
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1, "countrycodes": "co"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        rows = json.loads(resp.read())
    if not rows:
        return None
    return round(float(rows[0]["lat"]), 6), round(float(rows[0]["lon"]), 6)


def actor_row(spec: dict) -> dict:
    row = {
        "id": spec["id"],
        "name": spec["name"],
        "type": "org",
        "category": "corporate",
        "country": "Colombia",
        "city": spec["city"],
        "website": spec["website"],
        "page": None,
        "notes": "Wave 1 round 1 — Datalab Nexus Colombia map (Move 4)",
        "challenges": spec.get("challenges", []),
        "sector": "private",
        "source": SOURCE,
        "geo": {
            "lat": None,
            "lng": None,
            "address": None,
            "city": None,
            "country": "Colombia",
            "precision": "country",
            "source_url": None,
        },
        "nexus": {"card_slug": None},
        "card": spec["card"],
    }
    if spec.get("linkedin"):
        row["linkedin"] = spec["linkedin"]
    return row


def main() -> None:
    actors = json.loads(RAW.read_text(encoding="utf-8"))
    by_id = {a["id"]: a for a in actors}
    geo_blob = json.loads(GEO_BY_ID.read_text(encoding="utf-8"))

    new_rows: list[dict] = []
    for spec in WAVE1:
        if spec["id"] in by_id:
            print(f"skip existing {spec['id']}")
            continue
        row = actor_row(spec)
        new_rows.append(row)
        by_id[spec["id"]] = row

        seed = spec["geo_seed"]
        if seed.get("precision") == "address":
            coords = nominatim(seed["address"], seed["city"])
            g = {
                **seed,
                "lat": coords[0] if coords else None,
                "lng": coords[1] if coords else None,
            }
            if not coords:
                g = {
                    "lat": None,
                    "lng": None,
                    "address": None,
                    "city": None,
                    "country": "Colombia",
                    "precision": "country",
                    "source_url": None,
                    "location_note": "Street on source page; geocode pending.",
                }
            geo_blob[spec["id"]] = g
        else:
            geo_blob[spec["id"]] = {
                "lat": None,
                "lng": None,
                "address": None,
                "city": None,
                "country": "Colombia",
                "precision": "country",
                "source_url": None,
            }

    for a in actors:
        if a.get("id") == "co-ipse" and a.get("source") == "Mapa de Actores Perú 2026":
            a["source"] = SOURCE

    # Insert wave-1 block after co-ipse for readability
    out: list[dict] = []
    wave_ids = {s["id"] for s in WAVE1}
    wave_rows = sorted(
        [by_id[i] for i in wave_ids if i in by_id and i in {r["id"] for r in new_rows}],
        key=lambda x: x["id"],
    )
    inserted = False
    for a in actors:
        if a["id"] in wave_ids:
            continue
        out.append(a)
        if a.get("id") == "co-ipse" and not inserted:
            out.extend(wave_rows)
            inserted = True
    if not inserted:
        out.extend(wave_rows)

    RAW.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    GEO_BY_ID.write_text(json.dumps(geo_blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(wave_rows)} Wave 1 actors; total actors {len(out)}")


if __name__ == "__main__":
    main()
