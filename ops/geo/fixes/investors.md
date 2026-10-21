# Investor CRM HQ location fixes (batch: investors)

Generated: 2026-10-21 (re-verified with page fetch + evidence).
Source gaps: `ops/geo/location-gaps.csv` (529 `investor_crm` rows).

## Summary

| Metric | Count |
|--------|------:|
| Total rows | 529 |
| `precision=city` (city + country + evidence on cited page) | 257 |
| `precision=unknown` | 272 |
| Prior pass rows with homepage-only inferred note | 520 |

## Method (this revision)

- Fetched each CRM `source_url` plus `/contact`, `/about`, `/imprint`, and similar paths.
- Accepted `precision=city` only when a **city** and **country** appear on a fetched page (JSON-LD, `<address>`, contact meta, or HQ/contact/footer text) with an **evidence** snippet, or via **Wikidata P159** when P856 matches the fund domain.
- `source_url` is the **exact page** where the evidence snippet was found (not a generic homepage default).
- If no qualifying city on fetched pages/registry: `precision=unknown` (blank city/country/evidence).
- No street addresses or coordinates (`street_address`, `lat`, `lng` remain blank).

## Unknowns

**272** entities remain `precision=unknown` (official site did not expose a verifiable HQ city in fetched pages and no matching Wikidata P159 with domain match).

- `959` — 10 investment (https://10investments.nl)
- `841` — 1955 Capital (https://1955.capital)
- `814` — 2C Ventures (https://www.2cventures.eu)
- `860` — 2degrees (https://www.weare2degrees.com)
- `859` — 7percent ventures (https://www.7pc.vc)
- `987` — AALchemy ventures //n Andrey Kostyuk (https://aalchemy.eu)
- `147` — ABN Amro Sustainable Impact Fund (https://www.abnamro.nl/en/commercialbanking/corporates-institutionals/products/expand-your-business/private-equity/sustainable-impact-fund/index.html)
- `829` — Achmea Impact Fund (https://www.achmeainnovationfund.nl/en)
- `148` — Achmea Impact Ventures (https://www.achmea-impact.ventures)
- `799` — Achmea Ventures (https://www.achmea-impact.ventures)
- `71` — Acumen Trellis (https://acumen.org)
- `111` — AEBAN (https://aeban.es)
- `73` — Afrilabs (https://www.afrilabs.com)
- `75` — Agfunder (https://agfunder.com/about)
- `76` — Algebra Ventures (https://algebraventures.com)
- `77` — Alpha Mundi (https://www.alphamundigroup.com)
- `614` — Alphamundi (https://www.alphamundigroup.com)
- `589` — alter equity (https://www.alter-equity.com)
- `682` — AMS Institute (https://www.ams-institute.org)
- `113` — Ananda VC (https://ananda.vc)
- `863` — Andera (https://www.anderapartners.com/en)
- `617` — Angel Hub (https://www.angelhub.mx)
- `618` — Angel Investment Network (Colombia) (https://www.angelinvestmentnetwork.com.co)
- `195` — Anthos Fund & Asset Management (https://www.anthosam.com)
- `839` — Applied Ventures (https://www.appliedmaterials.com/us/en/applied-ventures.html)
- `621` — Arrebol (https://arrebolcap.com)
- `590` — asc impact GmbH (https://asc-impact.com/en)
- `858` — At One Ventures (https://www.atoneventures.com)
- `78` — Attijari Capital Management and Holdagro (https://www.fm6i.ma/fonds-thematiques-et-sectoriels/)
- `3` — Avenue (https://www.avenuecapital.com)
- … plus 242 more (see CSV).

## Changed rows vs prior `investors.csv` (inferred pass)

**413** rows changed city/country and/or precision after evidence-based re-verification.

| id | name | before | after |
|----|------|--------|-------|
| 959 | 10 investment | Amsterdam, Netherlands (city) | (unknown) |
| 841 | 1955 Capital | San Mateo, United States (city) | (unknown) |
| 814 | 2C Ventures | Madrid, Spain (city) | (unknown) |
| 860 | 2degrees | London, United Kingdom (city) | (unknown) |
| 852 | 500 startups | San Francisco, United States (city) | Mountain View, United States (city) |
| 859 | 7percent ventures | Amsterdam, Netherlands (city) | (unknown) |
| 987 | AALchemy ventures //n Andrey Kostyuk | Luxembourg, Luxembourg (city) | (unknown) |
| 147 | ABN Amro Sustainable Impact Fund | Amsterdam, Netherlands (city) | (unknown) |
| 829 | Achmea Impact Fund | Zeist, Netherlands (city) | (unknown) |
| 148 | Achmea Impact Ventures | Zeist, Netherlands (city) | (unknown) |
| 799 | Achmea Ventures | Zeist, Netherlands (city) | (unknown) |
| 185 | Acumen | New York, United States (city) | New York City, United States (city) |
| 71 | Acumen Trellis | New York, United States (city) | (unknown) |
| 111 | AEBAN | Madrid, Spain (city) | (unknown) |
| 175 | AEGON | The Hague, Netherlands (city) | Cedar Rapids, United States (city) |
| 73 | Afrilabs | Nairobi, Kenya (city) | (unknown) |
| 74 | Agdevco | London, United Kingdom (city) | London, United States (city) |
| 75 | Agfunder | San Francisco, United States (city) | (unknown) |
| 76 | Algebra Ventures | Cairo, Egypt (city) | (unknown) |
| 77 | Alpha Mundi | Zurich, Switzerland (city) | (unknown) |
| 614 | Alphamundi | Zurich, Switzerland (city) | (unknown) |
| 589 | alter equity | Paris, France (city) | (unknown) |
| 682 | AMS Institute | Amsterdam, Netherlands (city) | (unknown) |
| 113 | Ananda VC | Berlin, Germany (city) | (unknown) |
| 863 | Andera | Paris, France (city) | (unknown) |
| 617 | Angel Hub | Mexico City, Mexico (city) | (unknown) |
| 618 | Angel Investment Network (Colombia) | Bogotá, Colombia (city) | (unknown) |
| 195 | Anthos Fund & Asset Management | Amsterdam, Netherlands (city) | (unknown) |
| 1 | APG pension fund | Heerlen, Netherlands (city) | New York, Hong Kong (city) |
| 839 | Applied Ventures | Santa Clara, United States (city) | (unknown) |
| 621 | Arrebol | Bogotá, Colombia (city) | (unknown) |
| 590 | asc impact GmbH | Frankfurt am Main, Germany (city) | (unknown) |
| 206 | Astanor | Brussels, Belgium (city) | Paris, France (city) |
| 858 | At One Ventures | San Francisco, United States (city) | (unknown) |
| 78 | Attijari Capital Management and Holdagro | Casablanca, Morocco (city) | (unknown) |
| 3 | Avenue | New York, United States (city) | (unknown) |
| 182 | AXA Investment Managers | Paris, France (city) | (unknown) |
| 210 | Baillie Gifford | Edinburgh, United Kingdom (city) | Edinburgh, United States (city) |
| 5 | Barn Invest | São Paulo, Brazil (city) | Sao Paulo, Brazil (city) |
| 864 | Basinghall Partners | London, United Kingdom (city) | (unknown) |
| 114 | BCombinator | Barcelona, Spain (city) | (unknown) |
| 683 | Behold | San Francisco, United States (city) | (unknown) |
| 866 | Berkeley SkyDeck Fund | Berkeley, United States (city) | (unknown) |
| 6 | Better Ventures | Oakland, United States (city) | (unknown) |
| 79 | Beyond Capital Ventures | Bethesda, United States (city) | (unknown) |
| 217 | BlackRock | New York, United States (city) | Amsterdam, Netherlands (city) |
| 840 | Blitzscaling Ventures | San Francisco, United States (city) | Palo Alto, United States (city) |
| 867 | Bloom Equity | San Francisco, United States (city) | (unknown) |
| 869 | Blue Ashva | Gurugram, India (city) | Mumbai, India (city) |
| 7 | Blue Ashva Capital | Gurugram, India (city) | Mumbai, India (city) |
| 220 | Blue Earth Capital AG | Baar, Switzerland (city) | Baar-Zug, Switzerland (city) |
| 80 | Blue Haven Initiative | Cambridge, United States (city) | (unknown) |
| 9 | Blue like an orange | Paris, France (city) | (unknown) |
| 685 | BOM | Eindhoven, Netherlands (city) | Tilburg, Netherlands (city) |
| 1003 | Bonventures | Berlin, Germany (city) | (unknown) |
| 4 | BP Ventures | London, United Kingdom (city) | (unknown) |
| 686 | Brabant Startup Fonds | Breda, Netherlands (city) | (unknown) |
| 871 | Braemer Energy Ventures | Boston, United States (city) | (unknown) |
| 227 | Bridges Fund Management | London, United Kingdom (city) | (unknown) |
| 688 | Brightlands Venture Partners | Maastricht, Netherlands (city) | (unknown) |
| 228 | British International Investment | London, United Kingdom (city) | (unknown) |
| 10 | British International Investment (BII) | London, United Kingdom (city) | (unknown) |
| 81 | Calvert Capital | Bethesda, United States (city) | (unknown) |
| 232 | Calvert Impact Capital | Bethesda, United States (city) | (unknown) |
| 873 | Cantos | San Francisco, United States (city) | (unknown) |
| 236 | Capricorn Investment Group | Palo Alto, United States (city) | New York, United States (city) |
| 12 | Carao Ventures | San José, Costa Rica (city) | (unknown) |
| 879 | Caterpillar Ventures | Irving, United States (city) | (unknown) |
| 880 | Charles River Ventures | Palo Alto, United States (city) | San Francisco, Canada (city) |
| 877 | Chevron Technology Ventures | Houston, United States (city) | (unknown) |
| 878 | Citizen Capital | Paris, France (city) | (unknown) |
| 881 | Climactic VC | London, United Kingdom (city) | San Francisco, United States (city) |
| 973 | Climate Market Place | London, United Kingdom (city) | (unknown) |
| 886 | Congruent VC | San Francisco, United States (city) | San Francisco, Canada (city) |
| 982 | Core Angel Climate | Lisbon, Portugal (city) | (unknown) |
| 599 | Core Angels Pacific | Lisbon, Portugal (city) | (unknown) |
| 117 | Core Climate Angels | Lisbon, Portugal (city) | (unknown) |
| 821 | CoreAngels | Lisbon, Portugal (city) | (unknown) |
| 629 | Corekees | Amsterdam, Netherlands (city) | (unknown) |
| 693 | Corporate Venturing Network | London, United Kingdom (city) | (unknown) |
| 600 | Dadneo | Madrid, Spain (city) | (unknown) |
| 632 | Dalus | Mexico City, Mexico (city) | (unknown) |
| 633 | Danta | Guatemala City, Guatemala (city) | (unknown) |
| 16 | DEG | Cologne, Germany (city) | (unknown) |
| 17 | DEG (Deutsche Investition- und Entwicklungsgesellschaft) | Cologne, Germany (city) | (unknown) |
| 264 | DEG- Deutsche Investition- und Entwicklungsgesellschaft mbH | Cologne, Germany (city) | (unknown) |
| 694 | DELA | Eindhoven, Netherlands (city) | Antwerp, Belgium (city) |
| 889 | Diffusion Capital Partners | Amsterdam, Netherlands (city) | (unknown) |
| 695 | Diverse Leaders in Tech | London, United Kingdom (city) | Amsterdam, United States (city) |
| 84 | DOEN | Amsterdam, Netherlands (city) | (unknown) |
| 949 | DOW | Midland, United States (city) | (unknown) |
| 963 | Dozen investment | Tokyo, Japan (city) | (unknown) |
| 631 | DRk Foundation | Atlanta, United States (city) | Menlo Park, United States (city) |
| 893 | Dutch Mezzanine Fund II | Amsterdam, Netherlands (city) | Frankfurt am Main, Germany (city) |
| 964 | DWR Eco | Paris, France (city) | Berlin, Germany (city) |
| 636 | Eco Enterprises Fund | Alexandria, United States (city) | Washington, United States (city) |
| 285 | EcoEnterprises Fund | Alexandria, United States (city) | Washington, United States (city) |
| 286 | Ecosystem Integrity Fund | San Francisco, United States (city) | (unknown) |
| 894 | EDF Pulse Ventures | Paris, France (city) | (unknown) |
| 591 | eha Impact Ventures | Amsterdam, Netherlands (city) | (unknown) |
| 86 | ELEA | Zurich, Switzerland (city) | (unknown) |
| 895 | Elemental Excelerator | Honolulu, United States (city) | (unknown) |
| 288 | Elevar Equity | Seattle, United States (city) | (unknown) |
| 837 | Energy Innovation Capital | San Francisco, United States (city) | (unknown) |
| 637 | Epic Angels | Singapore, Singapore (city) | (unknown) |
| 122 | EsadeBan | Barcelona, Spain (city) | (unknown) |
| 292 | European Bank for Reconstruction and Development (EBRD), The | London, United Kingdom (city) | (unknown) |
| 25 | European Investment Bank | Luxembourg, Luxembourg (city) | (unknown) |
| 592 | evolutiq impact advisory | Zurich, Switzerland (city) | (unknown) |
| 896 | Fair Capital Partners | Utrecht, Netherlands (city) | (unknown) |
| 699 | Fem-Start | Amsterdam, Netherlands (city) | Den Haag, Netherlands (city) |
| 304 | Fidante Partners | Sydney, Australia (city) | (unknown) |
| 27 | Finance in Motion | Frankfurt, Germany (city) | (unknown) |
| 29 | Finn Fund | Helsinki, Finland (city) | Helsinki, United States (city) |
| 306 | Finnfund | Helsinki, Finland (city) | Helsinki, United States (city) |
| 297 | FINVIA Holding GmbH | Munich, Germany (city) | (unknown) |
| 903 | First Bridge Ventures | Paris, France (city) | (unknown) |
| 905 | Floodgate | Menlo Park, United States (city) | (unknown) |
| 26 | FMO | The Hague, Netherlands (city) | Nairobi, Netherlands (city) |
| 308 | Fondaction | Paris, France (city) | Montreal, United States (city) |
| 640 | Fondo Impacta | Santiago, Chile (city) | (unknown) |
| 311 | Ford Foundation | Luxembourg, Luxembourg (city) | Johannesburg, South Africa (city) |
| 298 | FOUNT | Brussels, Belgium (city) | (unknown) |
| 312 | Franklin Templeton | United States, United States (city) | San Mateo, United States (city) |
| 299 | FS Impact Finance | Frankfurt, Germany (city) | Frankfurt am Main, Germany (city) |
| 642 | Fundación Bancolombia | Medellín, Colombia (city) | (unknown) |
| 315 | Funds for Good | Luxembourg, Luxembourg (city) | (unknown) |
| 601 | Fundsurfer | London, United Kingdom (city) | (unknown) |
| 30 | Future Energy Ventures | Tokyo, Japan (city) | Seattle, United States (city) |
| 321 | Galvanize Climate Solutions | Washington, United States (city) | (unknown) |
| 31 | GAWA | Madrid, ES (city) | Madrid, Spain (city) |
| 317 | GAWA Capital | Madrid, ES (city) | Madrid, Spain (city) |
| 907 | Generate Capital | New York, United States (city) | San Francisco, Canada (city) |
| 32 | GetInvest | Nairobi, Kenya (city) | (unknown) |
| 323 | Giving Women | London, United Kingdom (city) | (unknown) |
| 318 | GK Ventures | Seoul, South Korea (city) | (unknown) |
| 319 | GLIN Impact Capital | Luxembourg, Luxembourg (city) | (unknown) |
| 993 | Global Angel Club | Luxembourg, Luxembourg (city) | (unknown) |
| 124 | GoldenEgg | Amsterdam, Netherlands (city) | Amersfoort, Netherlands (city) |
| 328 | Golding Capital Partners GmbH | Bavaria, Germany (city) | Munich, Germany (city) |
| 92 | Goodwell | Amsterdam, Netherlands (city) | Johannesburg, South Africa (city) |
| 329 | Goodwell Investments | Amsterdam, Netherlands (city) | Johannesburg, South Africa (city) |
| 91 | GoParity | Lisbon, PT (city) | Lisbon, Portugal (city) |
| 331 | Green Artha | Mumbai, India (city) | (unknown) |
| 126 | Green Impact Investing | Amsterdam, Netherlands (city) | (unknown) |
| 988 | Green Impact Investing // GreenChoice | Amsterdam, Netherlands (city) | (unknown) |
| 703 | Green Whale | Amsterdam, Netherlands (city) | (unknown) |
| 320 | GSG | The Hague, Netherlands (city) | London, United Kingdom (city) |
| 850 | Hitachi Ventues | Tokyo, Japan (city) | Berlin, Germany (city) |
| 706 | Horizon Flevoland | Amsterdam, Netherlands (city) | (unknown) |
| 593 | iConnections | New York, United States (city) | (unknown) |
| 34 | IDB | India, India (city) | (unknown) |
| 966 | IESE | Munich, Germany (city) | Sao Paulo, Germany (city) |
| 340 | IFU | Copenhagen, Denmark (city) | Johannesburg, South Africa (city) |
| 801 | Impact City | The Hague, Netherlands (city) | (unknown) |
| 157 | Impact City Amsterdam | The Hague, Netherlands (city) | (unknown) |
| 35 | Impact Fund Denmark | Copenhagen, Denmark (city) | Johannesburg, South Africa (city) |
| 342 | IMPact SGR | Milan, Italy (city) | (unknown) |
| 93 | Impact Shakers | Brussels, Belgium (city) | (unknown) |
| 350 | ImpactCity The Hague | The Hague, Netherlands (city) | (unknown) |
| 94 | Incofin | Brussels, Belgium (city) | (unknown) |
| 352 | Incofin Investment Management | Brussels, Belgium (city) | (unknown) |
| 970 | infiniumpartners | Dubai, United Arab Emirates (city) | (unknown) |
| 708 | Inkef | Amsterdam, Netherlands (city) | (unknown) |
| 38 | InnoEnergy | Paris, France (city) | Amsterdam, Netherlands (city) |
| 356 | Innpact S.A. | Luxembourg, Luxembourg (city) | (unknown) |
| 910 | Insight Venture Partners | San Francisco, United States (city) | New York, United States (city) |
| 357 | Insitor Partners Pte. Ltd. | Luxembourg, Luxembourg (city) | (unknown) |
| 358 | Inspired Evolution | Cape Town, South Africa (city) | (unknown) |
| 361 | Invesco | Luxembourg, Luxembourg (city) | Atlanta, United States (city) |
| 711 | Invest International | Amsterdam, Netherlands (city) | Den Haag, Netherlands (city) |
| 345 | ISF Advisers | Washington, United States (city) | (unknown) |
| 594 | iungo capital | Nairobi, Kenya (city) | (unknown) |
| 363 | Japan Social Innovation & Investment Foundation (SIIF) | Tokyo, Japan (city) | (unknown) |
| 364 | John D. and Catherine T. MacArthur Foundation, The | Chicago, United States (city) | New Delhi, India (city) |
| 365 | Jonathan Rose Companies | Lisbon, Portugal (city) | New York, United States (city) |
| 815 | K Fund | Madrid, Spain (city) | (unknown) |
| 370 | Katapult Ocean | Oslo, NO (city) | Oslo, Norway (city) |
| 371 | KawiSafi Ventures | Nairobi, Kenya (city) | New York, United States (city) |
| 40 | KFund | Madrid, Spain (city) | (unknown) |
| 39 | KFW | Frankfurt, Germany (city) | Berlin, Germany (city) |
| 716 | Kickstart AI | Amsterdam, Netherlands (city) | (unknown) |
| 375 | Kohlberg Kravis Roberts & Co. L.P. | Singapore, Singapore (city) | New York, United States (city) |
| 824 | KOIS | Paris, France (city) | (unknown) |
| 96 | KOIS Invest | Paris, France (city) | (unknown) |
| 159 | Kosmos Impact | Amsterdam, Netherlands (city) | (unknown) |
| 376 | Kresge Foundation, The | Luxembourg, Luxembourg (city) | (unknown) |
| 131 | Lanai VC | Barcelona, Spain (city) | (unknown) |
| 912 | LDV Capital | Luxembourg, Luxembourg (city) | (unknown) |
| 41 | LeapFrog Investments | Amsterdam, Netherlands (city) | (unknown) |
| 380 | Learn Capital | Austin, United States (city) | (unknown) |
| 381 | Lemma FX | Sydney, AU (city) | Sydney, Australia (city) |
| 379 | LGT Capital Partners | Pfäffikon, Switzerland (city) | (unknown) |
| 97 | LGT Capital Partners (Lightrock link) | London, United Kingdom (city) | Utrecht, Netherlands (city) |
| 383 | Liberty Group | United States, United States (city) | (unknown) |
| 913 | LifeX Ventures | Helsinki, Finland (city) | (unknown) |
| 42 | Light Ray Ventures | Paris, France (city) | New York, United States (city) |
| 384 | Lightrock | London, United Kingdom (city) | Utrecht, Netherlands (city) |
| 43 | Lightrock (LGT Group) | London, United Kingdom (city) | Utrecht, Netherlands (city) |
| 132 | Lumolabs | Eindhoven, Netherlands (city) | (unknown) |
| 914 | Lux Capital | New York, United States (city) | New York City, United States (city) |
| 392 | Maj Invest | London, United Kingdom (city) | (unknown) |
| 134 | Marbella Tech Angels | Madrid, Spain (city) | (unknown) |
| 916 | Matterwave Ventures | Munich, Germany (city) | Barcelona, Spain (city) |
| 386 | MCE Social Capital | Luxembourg, Luxembourg (city) | San Francisco, United States (city) |
| 394 | Mennonite Economic Development Associates (MEDA) | Washington, United States (city) | Nairobi, Kenya (city) |
| 388 | MENTERRA VENTURE ADVISORS | Bengaluru, India (city) | (unknown) |
| 655 | Mercy Corps | Portland, United States (city) | The Hague, Netherlands (city) |
| 99 | MercyCorps | Portland, United States (city) | (unknown) |
| 44 | MGM Sustainable Energy Fund II | São Paulo, Brazil (city) | (unknown) |
| 720 | Midpoint Brabant | Singapore, Singapore (city) | (unknown) |
| 918 | MIG Capital AG | Munich, Germany (city) | Frankfurt am Main, Germany (city) |
| 397 | Milken Institute | Toronto, Canada (city) | Toronto, South Korea (city) |
| 45 | Mirova | Paris, France (city) | Hong Kong, United States (city) |
| 400 | Mitsubishi UFJ Trust and Banking Corporation | Japan, Japan (city) | Tokyo, Japan (city) |
| 390 | MN | Amsterdam, Netherlands (city) | (unknown) |
| 133 | MVentures | Darmstadt, Germany (city) | Amsterdam, Netherlands (city) |
| 46 | NatureVest / The Nature Conservancy | Hong Kong, Hong Kong (city) | New York, Mexico (city) |
| 405 | Nawa Impact | Amsterdam, Netherlands (city) | (unknown) |
| 402 | NDPI Foundation | The Hague, Netherlands (city) | (unknown) |
| 407 | Neuberger Berman | New York, United States (city) | New York City, United States (city) |
| 921 | New Energy Capital | Helsinki, Finland (city) | (unknown) |
| 659 | New Ventures | United States, United States (city) | (unknown) |
| 411 | Nithio | Washington, United States (city) | Nairobi, United States (city) |
| 724 | NL Groeit | The Hague, Netherlands (city) | (unknown) |
| 726 | Noaber | Hilversum, Netherlands (city) | (unknown) |
| 412 | Nonprofit Finance Fund | Luxembourg, Luxembourg (city) | New York, United States (city) |
| 47 | Nordfund | Oslo, Norway (city) | (unknown) |
| 414 | Nordic Microfinance Initiative AS | Oslo, Norway (city) | Nairobi, Norway (city) |
| 854 | NPM Capital | Amsterdam, Netherlands (city) | (unknown) |
| 415 | Nuveen | New York, United States (city) | Chicago, United States (city) |
| 48 | Nuveen (TIAA) | New York, United States (city) | (unknown) |
| 416 | Nuveen, a TIAA Company | New York, United States (city) | (unknown) |
| 404 | NZ Super Fund | Copenhagen, Denmark (city) | Auckland, New Zealand (city) |
| 923 | Obvious Ventures | San Francisco, United States (city) | (unknown) |
| 420 | Octobre | Rotterdam, Netherlands (city) | Paris, France (city) |
| 845 | Octopus Ventures | London, United Kingdom (city) | (unknown) |
| 417 | OGCI Climate Investments | London, United Kingdom (city) | Houston, United Kingdom (city) |
| 418 | OGCI Climate Investments LLP | London, United Kingdom (city) | Houston, United Kingdom (city) |
| 49 | OIKO | Amersfoort, Netherlands (city) | (unknown) |
| 100 | Oiko Credit | Amersfoort, Netherlands (city) | (unknown) |
| 421 | Old Mutual Alternative Investments | Cape Town, South Africa (city) | Cape Town, United States (city) |
| 423 | Omnivore | Mumbai, India (city) | (unknown) |
| 424 | One to Watch | Utrecht, Netherlands (city) | (unknown) |
| 728 | Oost NL | Amsterdam, Netherlands (city) | (unknown) |
| 425 | Open Capital | Luxembourg, Luxembourg (city) | (unknown) |
| 426 | Open Road Alliance | Washington, United States (city) | (unknown) |
| 972 | Operator Exchange | London, United Kingdom (city) | (unknown) |
| 103 | Orange Corners | The Hague, Netherlands (city) | (unknown) |
| 428 | Orrick, Herrington & Sutcliffe LLP | London, United Kingdom (city) | Seattle, Singapore (city) |
| 429 | Overlay Capital | Dublin, Ireland (city) | Atlanta, United States (city) |
| 434 | Pangaea Ventures | Luxembourg, Luxembourg (city) | Tokyo, Japan (city) |
| 435 | Partnerships For Forests | London, United Kingdom (city) | (unknown) |
| 436 | Pathstone | New York, United States (city) | (unknown) |
| 437 | PayPal | Oslo, Norway (city) | San Jose, United States (city) |
| 438 | Pegasus 7 Ventures | Luxembourg, Luxembourg (city) | (unknown) |
| 978 | Perseo | Bilbao, Spain (city) | (unknown) |
| 50 | Persistent Energy Capital | Lagos, Nigeria (city) | (unknown) |
| 440 | Pioneers Post | London, United Kingdom (city) | London, United States (city) |
| 925 | Piva Capital | San Francisco, United States (city) | San Francisco, Canada (city) |
| 138 | Planet A | London, United Kingdom (city) | Berlin, Germany (city) |
| 826 | Planet A Ventures | London, United Kingdom (city) | Berlin, Germany (city) |
| 827 | Planet B.io | Berlin, Germany (city) | (unknown) |
| 661 | Plug N Play | Sunnyvale, United States (city) | (unknown) |
| 442 | Polestar Capital | Amsterdam, Netherlands (city) | (unknown) |
| 926 | Powerhouse Ventures | Auckland, New Zealand (city) | Oakland, United States (city) |
| 101 | Prime Coalition | Luxembourg, Luxembourg (city) | (unknown) |
| 444 | Private Financing Advisory Network | Paris, France (city) | (unknown) |
| 445 | Private Sector Foundation Uganda | Cairo, Egypt (city) | (unknown) |
| 102 | Proparco (FISEA+) | Paris, France (city) | (unknown) |
| 448 | Prudential | Newark, United States (city) | Prudential Headquarters, United States (city) |
| 449 | Prudential Financial | Newark, United States (city) | Prudential Headquarters, United States (city) |
| 450 | PureTerra Ventures | Luxembourg, Luxembourg (city) | Amsterdam, Netherlands (city) |
| 161 | PYM | Jakarta, Indonesia (city) | (unknown) |
| 605 | Qapu Ventures | Bogotá, Colombia (city) | (unknown) |
| 929 | QStone Capital | Rotterdam, Netherlands (city) | (unknown) |
| 453 | Quona Capital | Singapore, Singapore (city) | Jakarta, Brazil (city) |
| 454 | Quona Capital Management Ltd. | Singapore, Singapore (city) | Jakarta, Brazil (city) |
| 52 | Rabobank Energy | Utrecht, Netherlands (city) | (unknown) |
| 53 | Rabobank renewable energy | Utrecht, Netherlands (city) | (unknown) |
| 812 | Rabobank Start-to-Scale-up Team | Utrecht, Netherlands (city) | (unknown) |
| 455 | Rainforest Alliance | Amsterdam, Netherlands (city) | Guatemala City, Guatemala (city) |
| 456 | Rally Assets | Toronto, Canada (city) | (unknown) |
| 457 | Raskob Foundation for Catholic Activities | London, United Kingdom (city) | (unknown) |
| 460 | Realdania | Copenhagen, Denmark (city) | (unknown) |
| 461 | Red Ribbon Capital Partners | Amsterdam, Netherlands (city) | (unknown) |
| 463 | Regenerate Asset Management | London, United Kingdom (city) | London, United States (city) |
| 464 | Resonance | London, United Kingdom (city) | (unknown) |
| 465 | Rethink Capital Partners | London, United Kingdom (city) | (unknown) |
| 466 | Rhia Ventures | New York, United States (city) | (unknown) |
| 735 | ROM Utrecht Region | Utrecht, Netherlands (city) | (unknown) |
| 468 | Root Capital | Massachusetts, United States (city) | Cambridge, United States (city) |
| 484 | Sahel Capital Agribusiness Managers Limited | Dublin, Ireland (city) | Dublin, United Kingdom (city) |
| 934 | Sail Capital | Chicago, United States (city) | (unknown) |
| 485 | Sail Ventures | Amsterdam, Netherlands (city) | (unknown) |
| 664 | Salkantay | Lima, Peru (city) | (unknown) |
| 487 | Sanlam Investments | Johannesburg, South Africa (city) | (unknown) |
| 104 | Satgana | Luxembourg, Luxembourg (city) | (unknown) |
| 105 | Saviu VC | Paris, France (city) | (unknown) |
| 56 | Schneider Electric Energy Access | Rueil-Malmaison, France (city) | (unknown) |
| 935 | Seabird Ventures | London, United Kingdom (city) | (unknown) |
| 142 | Seedrocket | Madrid, Spain (city) | (unknown) |
| 740 | SET Ventures | Amsterdam, Netherlands (city) | (unknown) |
| 57 | Shell Ventures | London, United Kingdom (city) | (unknown) |
| 804 | Shift Invest | Amsterdam, Netherlands (city) | (unknown) |
| 936 | Shift4Good | Paris, France (city) | (unknown) |
| 974 | Shiftinvest | Amsterdam, Netherlands (city) | (unknown) |
| 794 | Ship2B | Madrid, Spain (city) | (unknown) |
| 143 | Ship2b Ventures | Barcelona, Spain (city) | (unknown) |
| 492 | Si3 | The Hague, Netherlands (city) | Rotterdam, United States (city) |
| 470 | SIDI | Paris, France (city) | Paris, United States (city) |
| 471 | SIGLO Capital Advisors AG | Zurich, Switzerland (city) | (unknown) |
| 472 | SIIF | Tokyo, Japan (city) | (unknown) |
| 495 | Silverhorn | Singapore, Singapore (city) | Jakarta, Singapore (city) |
| 494 | SilverStreet Capital | London, United Kingdom (city) | (unknown) |
| 474 | SJF Ventures | Philadelphia, United States (city) | (unknown) |
| 937 | Sofinnova Partners | London, United Kingdom (city) | London, France (city) |
| 500 | Sophora | Berlin, Germany (city) | (unknown) |
| 501 | Soros Economic Development Fund | New York, United States (city) | (unknown) |
| 938 | SOSV | Princeton, United States (city) | (unknown) |
| 939 | South Pole | Paris, France (city) | Madrid, Sweden (city) |
| 502 | Spin Ventures | Washington, United States (city) | (unknown) |
| 941 | Spring Lane Capital | New York, United States (city) | Montreal, Canada (city) |
| 504 | Squire Patton Boggs | Amsterdam, Netherlands (city) | San Francisco, Singapore (city) |
| 506 | Stardust Equity | New York, United States (city) | (unknown) |
| 507 | Startup Discovery School | Amsterdam, Netherlands (city) | (unknown) |
| 741 | Startup Utrecht | Utrecht, Netherlands (city) | (unknown) |
| 509 | Stichting SED Fund | Amsterdam, Netherlands (city) | (unknown) |
| 55 | SUMA Capital | Paris, France (city) | Milan, United States (city) |
| 59 | Summa Equity | Stockholm, Sweden (city) | (unknown) |
| 60 | SunFunder | Paris, France (city) | Hong Kong, United States (city) |
| 743 | Superconnectors | Cologne, Germany (city) | (unknown) |
| 511 | Sustainable Leaders Investment Management, Parnter firm Olduvai Capital | Amsterdam, Netherlands (city) | (unknown) |
| 942 | Sustainable Ocean Alliance | London, United Kingdom (city) | (unknown) |
| 943 | Sustainable Ventures | London, United Kingdom (city) | Cambridge, United States (city) |
| 513 | Symbiotics SA | Amsterdam, Netherlands (city) | Gurugram, South Africa (city) |
| 483 | SYSTEMIQ | London, United Kingdom (city) | (unknown) |
| 514 | T. Rowe Price | Luxembourg, Luxembourg (city) | (unknown) |
| 518 | Talanton Impact Fund | The Hague, Netherlands (city) | (unknown) |
| 519 | Tamil Nadu Shelter Fund | Mumbai, India (city) | (unknown) |
| 522 | Telos Impact srl | Paris, France (city) | Brussels, Belgium (city) |
| 523 | Temasek | Singapore, Singapore (city) | (unknown) |
| 946 | Tera Ventures | London, United Kingdom (city) | Tallinn, Estonia (city) |
| 525 | The Bridgespan Group | San Francisco, United States (city) | (unknown) |
| 528 | The Hague Business Agency | The Hague, Netherlands (city) | San Francisco, United States (city) |
| 529 | The John D. Gerhart Center for Philanthropy, Civic Engagement, and Responsible Business | New York, United States (city) | Cairo, Egypt (city) |
| 530 | The Nature Conservancy | Hong Kong, Hong Kong (city) | New York, Mexico (city) |
| 531 | The Scottish National Investment Bank | Edinburgh, United Kingdom (city) | (unknown) |
| 144 | The Sharing Group | Amsterdam, Netherlands (city) | Amsterdam, United States (city) |
| 533 | The UN Sanitation and Hygiene Fund | Melbourne, Australia (city) | (unknown) |
| 534 | The Visa Foundation | Foster City, United States (city) | (unknown) |
| 670 | The Yield Lab LATAM | São Paulo, Brazil (city) | Buenos Aires, Argentina (city) |
| 947 | Theia Finance Labs | Paris, France (city) | Berlin, Germany (city) |
| 971 | TheSharingGroup | Amsterdam, Netherlands (city) | Amsterdam, United States (city) |
| 535 | ThomasLloyd Group Ltd. | Amsterdam, Netherlands (city) | Munich, Germany (city) |
| 536 | Tideline | London, United Kingdom (city) | New York, United Kingdom (city) |
| 516 | TIIP: The Investment Integration Project | London, United Kingdom (city) | New York, United States (city) |
| 747 | TNO | Utrecht, Netherlands (city) | Utrecht, United States (city) |
| 539 | Tonbo | Amsterdam, Netherlands (city) | (unknown) |
| 541 | TortoiseEcofin | London, United Kingdom (city) | (unknown) |
| 63 | Toyota Ventures | Los Altos, United States (city) | (unknown) |
| 542 | Trade and Development Bank of Mongolia | New York, United States (city) | Ulaanbaatar, Mongolia (city) |
| 543 | Treehouse Investments, LLC | Luxembourg, Luxembourg (city) | (unknown) |
| 544 | Trimtab Impact | Luxembourg, Luxembourg (city) | (unknown) |
| 64 | Triodos | Amsterdam, Netherlands (city) | Zeist, Netherlands (city) |
| 164 | Triodos Bank | Amsterdam, Netherlands (city) | Zeist, Netherlands (city) |
| 65 | Triodos Investment Management | Zeist, Netherlands (city) | (unknown) |
| 797 | Triodos speciaal fonds | Zeist, Netherlands (city) | (unknown) |
| 545 | Triple P Advisory Pte Ltd | Singapore, Singapore (city) | (unknown) |
| 546 | Truvalu B.V. | Amsterdam, Netherlands (city) | (unknown) |
| 547 | Truvalu.enterprises Limited | Amsterdam, Netherlands (city) | (unknown) |
| 517 | TSIC | London, United Kingdom (city) | (unknown) |
| 62 | TWYNAM Earth Fund | Sydney, Australia (city) | (unknown) |
| 549 | Tyton Partners | New York, United States (city) | (unknown) |
| 550 | U.S. Impact Investing Alliance | Luxembourg, Luxembourg (city) | (unknown) |
| 551 | UBS | Zurich, Switzerland (city) | (unknown) |
| 554 | Ubuntoo | Atlanta, United States (city) | (unknown) |
| 672 | Uncompromise | San Francisco, United States (city) | (unknown) |
| 555 | United Nations | Geneva, Switzerland (city) | New York City, United States (city) |
| 948 | United Ventures | Milan, Italy (city) | (unknown) |
| 556 | Unitus Labs | Mumbai, India (city) | (unknown) |
| 833 | University of Capetown | Cape Town, South Africa (city) | (unknown) |
| 559 | Upaya Social Ventures | Luxembourg, Luxembourg (city) | (unknown) |
| 749 | Utrecht Inc | Utrecht, Netherlands (city) | (unknown) |
| 561 | Uxolo | Singapore, Singapore (city) | New York, United Kingdom (city) |
| 562 | Uxolo Development Finance | Singapore, Singapore (city) | New York, United Kingdom (city) |
| 564 | Van Lanschot Kempen | Amsterdam, Netherlands (city) | Paris, United Kingdom (city) |
| 565 | Vantain AG and Climate Fund Managers | New York, United States (city) | (unknown) |
| 950 | Vargas Holding / Altor Vargas | Stockholm, Sweden (city) | (unknown) |
| 566 | Variant Investments, LLC | Denver, United States (city) | (unknown) |
| 808 | Vattenfal | Groningen, Netherlands (city) | Stockholm, United States (city) |
| 751 | VGZ | Arnhem, Netherlands (city) | (unknown) |
| 951 | Victory Capital | Boston, United States (city) | (unknown) |
| 567 | Vidia GmbH | Paris, France (city) | Munich, Germany (city) |
| 568 | Vinci Impact and Return | Luxembourg, Luxembourg (city) | (unknown) |
| 569 | Vinte Viviendas Integrales, S.A.B. de C.V. (Vinte) | São Paulo, Brazil (city) | (unknown) |
| 570 | Visa Foundation | Foster City, United States (city) | (unknown) |
| 673 | Vista alta | Luxembourg, Luxembourg (city) | (unknown) |
| 572 | Vital Capital Fund | Luxembourg, Luxembourg (city) | (unknown) |
| 573 | Vital Strategies | New York, United States (city) | Paris, France (city) |
| 574 | Vivriti Asset Management | Chennai, IN (city) | Chennai, India (city) |
| 575 | Vivriti Asset Management Private Limited | Chennai, IN (city) | Chennai, India (city) |
| 576 | Volans | London, United Kingdom (city) | London, United States (city) |
| 577 | Vox Capital | São Paulo, Brazil (city) | São Paulo, United States (city) |
| 581 | WaterEquity | Oakland, United States (city) | (unknown) |
| 857 | Wellington | Boston, United States (city) | (unknown) |
| 68 | World Fund | Amsterdam, Netherlands (city) | Berlin, Germany (city) |
| 583 | World Vision | London, United Kingdom (city) | (unknown) |
| 584 | World Wide Fund for Nature (WWF) Zambia | Lusaka, Zambia (city) | (unknown) |
| 674 | WWF Fund | Gland, Switzerland (city) | (unknown) |
| 587 | Yunus Social Business | Berlin, Germany (city) | Bengaluru, India (city) |
| 69 | Zubi Capital | Madrid, Spain (city) | (unknown) |
| 588 | Zürcher Kantonalbank (ZKB) | Zurich, Switzerland (city) | (unknown) |

## Apply

Review `ops/geo/fixes/investors.csv` before merging into Investors CRM / geo pipeline (no deploy in this PR).
