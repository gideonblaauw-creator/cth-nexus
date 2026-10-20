#!/usr/bin/env python3
"""
tag_taxonomy.py
Classifies all CLP26 ideas against the real CTH CT Taxonomy (59 nodes,
9 sectors) and writes a ct_taxonomy tag to each BookStack page.

Usage:
  python3 -u tag_taxonomy.py \
    --bs-token-id clp26_ingest_01 \
    --bs-token-secret YOUR_SECRET \
    --anthropic-key sk-ant-... \
    [--dry-run]

Safe to re-run: overwrites any existing ct_taxonomy tag (needed because
earlier runs wrote wrong climate-theme values).
"""

import argparse
import json
import re
import time
import anthropic
import requests

# ---------------------------------------------------------------------------
# Full CTH CT Taxonomy — 59 nodes across 9 sectors
# ---------------------------------------------------------------------------
CT_TAXONOMY = {
    # AF — AFOLU (12)
    "CT-AF-001": "Sustainable Coffee Production",
    "CT-AF-002": "Coffee Supply Chain Traceability",
    "CT-AF-003": "Cacao Agroforestry Systems",
    "CT-AF-004": "Silvopastoral Systems",
    "CT-AF-005": "Community Reforestation (REDD+)",
    "CT-AF-006": "Sustainable Fishing & Blue Economy",
    "CT-AF-007": "Precision Agriculture & Digital Agri",
    "CT-AF-008": "Payments for Ecosystem Services (PES)",
    "CT-AF-009": "Bioeconomy & Non-Timber Forest Products",
    "CT-AF-010": "Smallholder Climate Adaptation (AFOLU)",
    "CT-AF-011": "Natural Rubber Agroforestry",
    "CT-AF-012": "Organic & Regenerative Agriculture",
    # BU — Buildings & Infrastructure (5)
    "CT-BU-001": "Green Building Design & Certification",
    "CT-BU-002": "Building Energy Retrofit",
    "CT-BU-003": "Affordable Green Housing",
    "CT-BU-004": "Urban Resilience & Climate Adaptation Infrastructure",
    "CT-BU-005": "Green Roofs & Urban Greening",
    # EN — Energy Systems (10)
    "CT-EN-001": "Solar PV (Utility & Distributed)",
    "CT-EN-002": "Wind Energy",
    "CT-EN-003": "Small Hydropower",
    "CT-EN-004": "Energy Storage (Battery & Grid)",
    "CT-EN-005": "Grid Modernisation",
    "CT-EN-006": "Distributed Generation & Prosumers",
    "CT-EN-007": "Clean Cooking",
    "CT-EN-008": "Energy Efficiency (Industrial)",
    "CT-EN-009": "Green Hydrogen",
    "CT-EN-010": "Biomass & Biogas",
    # IC — ICT & Digitalization (6)
    "CT-IC-001": "Satellite Deforestation Monitoring",
    "CT-IC-002": "AI-powered MRV & Carbon Measurement",
    "CT-IC-003": "Supply Chain Traceability (EUDR)",
    "CT-IC-004": "Climate Data Platforms & APIs",
    "CT-IC-005": "Precision Agriculture Data",
    "CT-IC-006": "Smart Grid & IoT for Energy",
    # IN — Industry (5)
    "CT-IN-001": "Industrial Energy Efficiency",
    "CT-IN-002": "Green Hydrogen (Industrial Use)",
    "CT-IN-003": "Cement & Construction Materials Decarbonisation",
    "CT-IN-004": "Circular Economy & Industrial Symbiosis",
    "CT-IN-005": "Clean Manufacturing SMEs",
    # TR — Transport (5)
    "CT-TR-001": "Electric Vehicles (2W/3W/Bus Priority)",
    "CT-TR-002": "Public Transit Electrification",
    "CT-TR-003": "Freight Decarbonisation",
    "CT-TR-004": "Sustainable Aviation Fuels",
    "CT-TR-005": "Active Mobility Infrastructure",
    # WA — Waste (4)
    "CT-WA-001": "Waste-to-Energy & Biogas",
    "CT-WA-002": "Organic Waste & Composting",
    "CT-WA-003": "Recycling & Materials Recovery",
    "CT-WA-004": "Extended Producer Responsibility",
    # WW — Water & Wastewater (4)
    "CT-WW-001": "Water Treatment & Sanitation",
    "CT-WW-002": "Irrigation Efficiency & Precision Water",
    "CT-WW-003": "Watershed Conservation & Payments",
    "CT-WW-004": "Urban Flood Resilience",
    # XS — Cross-Sectoral (8)
    "CT-XS-001": "Carbon Markets & Credits",
    "CT-XS-002": "MRV Platforms",
    "CT-XS-003": "Climate Finance & Green Bonds",
    "CT-XS-004": "Climate Risk Assessment & Disclosure",
    "CT-XS-005": "NDC Implementation Tracking",
    "CT-XS-006": "Green Insurance & Climate Risk Products",
    "CT-XS-007": "Blended Finance Structures",
    "CT-XS-008": "Climate Governance & Policy Enablers",
}

VALID_CODES = set(CT_TAXONOMY.keys())

BS_BASE = "https://wiki.cleantechhub.net/api"
BOOK_ID = 621
MODEL = "claude-haiku-4-5-20251001"
DELAY = 0.3


def bs_headers(token_id: str, token_secret: str) -> dict:
    return {
        "Authorization": f"Token {token_id}:{token_secret}",
        "Content-Type": "application/json",
    }


def get_all_pages(headers: dict) -> list[dict]:
    """Paginate through all pages in Book 621."""
    pages, offset, count = [], 0, 50
    while True:
        r = requests.get(
            f"{BS_BASE}/pages",
            headers=headers,
            params={"filter[book_id]": BOOK_ID, "count": count, "offset": offset},
        )
        r.raise_for_status()
        data = r.json()
        batch = data.get("data", [])
        pages.extend(batch)
        if len(pages) >= data.get("total", 0) or not batch:
            break
        offset += count
    return pages


def get_page_detail(page_id: int, headers: dict) -> dict:
    r = requests.get(f"{BS_BASE}/pages/{page_id}", headers=headers)
    r.raise_for_status()
    return r.json()


def build_taxonomy_block() -> str:
    """Format the taxonomy for the Claude prompt."""
    lines = []
    for code, label in CT_TAXONOMY.items():
        lines.append(f"  {code} — {label}")
    return "\n".join(lines)


def classify(
    startup_name: str,
    category: str,
    description: str,
    problem: str,
    solution: str,
    client: anthropic.Anthropic,
) -> str:
    """Ask Claude to pick the single best-matching taxonomy code."""
    taxonomy_block = build_taxonomy_block()

    prompt = f"""You are classifying cleantech startup ideas for the CleantechHUB Nexus platform.

CTH CT Taxonomy (59 nodes across 9 sectors). Pick exactly ONE code:
{taxonomy_block}

Startup: {startup_name}
CLP Category: {category}
Pitch: {description}
Problem: {problem}
Solution: {solution}

Respond with ONLY the taxonomy code (e.g. CT-AF-007). No explanation, no label, no punctuation. Just the code."""

    msg = client.messages.create(
        model=MODEL,
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}],
    )
    result = msg.content[0].text.strip()

    # Exact match
    if result in VALID_CODES:
        return result

    # Extract code pattern from response (model sometimes adds the label)
    match = re.search(r"CT-[A-Z]{2}-\d{3}", result)
    if match and match.group(0) in VALID_CODES:
        return match.group(0)

    # Fallback: default to Cross-Sectoral governance
    print(f"  WARN: unexpected model output '{result}', defaulting to CT-XS-008")
    return "CT-XS-008"


def tag_page(
    page_id: int,
    existing_tags: list[dict],
    ct_code: str,
    headers: dict,
    dry_run: bool,
) -> None:
    """Write ct_taxonomy tag, overwriting any existing value."""
    new_tags = [t for t in existing_tags if t.get("name") != "ct_taxonomy"]
    new_tags.append({"name": "ct_taxonomy", "value": ct_code})

    if dry_run:
        print(f"  [DRY RUN] Would set ct_taxonomy={ct_code}")
        return

    r = requests.put(
        f"{BS_BASE}/pages/{page_id}",
        headers=headers,
        json={"tags": new_tags},
    )
    r.raise_for_status()


def main():
    parser = argparse.ArgumentParser(
        description="Classify CLP26 ideas against the 59-node CTH CT Taxonomy"
    )
    parser.add_argument("--bs-token-id", required=True)
    parser.add_argument("--bs-token-secret", required=True)
    parser.add_argument("--anthropic-key", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    headers = bs_headers(args.bs_token_id, args.bs_token_secret)
    client = anthropic.Anthropic(api_key=args.anthropic_key)

    print("Fetching all pages in Book 621...")
    pages = get_all_pages(headers)
    print(f"Found {len(pages)} pages")

    ok = err = 0
    results = []

    for i, page in enumerate(pages, 1):
        page_id = page["id"]
        name = page.get("name", "")

        detail = get_page_detail(page_id, headers)
        tags = detail.get("tags", [])

        def tag_val(n):
            return next((t["value"] for t in tags if t["name"] == n), "")

        category = tag_val("category")
        startup = name.split(" · ")[0].strip()

        md = detail.get("markdown", "")
        pitch_match = re.search(r"## Elevator Pitch\n([\s\S]*?)(?=\n## |$)", md)
        description = pitch_match.group(1).strip()[:500] if pitch_match else ""
        prob_match = re.search(r"## Climate Problem\n([\s\S]*?)(?=\n## |$)", md)
        problem = prob_match.group(1).strip()[:400] if prob_match else ""
        sol_match = re.search(r"## Solution\n([\s\S]*?)(?=\n## |$)", md)
        solution = sol_match.group(1).strip()[:400] if sol_match else ""

        old_val = tag_val("ct_taxonomy")
        tag_note = f" (overwriting '{old_val}')" if old_val else ""
        print(f"[{i}/{len(pages)}] Classifying: {startup} ({category}){tag_note}")

        try:
            ct_code = classify(startup, category, description, problem, solution, client)
            print(f"  -> {ct_code} ({CT_TAXONOMY[ct_code]})")
            tag_page(page_id, tags, ct_code, headers, args.dry_run)
            results.append({"startup": startup, "ct_taxonomy": ct_code})
            ok += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            err += 1

        time.sleep(DELAY)

    print(f"\nDone: {ok} tagged, {err} errors")

    if results:
        with open("ct_taxonomy_results.json", "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Results saved to ct_taxonomy_results.json")


if __name__ == "__main__":
    main()
