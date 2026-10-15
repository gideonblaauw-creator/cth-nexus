"""Canonical Epic Angels APC-shareable allowlist (18 startups)."""

from __future__ import annotations

EPIC_ALLOWLIST_NAMES: list[str] = [
    "CurubaTech",
    "Amazóniko",
    "e.WAI",
    "ChumChum",
    "O3 Smart Cities",
    "Green Leaf",
    "Bio Natural Solutions",
    "CommunityLab",
    "Basilisco",
    "Reemade",
    "Xiclo",
    "EcoPoop",
    "SEOS Energy",
    "BioAmbientar",
    "Biogar",
    "Gescol SAS BIC",
    "Matter of Trust",
    "Cirkula",
]

EPIC_ALLOWLIST_SLUGS: frozenset[str] = frozenset(
    {
        "curuba",
        "amazoniko",
        "e-wai",
        "chumchum",
        "o3-smart-cities",
        "green-leaf",
        "bio-natural-solutions",
        "communitylab",
        "basilisco",
        "reemade",
        "xiclo",
        "ecopoop",
        "seos-energy",
        "bioambientar",
        "biogar",
        "gescol",
        "matter-of-trust",
        "cirkula",
    }
)

NAME_BY_SLUG: dict[str, str] = {
    "curuba": "CurubaTech",
    "amazoniko": "Amazóniko",
    "e-wai": "e.WAI",
    "chumchum": "ChumChum",
    "o3-smart-cities": "O3 Smart Cities",
    "green-leaf": "Green Leaf",
    "bio-natural-solutions": "Bio Natural Solutions",
    "communitylab": "CommunityLab",
    "basilisco": "Basilisco",
    "reemade": "Reemade",
    "xiclo": "Xiclo",
    "ecopoop": "EcoPoop",
    "seos-energy": "SEOS Energy",
    "bioambientar": "BioAmbientar",
    "biogar": "Biogar",
    "gescol": "Gescol SAS BIC",
    "matter-of-trust": "Matter of Trust",
    "cirkula": "Cirkula",
}

SLUG_ORDER: list[str] = [
    "curuba",
    "amazoniko",
    "e-wai",
    "chumchum",
    "o3-smart-cities",
    "green-leaf",
    "bio-natural-solutions",
    "communitylab",
    "basilisco",
    "reemade",
    "xiclo",
    "ecopoop",
    "seos-energy",
    "bioambientar",
    "biogar",
    "gescol",
    "matter-of-trust",
    "cirkula",
]


def is_epic_slug(slug: str) -> bool:
    return slug in EPIC_ALLOWLIST_SLUGS
