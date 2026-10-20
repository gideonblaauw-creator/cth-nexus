package cth.submit



default allow = false

allow if {
    input.principal.credential_type == "cth:SubmitterCredential"
    not input.principal.credential_expired
    input.resource.fpic_status in {"approved", "not_required"}
    input.resource.methodology_id in data.methodology_registry
}

deny_reason = "fpic_not_granted" if {
    not input.resource.fpic_status in {"approved", "not_required"}
}

deny_reason = "credential_expired" if {
    input.principal.credential_expired
}

deny_reason = "methodology_not_registered" if {
    not input.resource.methodology_id in data.methodology_registry
}
