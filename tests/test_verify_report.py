import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "verify_report.py"


def load_verify_report():
    spec = importlib.util.spec_from_file_location("verify_report", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyReportTests(unittest.TestCase):
    def write_report(self, text):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        report = Path(directory.name) / "report.md"
        report.write_text(text, encoding="utf-8")
        return report

    def test_parse_pass_report(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: PASS
checks:
- id: V-OPT-1
  status: PASS
  detail: constraints satisfied
approved_for_paper: true
""",
        )

        parsed = load_verify_report().parse_report(report)

        self.assertEqual(parsed["model"], "problem1_model")
        self.assertEqual(parsed["status"], "PASS")
        self.assertTrue(parsed["approved_for_paper"])
        self.assertEqual(parsed["checks"][0]["id"], "V-OPT-1")

    def test_parse_fail_report_marks_not_approved(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: FAIL
checks:
- id: V-OPT-1
  status: FAIL
  detail: constraints violated
approved_for_paper: false
""",
        )

        parsed = load_verify_report().parse_report(report)

        self.assertEqual(parsed["status"], "FAIL")
        self.assertFalse(parsed["approved_for_paper"])

    def test_missing_checks_section_is_invalid(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: PASS
approved_for_paper: true
"""
        )

        with self.assertRaisesRegex(ValueError, "missing required section: checks"):
            load_verify_report().parse_report(report)

    def test_invalid_top_level_status_is_invalid(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: MAYBE
checks:
- id: V-OPT-1
  status: PASS
  detail: constraints satisfied
approved_for_paper: true
"""
        )

        with self.assertRaisesRegex(ValueError, "status must be PASS or FAIL"):
            load_verify_report().parse_report(report)

    def test_invalid_check_status_is_invalid(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: PASS
checks:
- id: V-OPT-1
  status: MAYBE
  detail: constraints satisfied
approved_for_paper: true
"""
        )

        with self.assertRaisesRegex(ValueError, "check status must be PASS or FAIL"):
            load_verify_report().parse_report(report)

    def test_invalid_approved_for_paper_bool_is_invalid(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: PASS
checks:
- id: V-OPT-1
  status: PASS
  detail: constraints satisfied
approved_for_paper: yes
"""
        )

        with self.assertRaisesRegex(ValueError, "approved_for_paper must be true or false"):
            load_verify_report().parse_report(report)

    def test_malformed_check_entry_is_invalid(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: PASS
checks:
- id: V-OPT-1
  status: PASS
approved_for_paper: true
"""
        )

        with self.assertRaisesRegex(ValueError, "check missing required key: detail"):
            load_verify_report().parse_report(report)

    def test_cli_reports_parse_errors_to_stderr(self):
        report = self.write_report(
            """VERIFICATION REPORT
model: problem1_model
status: PASS
approved_for_paper: true
"""
        )

        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(report)],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("verify_report parse error", result.stderr)
        self.assertIn(str(report), result.stderr)


if __name__ == "__main__":
    unittest.main()
