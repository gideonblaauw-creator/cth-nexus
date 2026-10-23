# Colombia ecosystem actor list (v1)

Draft for Gideon's review. Categories mirror **Peru** `actors.json` taxonomy. 
Existing map actors (`co-*` ids) are included; **no** changes to `static/` data in this PR.

## Category summary

| Category | UI label (ES / EN) | Peru count (PE) | Colombia count (this doc) | Shortfall |
| --- | --- | ---: | ---: | --- |
| `corporate` | Corporativo / Corporate | 84 | 10 | — |
| `government` | Gobierno / Government | 36 | 10 | — |
| `accelerator` | Aceleradora / Accelerator | 32 | 10 | — |
| `international` | Internacional / International | 26 | 10 | — |
| `ngo_foundation` | ONG / NGO | 23 | 10 | — |
| `academia` | Academia / Academia | 23 | 10 | — |
| `funder` | Fondo / Funder | 23 | 9 | — |
| `finance` | Finanzas / Finance | 14 | 10 | — |
| `chamber` | Cámara / Chamber | 9 | 10 | — |
| `policy` | Policy (instrument) / Policy | 8 | 10 | — |
| `media` | Medios / Media | 4 | 10 | — |

**Total actors:** 109 across 11 categories (`startup` omitted — covered elsewhere in the map).

### Shortfalls

None for included categories. `startup` excluded by review; `funder` held at 9 rows (ANI entry removed — not a Colombian science-funding agency).

## UI label map (from `static/ecosystem/ecosystem.mjs`)

| Key | ES | EN |
| --- | --- | --- |
| government | Gobierno | Government |
| accelerator | Aceleradora | Accelerator |
| international | Internacional | International |
| funder | Fondo | Funder |
| ngo_foundation | ONG | NGO |
| academia | Academia | Academia |
| corporate | Corporativo | Corporate |
| finance | Finanzas | Finance |
| chamber | Cámara | Chamber |
| media | Medios | Media |

(Policy nodes in Peru use category `policy`; UI falls back to raw key.)

## corporate — Corporativo / Corporate

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| Alpina | Sopó | https://www.alpina.com/ | Dairy and food company with national production footprint. | https://www.alpina.com/ | `co-alpina` |
| Alquería | Bogotá | https://www.alqueria.com.co/ | Food and beverages corporate group. | https://www.alqueria.com.co/ | `co-alqueria` |
| Celsia | Medellín | https://www.celsia.com/ | Power utility investing in renewables and grid services. | https://www.celsia.com/ | `co-celsia` |
| EPM | Medellín | https://www.epm.com.co/ | Multi-utility (energy, water, telecom) with clean-energy portfolio. | https://www.epm.com.co/ | `co-epm` |
| Enel Colombia | Bogotá | https://www.enel.com.co/ | Electric utility operating generation, distribution and renewable projects. | https://www.enel.com.co/ | `co-enel-colombia` |
| GEB (Grupo Energía Bogotá) | Bogotá | https://www.geb.com.co/ | Energy holding (transmission, generation, distribution, gas). | https://www.geb.com.co/ | `co-geb-grupo-energia-bogota` |
| Grupo Nutresa | Medellín | https://www.gruponutresa.com/ | Food corporate group with sustainability and climate reporting. | https://www.gruponutresa.com/ | `co-grupo-nutresa` |
| ISA | Medellín | https://www.isa.co/ | Energy and infrastructure group (transmission, toll roads, telecom). | https://www.isa.co/ | `co-isa` |
| Juan Valdez | Bogotá | https://www.juanvaldez.com/ | Colombian coffee brand and retail chain. | https://www.juanvaldez.com/ | `co-juan-valdez` |
| Promigas | Barranquilla | https://www.promigas.com/ | Natural-gas transmission and energy solutions company. | https://www.promigas.com/ | `co-promigas` |

## government — Gobierno / Government

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| MinEnergía | Bogotá | https://www.minenergia.gov.co/ | National ministry for mining and energy policy. | https://www.minenergia.gov.co/ | `co-minenergia` |
| CREG | Bogotá | https://www.creg.gov.co/ | Energy and gas regulatory commission. | https://www.creg.gov.co/ | `co-creg` |
| UPME | Bogotá | https://www1.upme.gov.co/ | Mining and energy planning unit. | https://www1.upme.gov.co/ | `co-upme` |
| IPSE | Bogotá | https://www.ipse.gov.co/ | Institute for planning and promotion of energy solutions in non-interconnected zones. | https://www.ipse.gov.co/ | `co-ipse` |
| MinAmbiente | Bogotá | https://www.minambiente.gov.co/ | National environment ministry; leads climate policy and SISCLIMA. | https://www.minambiente.gov.co/organigrama-minambiente/ | — |
| ANLA | Bogotá | https://www.anla.gov.co/ | National environmental licensing authority. | https://www.anla.gov.co/nosotros/institucional/somos-anla | — |
| IDEAM | Bogotá | https://www.ideam.gov.co/ | Hydrology, meteorology and environmental studies institute. | https://www.anla.gov.co/administrativa-y-financiera/talento-humano/directorio-entidades-sector-ambiente | — |
| Parques Nacionales Naturales de Colombia | Bogotá | https://www.parquesnacionales.gov.co/ | Public agency managing Colombia's protected areas system (SINAP). | https://www.anla.gov.co/administrativa-y-financiera/talento-humano/directorio-entidades-sector-ambiente | — |
| DNP | Bogotá | https://www.dnp.gov.co/ | National Planning Department; coordinates long-term development and climate planning. | https://www.dnp.gov.co/ | — |
| MinCiencias | Bogotá | https://minciencias.gov.co/ | Science ministry funding R&D and innovation for sustainable development. | https://minciencias.gov.co/ | — |

## accelerator — Aceleradora / Accelerator

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| iNNpulsa Colombia | Bogotá | https://www.innpulsacolombia.com/ | National entrepreneurship and innovation agency (ALDEA, productivity programs). | https://www.innpulsacolombia.com/nosotros/ | — |
| HubBOG | Bogotá | https://www.hubbog.com/ | Bogotá innovation campus and accelerator for digital startups. | https://www.hubbog.com/conectemonos | — |
| Ruta N | Medellín | https://rutanmedellin.org/ | Medellín STI corporation: startup acceleration and open innovation. | https://rutanmedellin.org/en/ | — |
| Connect Bogotá Región | Bogotá | https://www.connectbogota.org/ | Regional innovation network; Springboard and open-innovation programs. | https://www.connectbogota.org/ecosistema/soy-emprendedor | — |
| APPS.CO | Bogotá | https://www.apps.co/portal/ | MinTIC digital entrepreneurship program operated with iNNpulsa. | https://www.apps.co/portal/ | — |
| NIDO (Distrito de Innovación Valle) | Cali | https://distritovalle.com/ | Valle del Cauca incubation, acceleration and expansion platform. | https://www.valledelcauca.gov.co/publicaciones/82445/nido-iniciara-con-mas-de-30-emprendedores-que-seran-los-beneficiados-en-tres-programas-incubacion-aceleracion-y-expansion/ | — |
| Wayra Hispam (Colombia hub) | Bogotá | https://hispam.wayra.com/ | Telefónica open innovation and corporate venture platform active in Colombia. | https://hispam.wayra.com/news/wayra-hispam-y-su-apuesta-por-los-emprendimientos-del-valle-del-cauca-colombia | — |
| Socialab Colombia | Bogotá | https://colombia.socialab.com/ | Open innovation and impact entrepreneurship programs with corporates and territories. | https://colombia.socialab.com/ | — |
| Fondo Emprender (SENA) | Bogotá | https://www.innovamos.gov.co/ | National entrepreneurship fund with innovation and digital-industry calls. | https://www.innovamos.gov.co/sites/default/content/files/000222/11051_tr_conv_119_industrias_digitales.pdf | — |
| Colombia Potencia Digital – Emprendimiento Digital | Bogotá | https://www.mintic.gov.co/ | MinTIC–iNNpulsa program accelerating digital ventures nationwide. | https://www.mintic.gov.co/portal/715/w3-article-383162.html | — |

## international — Internacional / International

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| GCF – Green Climate Fund | Incheon | https://www.greenclimate.fund/ | Multilateral climate fund financing mitigation and adaptation (Colombia portfolio). | https://www.worldwildlife.org/our-work/funds/wwf-and-gcf/projects/heritage-colombia-heco/ | `co-gcf-green-climate-fund` |
| CIF – Climate Investment Funds | Washington | https://www.climateinvestmentfunds.org/ | Multilateral climate investment funds active in Colombia energy and forest programs. | https://www.climateinvestmentfunds.org/ | `co-cif-climate-investment-funds` |
| PNUD Colombia | Bogotá | https://www.undp.org/es/colombia | UNDP country office on climate adaptation, low-emissions capacity and territorial resilience. | https://www.undp.org/es/colombia/projects/construccion-capacidades-bajas-emisiones-colombia | — |
| ONU Colombia | Bogotá | https://colombia.un.org/ | United Nations country team coordinating SDG and climate cooperation. | https://colombia.un.org/ | — |
| Banco Mundial – Colombia | Bogotá | https://www.worldbank.org/ext/en/country/colombia | World Bank Group country program (climate, Amazon, disaster risk). | https://www.worldbank.org/ext/en/country/colombia | — |
| BID – Colombia | Bogotá | https://www.iadb.org/es/colombia | Inter-American Development Bank country office. | https://www.iadb.org/es/colombia | — |
| IFC Colombia | Bogotá | https://www.ifc.org/ | IFC private-sector climate and infrastructure finance in Colombia. | https://www.ifc.org/ | — |
| CAF – Banco de Desarrollo de América Latina | Bogotá | https://www.caf.com/ | Development bank financing sustainable infrastructure and climate projects. | https://www.caf.com/ | — |
| GEF – Global Environment Facility | Washington | https://www.thegef.org/ | Global environment fund channelled via agencies for Colombia Amazon and adaptation projects. | https://www.worldbank.org/en/programs/amazon-sustainable-landscapes-program/partners | — |
| WWF Colombia (GCF accredited entity role) | Bogotá | https://www.wwf.org.co/ | Conservation NGO serving as executing partner on GCF landscape programs. | https://www.worldwildlife.org/news/stories/wwf-celebrates-launch-of-gcf-project-in-colombia/ | — |

## ngo_foundation — ONG / NGO

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| WWF Colombia | Bogotá | https://www.wwf.org.co/ | Conservation NGO working on climate, Amazon and freshwater. | https://www.wwf.org.co/ | — |
| Fundación Natura Colombia | Bogotá | https://natura.org.co/ | Foundation on biodiversity, climate and CarbonoCero compensation program. | https://natura.org.co/que-hacemos/programas/carbonocero/ | — |
| Conservation International Colombia | Bogotá | https://www.conservation.org.co/ | NGO on nature-based solutions and territorial conservation. | https://www.conservation.org.co/ | — |
| Fundación Gaia Amazonas | Bogotá | https://gaiaamazonas.org/ | NGO supporting indigenous governance and Amazon conservation. | https://gaiaamazonas.org/ | — |
| Fundación Humedales | Bogotá | https://fundacionhumedales.org/ | Participatory wetlands and biodiversity conservation NGO. | https://fundacionhumedales.org/nosotros/ | — |
| ProAves | Bogotá | https://www.proaves.org/ | Bird conservation NGO protecting key ecosystems and climate-relevant forests. | https://www.proaves.org/ | — |
| Fundación Mario Santo Domingo | Barranquilla | https://www.fundacionmariosantodomingo.org/ | Foundation on social and environmental development in Caribbean region. | https://www.fundacionmariosantodomingo.org/ | — |
| Fundación Bolívar Davivienda | Bogotá | https://www.fundacionbolivardavivienda.org/ | Corporate foundation on education, entrepreneurship and environment. | https://www.fundacionbolivardavivienda.org/ | — |
| Fundación Grupo Argos | Medellín | https://www.fundaciongrupoargos.org/ | Foundation on habitat, water and climate adaptation in territories. | https://www.fundaciongrupoargos.org/ | — |
| Fundación Selva | Bogotá | https://selva.org.co/ | NGO supporting Amazon conservation and indigenous territorial governance. | https://selva.org.co/ | — |

## academia — Academia / Academia

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| Universidad de los Andes | Bogotá | https://uniandes.edu.co/ | University sustainability program and carbon-neutrality roadmap. | https://sostenibilidad.uniandes.edu.co/programa-ambiental | — |
| Universidad Nacional de Colombia | Bogotá | https://unal.edu.co/ | Public research university with environmental and climate research institutes. | https://unal.edu.co/ | — |
| Universidad EIA | Envigado | https://www.eia.edu.co/ | Engineering university with institutional sustainability and GreenMetric participation. | https://www.eia.edu.co/orientacion-de-sostenibilidad/ | — |
| Universidad de Antioquia | Medellín | https://www.udea.edu.co/ | Public university with research on environment, energy and territory. | https://www.udea.edu.co/ | — |
| Universidad del Valle | Cali | https://www.univalle.edu.co/ | Public university with climate and sustainability research centers. | https://www.univalle.edu.co/ | — |
| Pontificia Universidad Javeriana | Bogotá | https://www.javeriana.edu.co/ | University with environmental engineering and climate policy research. | https://www.javeriana.edu.co/ | — |
| Universidad EAFIT | Medellín | https://www.eafit.edu.co/ | University with energy, sustainability and innovation programs. | https://www.eafit.edu.co/ | — |
| Universidad Industrial de Santander | Bucaramanga | https://www.uis.edu.co/ | Public university with engineering and environmental research. | https://www.uis.edu.co/ | — |
| Universidad del Rosario | Bogotá | https://www.urosario.edu.co/ | University with environmental law and climate governance research. | https://www.urosario.edu.co/ | — |
| Instituto de Investigación de Recursos Biológicos Alexander von Humboldt | Bogotá | https://www.humboldt.org.co/ | Public research institute on biodiversity and ecosystem services for climate policy. | https://www.anla.gov.co/administrativa-y-financiera/talento-humano/directorio-entidades-sector-ambiente | — |

## funder — Fondo / Funder

**Count:** 9 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| FENOGE | Bogotá | https://fenoge.gov.co/ | Non-conventional energy and energy-efficiency fund under MinEnergía. | https://fenoge.gov.co/quienes-somos/ | `co-fenoge` |
| Fondo Patrimonio Natural | Bogotá | https://www.patrimonionatural.org.co/ | Endowment fund for protected areas and biodiversity finance. | https://www.patrimonionatural.org.co/ | — |
| Bancóldex Capital (LP investments) | Bogotá | https://www.bancoldex.com/inversion-en-fondos | Bancóldex program investing as LP in PE/VC funds including cleantech. | https://www.bancoldex.com/inversion-en-fondos | — |
| FCP Bancóldex Capital Fondo de Fondos | Bogotá | https://fiducoldex.com.co/fondo-de-fondos | Fund-of-funds vehicle managed by Bancóldex for venture and PE. | https://fiducoldex.com.co/fondo-de-fondos | — |
| Findeter | Bogotá | https://findeter.gov.co/ | Territorial development bank financing sustainable infrastructure. | https://findeter.gov.co/ | — |
| Adaptation Fund (Colombia projects) | Washington | https://www.adaptation-fund.org/ | Multilateral fund supporting Colombia adaptation (e.g. La Mojana). | https://www.adaptation-undp.org/projects/scaling-climate-resilient-water-management-practices-vulnerable-communities-la-mojana-0 | — |
| Global Environment Facility (Colombia) | Washington | https://www.thegef.org/ | GEF grants for Amazon and climate projects in Colombia. | https://www.worldbank.org/en/programs/amazon-sustainable-landscapes-program/partners | — |
| Green Climate Fund (Colombia portfolio) | Incheon | https://www.greenclimate.fund/ | GCF finance for Colombian landscape and resilience programs. | https://www.worldwildlife.org/our-work/funds/wwf-and-gcf/projects/heritage-colombia-heco/ | `co-gcf-green-climate-fund` |
| Climate Investment Funds (Colombia) | Washington | https://www.climateinvestmentfunds.org/ | CIF programs supporting clean energy and climate resilience. | https://www.climateinvestmentfunds.org/ | `co-cif-climate-investment-funds` |

## finance — Finanzas / Finance

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| Bancóldex | Bogotá | https://www.bancoldex.com/ | Export and development bank; green and MSME credit lines. | https://www.bancoldex.com/ | `co-bancoldex` |
| Bancolombia | Medellín | https://www.bancolombia.com/ | Commercial bank with sustainable finance and green bond programs. | https://www.bancolombia.com/ | — |
| Banco Agrario de Colombia | Bogotá | https://www.bancoagrario.gov.co/ | Public agricultural development bank. | https://www.bancoagrario.gov.co/ | — |
| Finagro | Bogotá | https://www.finagro.com.co/ | Agricultural credit guarantee fund. | https://www.finagro.com.co/ | — |
| Findeter | Bogotá | https://findeter.gov.co/ | Development finance for territories and sustainable infrastructure. | https://findeter.gov.co/ | — |
| Bolsa de Valores de Colombia (BVC) | Bogotá | https://www.bvc.com.co/ | Stock exchange listing green bonds and sustainable issuers. | https://www.bvc.com.co/ | — |
| Davivienda | Bogotá | https://www.davivienda.com/ | Bank with sustainability-linked lending and green products. | https://www.davivienda.com/ | — |
| Banca de las Oportunidades | Bogotá | https://www.bancadelasoportunidades.gov.co/ | Public program expanding access to finance for vulnerable populations. | https://www.bancadelasoportunidades.gov.co/ | — |
| Banco de Bogotá (Grupo Aval) | Bogotá | https://www.bancodebogota.com/ | Commercial bank financing corporates and sustainability projects. | https://www.bancodebogota.com/ | — |
| Fiducoldex | Bogotá | https://fiducoldex.com.co/ | Trust company administering Bancóldex fund vehicles. | https://fiducoldex.com.co/ | — |

## chamber — Cámara / Chamber

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| Cámara de Comercio de Bogotá | Bogotá | https://www.ccb.org.co/ | Bogotá chamber: business registry, productivity and sustainability services. | https://www.ccb.org.co/ | — |
| Cámara de Comercio de Medellín para Antioquia | Medellín | https://www.camaramedellin.com.co/ | Antioquia chamber supporting innovation and competitiveness. | https://www.camaramedellin.com.co/ | — |
| Cámara de Comercio de Cali | Cali | https://www.ccc.org.co/ | Valle chamber with innovation and market-access services. | https://www.ccc.org.co/ | — |
| Confecámaras | Bogotá | https://confecamaras.org.co/ | National federation of Colombia's 58 chambers of commerce. | https://confecamaras.org.co/conozca-la-red-de-camaras-de-comercio/ | — |
| Cámara de Comercio de Barranquilla | Barranquilla | https://www.camarabaq.org.co/ | Caribbean regional chamber. | https://confecamaras.org.co/conozca-la-red-de-camaras-de-comercio/ | — |
| Cámara de Comercio de Bucaramanga | Bucaramanga | https://www.camaradirecta.com/ | Santander chamber. | https://confecamaras.org.co/conozca-la-red-de-camaras-de-comercio/ | — |
| Cámara de Comercio de Cartagena | Cartagena | https://www.camaracartagena.org.co/ | Bolívar coastal chamber. | https://confecamaras.org.co/conozca-la-red-de-camaras-de-comercio/ | — |
| Cámara de Comercio de Pereira | Pereira | https://www.camaradecomerciopereira.org.co/ | Risaralda coffee-region chamber. | https://confecamaras.org.co/conozca-la-red-de-camaras-de-comercio/ | — |
| Cámara de Comercio de Manizales por Caldas | Manizales | https://www.ccmpc.org.co/ | Caldas chamber. | https://confecamaras.org.co/conozca-la-red-de-camaras-de-comercio/ | — |
| Cámara de Comercio de Cúcuta | Cúcuta | https://www.camaracucuta.org.co/ | Norte de Santander border chamber. | https://confecamaras.org.co/conozca-la-red-de-camaras-de-comercio/ | — |

## policy — Policy (instrument) / Policy

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| Ley 2169 de 2021 (carbono neutralidad y resiliencia) | Bogotá | https://www.minambiente.gov.co/ | Framework law for carbon neutrality, climate resilience and low-carbon development. | https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=119745 | — |
| NDC Colombia (actualización 2020) | Bogotá | https://www.minambiente.gov.co/cambio-climatico-y-gestion-del-riesgo/documentos-oficiales-contribuciones-nacionalmente-determinadas/ | Nationally determined contribution: mitigation, adaptation and means of implementation. | https://www.minambiente.gov.co/cambio-climatico-y-gestion-del-riesgo/documentos-oficiales-contribuciones-nacionalmente-determinadas/ | — |
| Programa Nacional de Carbono Neutralidad y Resiliencia Climática | Bogotá | https://carbononeutral.minambiente.gov.co/ | National program for GHG reduction and adaptive capacity (NDC/Ley 2169). | https://carbononeutral.minambiente.gov.co/ | — |
| SISCLIMA – Sistema Nacional de Cambio Climático | Bogotá | https://www.minambiente.gov.co/cambio-climatico-y-gestion-del-riesgo/sistema-nacional-de-cambio-climatico-sisclima/ | National climate governance system coordinating public and private actors. | https://www.minambiente.gov.co/cambio-climatico-y-gestion-del-riesgo/sistema-nacional-de-cambio-climatico-sisclima/ | — |
| Estrategia Colombia Carbono Neutral 2050 (E2050) | Bogotá | https://www.minambiente.gov.co/ | Long-term low-emissions development strategy aligned with Paris Agreement. | https://carbononeutral.minambiente.gov.co/ | — |
| Taxonomía verde Colombia (MinHacienda / UVT) | Bogotá | https://www.minhacienda.gov.co/ | Green taxonomy defining eligible sustainable economic activities. | https://www.minhacienda.gov.co/ | — |
| Resolución CREG 174/2021 (autogeneración solar) | Bogotá | https://www.creg.gov.co/ | Grid rules enabling distributed solar self-generation and connection. | https://www.creg.gov.co/ | — |
| Resolución UPME 203/2020 (autogeneración) | Bogotá | https://www1.upme.gov.co/ | Technical regulation for small-scale renewable self-generation. | https://www1.upme.gov.co/ | — |
| Política Nacional de Gestión del Riesgo de Desastres | Bogotá | https://www.gestiondelriesgo.gov.co/ | Disaster risk policy linked to climate adaptation. | https://www.gestiondelriesgo.gov.co/ | — |
| Plan Nacional de Adaptación al Cambio Climático (PNACC) | Bogotá | https://www.minambiente.gov.co/ | National adaptation planning instrument under MinAmbiente. | https://www.minambiente.gov.co/cambio-climatico-y-gestion-del-riesgo/sistema-nacional-de-cambio-climatico-sisclima/ | — |

## media — Medios / Media

**Count:** 10 actors

| Name | City | Website | Role (one line) | Source | Map id |
| --- | --- | --- | --- | --- | --- |
| Semana Sostenible | Bogotá | https://www.semana.com/sostenible/ | Digital sustainability and climate coverage (Grupo Semana). | https://www.semana.com/sostenible/ | — |
| Portafolio | Bogotá | https://www.portafolio.co/ | Business and economy news including energy transition. | https://www.portafolio.co/ | — |
| La República | Bogotá | https://www.larepublica.co/ | Business newspaper covering green finance and policy. | https://www.larepublica.co/ | — |
| Forbes Colombia | Bogotá | https://forbes.co/ | Business media featuring innovation and sustainability leaders. | https://forbes.co/ | — |
| El Espectador | Bogotá | https://www.elespectador.com/ | National newspaper with environment and climate desk. | https://www.elespectador.com/ | — |
| Valora Analitik | Bogotá | https://www.valoraanalitik.com/ | Financial and economic analysis including energy markets. | https://www.valoraanalitik.com/ | — |
| Dinero | Bogotá | https://www.dinero.com/ | Business magazine on companies, markets and policy. | https://www.dinero.com/ | — |
| Blu Radio | Bogotá | https://www.bluradio.com/ | News radio with national economy and environment coverage. | https://www.bluradio.com/ | — |
| RCN Radio Noticias | Bogotá | https://www.noticiasrcn.com/ | National news network covering climate and infrastructure. | https://www.noticiasrcn.com/ | — |
| Energía Estratégica | Bogotá | https://www.energiaestrategica.com/ | Specialized media on renewables and energy transition in LATAM. | https://www.energiaestrategica.com/ | — |

---

*Generated for ecosystem mapping review. Verify URLs periodically; policy rows are legal instruments, not organizations.*
