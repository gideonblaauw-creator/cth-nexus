from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.response import make_request_id, standard_headers

router = APIRouter(tags=["catalogue"])

CATALOGUE = {
    "@context": [
        "https://www.w3.org/ns/dcat.jsonld",
        {"odrl": "http://www.w3.org/ns/odrl/2/"},
    ],
    "@type": "dcat:Catalog",
    "dct:title": "CleantechHUB LATAM Startup Taxonomy Catalogue",
    "dct:publisher": {"@id": "https://cleantechhub.net"},
    "dcat:dataset": [
        {
            "@type": "dcat:Dataset",
            "dct:identifier": "cth-startups-v1",
            "dct:title": "LATAM Cleantech Startup Portfolio",
            "dct:description": "102 cleantech startups mapped to the CTH taxonomy (106 nodes)",
            "dct:license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "dct:source": "https://nexus.cleantechhub.net",
            "dcat:distribution": [
                {
                    "@type": "dcat:Distribution",
                    "dcat:accessURL": "https://data.cleantechhub.net/v1/startups",
                    "dcat:downloadURL": "https://data.cleantechhub.net/v1/startups/export",
                    "dct:format": "application/json",
                }
            ],
            "odrl:hasPolicy": {
                "@type": "odrl:Policy",
                "odrl:permission": [
                    {
                        "odrl:action": "odrl:read",
                        "odrl:constraint": {
                            "odrl:leftOperand": "odrl:purpose",
                            "odrl:operator": "odrl:isAnyOf",
                            "odrl:rightOperand": [
                                "research", "eudr", "csrd", "carbon", "internal",
                            ],
                        },
                    }
                ],
                "odrl:prohibition": [{"odrl:action": "odrl:commercialize"}],
            },
        },
        {
            "@type": "dcat:Dataset",
            "dct:identifier": "cth-taxonomy-v1",
            "dct:title": "LATAM Cleantech Taxonomy v1.1",
            "dct:description": "106 cleantech nodes across 10 sectors, LATAM-weighted",
            "dct:license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "dcat:distribution": [
                {
                    "@type": "dcat:Distribution",
                    "dcat:accessURL": "https://data.cleantechhub.net/v1/taxonomy/nodes",
                    "dct:format": "application/json",
                }
            ],
        },
    ],
}


@router.get("/catalogue")
def get_catalogue(request: Request):
    request_id = getattr(request.state, "request_id", make_request_id())
    headers = standard_headers(request_id)
    headers["Content-Type"] = "application/ld+json"
    return JSONResponse(content=CATALOGUE, headers=headers)
