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

RELATIONS: list[dict[str, str | bool]] = [
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
    {
        "source": "pe-unmsm-universidad-nacional-mayor-de-san-marcos",
        "target": "pe-1551-unmsm",
        "type": "hosts",
        "source_url": "https://1551.unmsm.edu.pe/",
        "source_title": "https://1551.unmsm.edu.pe/",
        "evidence": (
            "1551 || Incubadora de Empresas Innovadoras [1551@unmsm.edu.pe] +(511) 619 7000 Anexo: 1841 English Version UNMSM"
        ),
    },
    {
        "source": "pe-unsm-universidad-nacional-de-san-martin",
        "target": "pe-incubadora-unsm-san-martin",
        "type": "hosts",
        "source_url": "https://bioinnova.unsm.edu.pe/",
        "source_title": "Bioinnova UNSM",
        "evidence": (
            "Campus Universitario Piso 3, Edificio de la biblioteca UNSM. Morales San Martín - Perú © BioInnova San Martín"
        ),
    },
    {
        "source": "pe-emprende-up-climatech-rein-hub-peru",
        "target": "pe-pvblic-foundation",
        "type": "partner",
        "source_url": "https://pvblic.org/rein-hubs/",
        "source_title": "https://pvblic.org/rein-hubs/",
        "evidence": (
            "evolved into REIN, a permanent, multilateral platform managed by PVBLIC Foundation in partnership with CleantechHUB,"
        ),
    },
    {
        "source": "pe-emprende-up-climatech-rein-hub-peru",
        "target": "pe-cleantechhub",
        "type": "partner",
        "source_url": "https://emprendeup.pe/climatech-impulsando-soluciones-para-un-mundo-sostenible/",
        "source_title": "Emprende UP — ClimaTech",
        "evidence": (
            "emprendimiento climático en el Perú. La iniciativa, desarrollada en alianza con ProInnóvate y CleantechHUBs , apunta a incubar startups que enfrenten el cambio climático desde la innovación."
        ),
    },
    {
        "source": "pe-minam-ministerio-del-ambiente",
        "target": "pe-programa-bosques-minam",
        "type": "runs_program",
        "source_url": "https://www.gob.pe/bosques",
        "source_title": "MINAM — Programa Bosques",
        "evidence": (
            "Jorge Luis Sáenz Rabanal asume la Coordinación Ejecutiva del Programa Bosques del MINAM"
        ),
    },
    {
        "source": "co-minenergia",
        "target": "co-ipse",
        "type": "regulates_layer",
        "source_url": (
            "https://ipse.gov.co/documento_prensa/documento/documentos_de_%20investigacion/Art%C3%ADculo%20Mundoel%C3%A9ctrico.pdf"
        ),
        "source_title": "Mundoeléctrico — marco regulatorio",
        "evidence": (
            "Ministerio de Minas y Energía (MINENERGÍA), el Instituto de Planificación y Promoción de Soluciones Energéticas para Zonas No Interconectadas (IPSE)"
        ),
    },
    {
        "source": "co-creg",
        "target": "co-ipse",
        "type": "regulates_layer",
        "source_url": (
            "https://ipse.gov.co/documento_prensa/documento/documentos_de_%20investigacion/Art%C3%ADculo%20Mundoel%C3%A9ctrico.pdf"
        ),
        "source_title": "Mundoeléctrico — marco regulatorio",
        "evidence": (
            "Instituto de Planificación y Promoción de Soluciones Energéticas para Zonas No Interconectadas (IPSE), la Unidad de Planeación Minero-Energética (UPME), la Comisión de Regulación de Energía y Gas (CREG)"
        ),
    },
    {
        "source": "pe-profonanpe",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": (
            "https://profonanpe.org.pe/proyectos/manejo-sostenible-y-restauracion-"
            "del-bosque-seco-de-la-costa-norte-del-peru-bosque-seco/"
        ),
        "source_title": "Profonanpe — Bosque Seco",
        "evidence": (
            "bosques secos de la Costa Norte del Perú, facilitando la conservación de la "
            "biodiversidad y los servicios de los ecosistemas, aumentando la resiliencia de "
            "las comunidades y sus medios de subsistencia, y apoyando al logro de la meta de "
            "neutralidad en la degradación de la tierra (LDN). Inicio: 23 de diciembre de 2022 "
            "Culminación: 19 de octubre de 2027 Financiamiento $7.493.291,00 Rol de Profonanpe"
        ),
        "verified": True,
        "date_accessed": "2026-10-22",
    },
    {
        "source": "pe-amazonia-impact-ventures",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.amazoniaimpactventures.com",
        "source_title": "https://www.amazoniaimpactventures.com",
        "evidence": (
            "Home | Amazonia Impact Ventures | Impact investing | Amazon rainforest top of page What"
        ),
    },
    {
        "source": "pe-ecoenterprises-fund",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://ecoenterprisesfund.com",
        "source_title": "https://ecoenterprisesfund.com",
        "evidence": (
            "EcoEnterprises Fund: Investing in Nature for 25 Years Biodiversity preservation and regeneration We support businesses that directly protect and restore valuable ecosystems, watersheds, and working landscapes. Through investing to transform crucial sectors such as regenerative agriculture, agro-forestry,"
        ),
    },
    {
        "source": "pe-andes-amazon-fund",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.andesamazonfund.org",
        "source_title": "https://www.andesamazonfund.org",
        "evidence": (
            "Andes Amazon Fund - Safeguarding the Most Diverse Landscapes on Earth Skip to content Menu"
        ),
    },
    {
        "source": "pe-rainforest-alliance",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.rainforest-alliance.org",
        "source_title": "https://www.rainforest-alliance.org",
        "evidence": (
            "Rainforest Alliance | Creating a Better World for People and Nature Give Our Work Our"
        ),
    },
    {
        "source": "pe-minam-ministerio-del-ambiente",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.gob.pe/bosques",
        "source_title": "MINAM — Programa Bosques",
        "evidence": (
            "MINAM invierte más de S/ 16,5 millones para impulsar la castaña y conservar los bosques de ..."
        ),
    },
    {
        "source": "pe-conservacion-amazonica-acca",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://acca.org.pe",
        "source_title": "https://acca.org.pe",
        "evidence": (
            "Conservación Regional Lomas y Desierto Costero octubre 14, 2026 Noticias Facebook Twitter Youtube Conservación Amazónica"
        ),
    },
    {
        "source": "pe-nature-services-peru",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.natureservices.net",
        "source_title": "https://www.natureservices.net",
        "evidence": (
            "competitividad y creando valor compartido mediante la conservación y restauración de ecosistemas. Nosotros Nature Services"
        ),
    },
    {
        "source": "pe-arbio",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.arbioperu.org",
        "source_title": "https://www.arbioperu.org",
        "evidence": (
            "ARBIO Perú: conservación del bosque amazónico Toggle navigation Nosotros Somos ARBIO Personas Adopta un árbol"
        ),
    },
    {
        "source": "pe-red-amazonia-que-late",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://amazoniaquelate.com",
        "source_title": "https://amazoniaquelate.com",
        "evidence": (
            "Abra Patricia Alto Nieva Hierba Buena - Allpayacu Copallín Huaylla-Belén Milpuj - La Heredad Bosque"
        ),
    },
    {
        "source": "pe-spda-sociedad-peruana-de-derecho-ambiental",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://spda.org.pe/bosques/",
        "source_title": "SPDA — Bosques",
        "evidence": (
            "Bosques - SPDA | SPDA - Sociedad Peruana de Derecho Ambiental ES EN Nosotros Línea de tiempo Nuestro Trabajo Cambio Climático Equidad y justicia ambiental Naturaleza y vida silvestre Desarrollo sostenible Impacto Noticias Historias Campañas Eventos Recursos Publicaciones Audiovisuales Podcasts Formación Transparencia Memorias SÚMATE Nosotros Línea de tiempo Nuestro Trabajo Cambio Climático Equidad y justicia ambiental Naturaleza y vida silvestre Desarrollo sostenible Impacto Noticias Historias Campañas Eventos Recursos Publicaciones Audiovisuales Podcasts Formación Transparencia Memorias SÚMATE Nosotros Línea de tiempo Nuestro Trabajo Cambio Climático Equidad y justicia ambiental Naturaleza y vida silvestre Desarrollo sostenible Impacto Noticias Historias Campañas Eventos Recursos Publicaciones Audiovisuales Podcasts Formación Transparencia Memorias ES EN SÚMATE Nuestro Trabajo Naturaleza y vida silvestre Bosques Con nuestra labor apoyamos a reducir la deforestación y degradación de los bosques del Perú peruanos con herramientas basadas en evidencia"
        ),
    },
    {
        "source": "pe-conservacion-internacional",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.conservation.org/peru",
        "source_title": "Conservación Internacional Perú",
        "evidence": (
            "y la naturaleza. En Conservación Internacional estamos convencidos que la gente que vive en los lugares con mayor diversidad biológica y cultural, como la Amazonia"
        ),
    },
    {
        "source": "pe-wwf-peru",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.wwf.org.pe",
        "source_title": "https://www.wwf.org.pe",
        "evidence": (
            "personas vivan en armonía con la naturaleza. Leer más © Daniel Martinez / WWF-Perú Amazonía"
        ),
    },
    {
        "source": "pe-the-nature-conservancy",
        "target": "challenge:PE-1-bosques",
        "type": "works_on_challenge",
        "source_url": "https://www.nature.org",
        "source_title": "https://www.nature.org",
        "evidence": (
            "English Español Show search Renew Donate Search The Nature Conservancy Look Up A bamboo forest"
        ),
    },
    {
        "source": "pe-inaigem",
        "target": "challenge:PE-2-agua",
        "type": "works_on_challenge",
        "source_url": "https://www.gob.pe/inaigem",
        "source_title": "https://www.gob.pe/inaigem",
        "evidence": (
            "a. m. Minam: INAIGEM fortalece la gestión ambiental y la protección de los recursos hídricos"
        ),
    },
    {
        "source": "pe-senamhi",
        "target": "challenge:PE-2-agua",
        "type": "works_on_challenge",
        "source_url": "https://www.gob.pe/senamhi",
        "source_title": "https://www.gob.pe/senamhi",
        "evidence": (
            "Senamhi acerca la información meteorológica a la ciudadanía en la Expo Agro Arequipa 2026 "
            "19 de octubre de 2026 - 2:20 p. m. Cambio climático podría afectar la disponibilidad de "
            "agua en la cuenca alta del río Apurímac"
        ),
    },
    {
        "source": "pe-policy-startup-peru-proinnovate",
        "target": "pe-proinnovate-startup-peru",
        "type": "administered_by",
        "source_url": "https://www.gob.pe/proinnovate",
        "source_title": "ProInnóvate — Gob.pe",
        "evidence": (
            "Programa Nacional de Innovación y Desarrollo Productivo - ProInnóvate - PROINNOVATE"
        ),
    },
    {
        "source": "pe-policy-startup-peru-proinnovate",
        "target": "pe-produce-ministerio-de-la-produccion",
        "type": "administered_by",
        "source_url": "https://www.gob.pe/proinnovate",
        "source_title": "ProInnóvate — Gob.pe",
        "evidence": "Resolución de Dirección Ejecutiva N.° 388-2026-PRODUCE/PROINNÓVATE",
    },
    {
        "source": "pe-policy-programa-bosques-minam",
        "target": "pe-minam-ministerio-del-ambiente",
        "type": "administered_by",
        "source_url": "https://www.gob.pe/bosques",
        "source_title": "MINAM — Programa Bosques",
        "evidence": (
            "Jorge Luis Sáenz Rabanal asume la Coordinación Ejecutiva del Programa Bosques del MINAM"
        ),
    },
    {
        "source": "pe-proinnovate-startup-peru",
        "target": "pe-yakusmart",
        "type": "funding",
        "source_url": (
            "https://www.gob.pe/institucion/proinnovate/noticias/"
            "1451423-startup-impulsada-por-proinnovate-optimiza-el-riego-agricola-"
            "para-incrementar-el-valor-exportable-de-las-frutas"
        ),
        "source_title": "ProInnóvate — YakuSmart optimiza el riego",
        "evidence": (
            "Con el impulso del programa ProInnóvate del Ministerio de la Producción (PRODUCE), "
            "la startup YakuSmart desarrolló y mejoró una plataforma tecnológica que ayuda a las "
            "agroexportadoras a optimizar el riego de sus cultivos y aprovechar de manera más "
            "eficiente los recursos hídricos y energéticos."
        ),
    },
    {
        "source": "pe-produce-ministerio-de-la-produccion",
        "target": "pe-yakusmart",
        "type": "funding",
        "source_url": (
            "https://www.gob.pe/institucion/proinnovate/noticias/"
            "1451423-startup-impulsada-por-proinnovate-optimiza-el-riego-agricola-"
            "para-incrementar-el-valor-exportable-de-las-frutas"
        ),
        "source_title": "ProInnóvate — YakuSmart optimiza el riego",
        "evidence": (
            "Con el impulso del programa ProInnóvate del Ministerio de la Producción (PRODUCE), "
            "la startup YakuSmart desarrolló y mejoró una plataforma tecnológica que ayuda a las "
            "agroexportadoras a optimizar el riego de sus cultivos y aprovechar de manera más "
            "eficiente los recursos hídricos y energéticos."
        ),
    },
    {
        "source": "pe-yakusmart",
        "target": "challenge:PE-2-agua",
        "type": "works_on_challenge",
        "source_url": (
            "https://www.gob.pe/institucion/proinnovate/noticias/"
            "1451423-startup-impulsada-por-proinnovate-optimiza-el-riego-agricola-"
            "para-incrementar-el-valor-exportable-de-las-frutas"
        ),
        "source_title": "ProInnóvate — YakuSmart optimiza el riego",
        "evidence": (
            "la startup YakuSmart desarrolló y mejoró una plataforma tecnológica que ayuda a las "
            "agroexportadoras a optimizar el riego de sus cultivos y aprovechar de manera más "
            "eficiente los recursos hídricos y energéticos."
        ),
    },
    {
        "source": "pe-jaku-emprende-unsa-arequipa",
        "target": "pe-yakufil",
        "type": "incubated",
        "source_url": (
            "https://www.unsa.edu.pe/emprendedores-de-la-unsa-ganan-concurso-y-"
            "recibiran-s-60-000-por-parte-de-startup-peru-9g/"
        ),
        "source_title": "UNSA — Yakufil, Startup Perú 9G",
        "evidence": (
            "Jóvenes representantes de los proyectos Space School, AVIRU y YAKUFIL, que recibieron "
            "acompañamiento de la Incubadora de Negocios JAKU Emprende UNSA, recibirán un fondo de "
            "hasta S/ 60 000. Esta importante subvención les permitirá seguir con el desarrollo de "
            "sus propuestas. Los tres proyectos fueron ganadores en la categoría Emprendimientos "
            "Innovadores en el concurso organizado por la iniciativa Startup Perú 9G, del Programa "
            "Nacional PROINNOVATE"
        ),
    },
    {
        "source": "pe-proinnovate-startup-peru",
        "target": "pe-yakufil",
        "type": "funding",
        "source_url": (
            "https://www.unsa.edu.pe/emprendedores-de-la-unsa-ganan-concurso-y-"
            "recibiran-s-60-000-por-parte-de-startup-peru-9g/"
        ),
        "source_title": "UNSA — Yakufil, Startup Perú 9G",
        "evidence": (
            "Jóvenes representantes de los proyectos Space School, AVIRU y YAKUFIL, que recibieron "
            "acompañamiento de la Incubadora de Negocios JAKU Emprende UNSA, recibirán un fondo de "
            "hasta S/ 60 000. Esta importante subvención les permitirá seguir con el desarrollo de "
            "sus propuestas. Los tres proyectos fueron ganadores en la categoría Emprendimientos "
            "Innovadores en el concurso organizado por la iniciativa Startup Perú 9G, del Programa "
            "Nacional PROINNOVATE"
        ),
    },
    {
        "source": "pe-uqhu",
        "target": "challenge:PE-2-agua",
        "type": "works_on_challenge",
        "source_url": "https://www.unasam.edu.pe/noticia/y0zRtTQ1BgA=",
        "source_title": "UNASAM — startup Uqhu",
        "evidence": (
            "La startup que presentaron, llamada \"Uqhu\", surgió de la investigación en el "
            "tratamiento de aguas residuales domesticas (ARD) mediante humedales construidos de tipo francés"
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
