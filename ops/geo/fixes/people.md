# CLP26 people location fixes (batch: people)

Proposed city/country fields for **CLP26 mentors** (`mentor_clp26`, 55 rows) and **jury** (`jury_clp26`, 21 rows) from [`location-gaps.csv`](../location-gaps.csv). Parent audit: PR [#86](https://github.com/gideonblaauw-creator/cth-nexus/pull/86) (`cursor/location-audit-ef81`).

## Policy applied

- Record **city + country** only (no street, no home address, no lat/lng in this file).
- Sources: **public professional** pages (employer/org site, faculty CV, public speaker/profile pages). No LinkedIn login or scraping; LinkedIn URLs from the gap export were not used as `source_url`.
- Each row has either `precision=city` with a `source_url`, or `precision=unknown` with blank city/country/source.
- CLP26 roster country strings in `mentor_cards.json` are **not** treated as verified geo without an independent public city source.

## Summary counts

| Metric | Count |
|--------|------:|
| Total rows | 76 |
| Mentors (`mentor_clp26`) | 55 |
| Jury (`jury_clp26`) | 21 |
| `precision=city` (verified) | 16 |
| `precision=unknown` | 60 |
| Mentors verified | 4 |
| Jury verified | 12 |

## Verified city (16)

| entity_type | id | name | city | country | source |
|-------------|-----|------|------|---------|--------|
| jury_clp26 | juror-1 | Eddie Ajalcriña | Lima | Peru | [redesignlab.org](https://www.redesignlab.org/) |
| jury_clp26 | juror-2 | Flora Drozak | Berlin | Germany | [Climate KIC inclusive team](https://www.climate-kic.org/programmes/climate-entrepreneurship/inclusive-climate-innovation/) |
| jury_clp26 | juror-3 | Sebastián Bustamante | Barcelona | Spain | [b2match event profile](https://www.b2match.com/e/4-basquegreentech/participants/2793637) |
| jury_clp26 | juror-5 | Lina Ospina | Bello | Colombia | [Interactuar contacto](https://www.interactuar.org.co/contacto) |
| jury_clp26 | juror-11 | Ana María Parra García | Bogotá | Colombia | [Fedepalma contacto](https://fedepalma.org/contacto-solicitudes-palmeros/) |
| jury_clp26 | juror-12 | Daniel Swift | Bogotá | Colombia | [Banco de la República Bogotá](https://www.banrep.gov.co/es/sucursal-bogota-edificio-principal) |
| jury_clp26 | juror-13 | Iván Dávila | Bogotá | Colombia | [FutureLab contacto](https://futurelab.com.co/hablemos/) |
| jury_clp26 | juror-14 | Mario Rojas | Bogotá | Colombia | [Uniandinos sede nacional](https://www.uniandinos.org.co/sede-nacional/) |
| jury_clp26 | juror-15 | Mariana Revilla Llaca | Mexico City | Mexico | [Expok News / GRG](https://www.expoknews.com/5-formas-de-impulsar-la-gestion-de-residuos-grupo-restaurantero-gigante/) |
| jury_clp26 | juror-18 | Diego Martínez de Velasco | Mexico City | Mexico | [Ongoing / Ibero author bio](https://ongoing.ibero.mx/objetivos-del-desarrollo-sostenible-en-accion-impacto-global/) |
| jury_clp26 | juror-20 | Federico Espinosa | San José | Costa Rica | [Universidad Veritas contact](https://studyabroad.veritas.cr/contact-us/) |
| jury_clp26 | juror-21 | Andrés Ortega | Bogotá | Colombia | [Externado CEE](https://www.uexternado.edu.co/centroemprendimientocee/) |
| mentor_clp26 | M045 | Carlos Jaramillo | Medellín | Colombia | [Seguros SURA términos](https://segurossura.com/co/terminos-y-condiciones/) |
| mentor_clp26 | M068 | Renzo Salas | Lima | Peru | [bsf.pe](https://bsf.pe/) |
| mentor_clp26 | mentor-10 | Daniel Alpaca | Lima | Peru | [USMP faculty CV](https://derechousmp.com/docentes/detalle_cv/detalle.php?ID=90028674) |
| mentor_clp26 | mentor-36 | Martin Dolan | Bogotá | Colombia | [Pangea profile](https://pangea.app/profile/martin-dolan) |

For org-affiliated jury/mentor rows, city reflects **affiliated organization HQ or public contact city** from the cited page; individual residence was not verified.

## Unknown (60)

No public employer site or public bio located in this pass that states a city (without using LinkedIn as source).

### Mentors (51)

- `mentor-1` Alaide Díaz
- `mentor-2` Alejandra Sierralta
- `mentor-3` Alex Kudzuma
- `mentor-4` Andrés Felipe Páez
- `mentor-5` Bernardo Joseph Trujillo León
- `mentor-6` Carlos Arango Ucros
- `M072` Carlos Fernando de la Cruz
- `mentor-9` Cinthya Sandoval Cuéllar
- `mentor-11` Diana Castrillón Gómez
- `mentor-12` Erwin Navarrete
- `mentor-13` Estela Ugalde
- `mentor-14` Felipe Hernández
- `mentor-15` Fernando Torres
- `mentor-16` Gabriela Tenaz
- `mentor-17` Genoveva Martínez
- `mentor-18` Gloria Bazán Narváez
- `mentor-19` Guillermo Nariño
- `mentor-20` Guisela Carbajal Romero
- `mentor-21` Gustavo García
- `mentor-22` Heraldo Escobar
- `mentor-23` Jhosseli García
- `mentor-24` Jorge Montenegro
- `mentor-25` José Soto
- `mentor-26` Juan Diego Loarca
- `mentor-27` Juan Sebastián Villamizar
- `mentor-28` Julián Martínez
- `mentor-29` Karol M. Garzón
- `mentor-30` Lucía Medina Capacoila
- `mentor-31` Maité Marroquín
- `mentor-32` Mario Reichert
- `mentor-33` Mario Rojas
- `mentor-34` Marisa Arias
- `mentor-35` Martha Zeledón
- `mentor-37` Marvin Luna
- `mentor-38` María Isabel Cruz López
- `mentor-39` María Juliana Pérez Vasco
- `M043` Michel Marfil Rivero
- `M069` Mitchell Lázaro
- `mentor-42` Mónica O’Connor
- `mentor-43` Osvaldo Ruiz
- `mentor-44` Paola Andrea Sánchez Gutiérrez
- `mentor-45` Patricia Carrasquilla Cortés
- `mentor-46` Patricia Melgar
- `mentor-47` Patricia Vidal
- `mentor-48` Raúl Campos
- `M074` Rubén Arias
- `mentor-51` Santiago Aristizábal
- `mentor-52` Santiago Cruz
- `mentor-53` Sebastián Martínez Pérez
- `mentor-54` Silvia López Giraldo
- `M001` Ximena Tavera

### Jury (9)

- `juror-4` Johana Figueroa
- `juror-6` Diana María Quimbay
- `juror-7` Camila Hernández Lozada
- `juror-8` Santiago Quiñones
- `juror-9` Felipe González
- `juror-10` Luis Miguel Mateus
- `juror-16` Santiago Cruz
- `juror-17` Felipe Hernández
- `juror-19` Héctor Vinicio España González

## Artifact

- [`people.csv`](./people.csv) — columns: `entity_type`, `id`, `name`, `precision`, `street_address`, `city`, `country`, `lat`, `lng`, `source_url`, `notes`
