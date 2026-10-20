package cth.purpose

default allow = false

valid_purposes := {"research", "eudr", "csrd", "carbon", "internal"}

allow if {
    input.declared_purpose in valid_purposes
    input.declared_purpose in input.fpic_permitted_purposes
}

allow if {
    input.declared_purpose in valid_purposes
    input.fpic_permitted_purposes == null
}

deny_reason = "purpose_not_in_fpic" if {
    input.declared_purpose in valid_purposes
    not input.declared_purpose in input.fpic_permitted_purposes
    input.fpic_permitted_purposes != null
}
