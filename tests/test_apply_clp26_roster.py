"""Tests for CLP26 roster apply script (JS MENTORS array append)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_clp26_roster import (  # noqa: E402
    find_mentors_array_bounds,
    format_mentor_object_js,
    merge_html,
    parse_mentors_array_body,
)

SAMPLE_HTML = """<!DOCTYPE html>
<script>
const MENTORS = [
{id:"M002",name:"Juliana Rincón",linkedin:"https://www.linkedin.com/in/juliana/",photo:"/nexus-assets/mentors/juliana.jpg",desc:"Cofundadora."},
{id:"M073",name:"Miguel Ñañez",linkedin:"https://www.linkedin.com/in/miguel/",desc:"Gerente territorial."}
];
</script>
"""


class TestMentorsJsAppend(unittest.TestCase):
    def test_parse_js_array_body(self) -> None:
        open_b, close_b = find_mentors_array_bounds(SAMPLE_HTML)
        body = SAMPLE_HTML[open_b + 1 : close_b]
        ids, names, links = parse_mentors_array_body(body)
        self.assertEqual(ids, {"M002", "M073"})
        self.assertIn("miguel nanez", names)
        self.assertTrue(any("linkedin.com/in/miguel" in l for l in links))

    def test_format_mentor_object_omits_photo_when_empty(self) -> None:
        s = format_mentor_object_js(
            {
                "id": "M077",
                "name": "Alaide Díaz",
                "linkedin_url": "https://www.linkedin.com/in/alaide/",
                "desc": "",
            }
        )
        self.assertEqual(
            s,
            '{id:"M077",name:"Alaide Díaz",linkedin:"https://www.linkedin.com/in/alaide/",desc:""}',
        )
        self.assertNotIn("photo:", s)

    def test_merge_appends_without_mutating_existing_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            html_path.write_text(SAMPLE_HTML, encoding="utf-8")
            original = SAMPLE_HTML
            open_b, close_b = find_mentors_array_bounds(original)
            preserved = original[:close_b]

            additions = [
                {
                    "id": "M077",
                    "name": "New Mentor",
                    "linkedin_url": "https://www.linkedin.com/in/new/",
                    "desc": "CLP26 mentor.",
                }
            ]
            added, skipped = merge_html(html_path, additions, dry_run=False)
            self.assertEqual((added, skipped), (1, 0))

            result = html_path.read_text(encoding="utf-8")
            self.assertTrue(result.startswith(preserved))
            self.assertIn(
                '{id:"M077",name:"New Mentor",linkedin:"https://www.linkedin.com/in/new/",desc:"CLP26 mentor."}',
                result,
            )
            self.assertTrue(result.endswith("];\n</script>\n"))

    def test_merge_skips_duplicate_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            html_path.write_text(SAMPLE_HTML, encoding="utf-8")
            additions = [
                {
                    "id": "M002",
                    "name": "Someone else",
                    "linkedin_url": "https://www.linkedin.com/in/other/",
                    "desc": "",
                }
            ]
            added, skipped = merge_html(html_path, additions, dry_run=True)
            self.assertEqual((added, skipped), (0, 1))

    def test_merge_refuses_missing_linkedin_in_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            html_path.write_text(SAMPLE_HTML, encoding="utf-8")
            # validate_additions is separate; merge_html skips blank linkedin_url
            additions = [{"id": "M099", "name": "No LI", "linkedin_url": "", "desc": ""}]
            added, skipped = merge_html(html_path, additions, dry_run=True)
            self.assertEqual((added, skipped), (0, 1))


if __name__ == "__main__":
    unittest.main()
