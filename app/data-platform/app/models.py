from __future__ import annotations

from pydantic import BaseModel


class TaxonomyNodeOut(BaseModel):
    id: str
    sector: str
    seq: int
    label_short: str
    label_full: str
    description: str | None = None
    parent_id: str | None = None
    latam_relevance: str | None = None
    latam_colombia: int = 0
    latam_mexico: int = 0
    latam_chile: int = 0
    cth_data_coverage: str = "N"
    cth_clp_coverage: str | None = None
    bookstack_page_id: int | None = None
    version: str = "1.1"


class StartupOut(BaseModel):
    id: str
    nexus_id: str | None = None
    name: str
    country: str
    program: str | None = None
    stage: str | None = None
    website: str | None = None
    description: str | None = None
    ct_primary_node: str | None = None
    ct_secondary_1: str | None = None
    ct_secondary_2: str | None = None
    mapping_confidence: str | None = None
    mapping_notes: str | None = None
    nexus_theme: str | None = None
    data_licence: str = "CC BY-NC-SA 4.0"


class PolicyEvalRequest(BaseModel):
    purpose: str
    resource_type: str | None = None
    resource_id: str | None = None
    caller_tier: str | None = None


class PolicyEvalResponse(BaseModel):
    allow: bool
    ttl: int = 3600
    purpose: str
    request_id: str
    error: str | None = None
    reason: str | None = None


class ApiKeyCreateRequest(BaseModel):
    tier: str
    declared_purpose: str
    organisation: str | None = None
    contact_email: str | None = None


class ApiKeyCreateResponse(BaseModel):
    id: str
    raw_key: str
    key_prefix: str
    tier: str
    declared_purpose: str
    message: str = "Store this key securely. It will not be shown again."


class HealthResponse(BaseModel):
    status: str
    db: str
    version: str


class Meta(BaseModel):
    total: int
    limit: int
    offset: int
    request_id: str
    dataset_version: str
    last_updated: str


class EnvelopeResponse(BaseModel):
    data: list
    meta: Meta


class ErrorResponse(BaseModel):
    error: str
    request_id: str | None = None
    valid: list[str] | None = None
    reason: str | None = None
    docs: str | None = None
