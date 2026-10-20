package cth.validate

default allow = false

allow if {
    input.validator.credential_type == "cth:ValidatorCredential"
    not input.validator.credential_expired
    input.validator.did != input.submission.submitter_did
    input.submission.methodology_type in input.validator.accredited_methodologies
}

deny_reason = "self_certification" if {
    input.validator.did == input.submission.submitter_did
}

deny_reason = "out_of_accreditation_scope" if {
    not input.submission.methodology_type in input.validator.accredited_methodologies
}
