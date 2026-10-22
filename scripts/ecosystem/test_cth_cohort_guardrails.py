#!/usr/bin/env python3
"""Guardrail checks for cth_cohort evidence. No network."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cth_cohort_guardrails import (  # noqa: E402
    EVIDENCE_TYPE_PUBLIC,
    cth_cohort_blockers,
    evidence_type_of,
)

PROGRAMMES = {"pe-cleantechhub", "cth-academy", "cth-climate-launchpad", "cth-climaccelerator"}


def cohort(**extra):
    row = {
        "source": "startup-x",
        "target": "challenge:PE-2-agua",
        "type": "works_on_challenge",
        "evidence_type": "cth_cohort",
        "programme": "cth-academy",
        "source_url": "https://cohort.internal/startup-x",
        "evidence": "Startup X joined the CTH Academy cohort and worked on water treatment.",
    }
    row.update(extra)
    return row


class CthCohortGuardrailTests(unittest.TestCase):
    def test_default_evidence_type_is_public_quote(self):
        self.assertEqual(evidence_type_of({}), EVIDENCE_TYPE_PUBLIC)
        self.assertEqual(evidence_type_of({"evidence_type": "  "}), EVIDENCE_TYPE_PUBLIC)

    def test_skip_allowed_when_all_three_hold(self):
        self.assertEqual(cth_cohort_blockers(cohort(), PROGRAMMES), [])

    def test_endpoint_counts_as_programme_when_field_omitted(self):
        row = cohort(programme=None, source="pe-cleantechhub")
        del row["programme"]
        self.assertEqual(cth_cohort_blockers(row, PROGRAMMES), [])

    def test_programme_must_be_listed(self):
        reasons = cth_cohort_blockers(
            cohort(programme="pe-proinnovate-startup-peru"), PROGRAMMES
        )
        self.assertTrue(any("not a CTH-run programme" in r for r in reasons))

    def test_explicit_programme_beats_a_listed_endpoint(self):
        reasons = cth_cohort_blockers(
            cohort(programme="minam", source="pe-cleantechhub"), PROGRAMMES
        )
        self.assertTrue(any("not a CTH-run programme" in r for r in reasons))

    def test_personal_email_fails(self):
        reasons = cth_cohort_blockers(
            cohort(evidence="Write founder@example.com for the cohort note."), PROGRAMMES
        )
        self.assertTrue(any("email" in r for r in reasons))

    def test_personal_phone_fails(self):
        reasons = cth_cohort_blockers(
            cohort(evidence="Call +51 999 888 777 after the session."), PROGRAMMES
        )
        self.assertTrue(any("phone" in r for r in reasons))

    def test_home_address_fails(self):
        reasons = cth_cohort_blockers(
            cohort(home_address="Calle Los Pinos 123"), PROGRAMMES
        )
        self.assertTrue(any("home address" in r for r in reasons))

    def test_iso_date_is_not_a_phone(self):
        reasons = cth_cohort_blockers(
            cohort(evidence="Cohort note dated 2026-10-22."), PROGRAMMES
        )
        self.assertEqual(reasons, [])

    def test_consent_ref_is_not_a_phone(self):
        reasons = cth_cohort_blockers(cohort(consent_ref="consent-2026-014"), PROGRAMMES)
        self.assertEqual(reasons, [])

    def test_resolution_number_is_not_a_phone(self):
        reasons = cth_cohort_blockers(
            cohort(evidence="Recorded under resolution N.° 388-2026."), PROGRAMMES
        )
        self.assertEqual(reasons, [])

    def test_money_without_consent_fails(self):
        reasons = cth_cohort_blockers(
            cohort(type="funding", evidence="Awarded USD 10000."), PROGRAMMES
        )
        self.assertTrue(any("consent_ref" in r for r in reasons))

    def test_pilot_outcome_without_consent_fails(self):
        reasons = cth_cohort_blockers(
            cohort(pilot_outcome="Pilot reduced water use."), PROGRAMMES
        )
        self.assertTrue(any("consent_ref" in r for r in reasons))

    def test_money_and_pilot_pass_with_consent_ref(self):
        reasons = cth_cohort_blockers(
            cohort(
                type="funding",
                amount="10000",
                pilot_outcome="Pilot reduced water use.",
                consent_ref="consent-2026-014",
            ),
            PROGRAMMES,
        )
        self.assertEqual(reasons, [])

    def test_nested_outcome_needs_its_own_consent_when_row_has_none(self):
        reasons = cth_cohort_blockers(
            cohort(outcomes=[{"pilot_outcome": "Pilot shipped", "consent_ref": ""}]),
            PROGRAMMES,
        )
        self.assertTrue(any("consent_ref" in r for r in reasons))

    def test_row_consent_covers_nested_outcome(self):
        reasons = cth_cohort_blockers(
            cohort(
                consent_ref="consent-2026-014",
                outcomes=[{"pilot_outcome": "Pilot shipped"}],
            ),
            PROGRAMMES,
        )
        self.assertEqual(reasons, [])


if __name__ == "__main__":
    unittest.main()
