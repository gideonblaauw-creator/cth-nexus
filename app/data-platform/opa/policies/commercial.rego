package cth.commercial

default allow = false

allow if {
    input.caller_tier != "commercial"
}

allow if {
    input.caller_tier == "commercial"
    input.cpi_licence_active == true
    input.benefit_agreement_present == true
}

deny_reason = "cpi_licence_pending" if {
    input.caller_tier == "commercial"
    input.cpi_licence_active == false
}

deny_reason = "no_benefit_agreement" if {
    input.caller_tier == "commercial"
    input.cpi_licence_active == true
    input.benefit_agreement_present == false
}
