import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SETUP = SKILL_ROOT / "scripts" / "setup_workspace.py"
QUALITY_GATE = SKILL_ROOT / "scripts" / "quality_gate.py"


class QualityGateTests(unittest.TestCase):
    def setup_workspace(self, root):
        result = subprocess.run(
            [sys.executable, str(SETUP), "--project", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return root / "CUMCM_Workspace"

    def run_quality_gate(self, root, *args):
        return subprocess.run(
            [sys.executable, str(QUALITY_GATE), "--project", str(root), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def write_pass_report(self, workspace):
        report = workspace / "reports" / "verification" / "problem1_report.md"
        report.write_text(
            """VERIFICATION REPORT
model: problem1_model
status: PASS
checks:
- id: V-OPT-1
  status: PASS
  detail: constraints satisfied
approved_for_paper: true
""",
            encoding="utf-8",
        )
        return report

    def write_registry(self, workspace, figures=None, values=None, verification_report="reports/verification/problem1_report.md"):
        registry = workspace / "memory" / "result_registry.json"
        registry.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "results": [
                        {
                            "id": "R1",
                            "subproblem": "Q1",
                            "source_script": "src/models/problem1.py",
                            "run_timestamp": "2026-05-07T00:00:00+00:00",
                            "values": values if values is not None else {"objective": 42},
                            "figures": figures or [],
                            "verification_report": verification_report,
                            "verification_status": "PASS",
                            "approved_for_paper": True,
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return registry

    def test_verify_gate_passes_approved_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            report = self.write_pass_report(workspace)

            result = self.run_quality_gate(root, "model-verify", "--report", str(report))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("GATE PASS model_verify", result.stdout)

    def test_verify_gate_blocks_failed_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            report = workspace / "reports" / "verification" / "problem1_report.md"
            report.write_text(
                """VERIFICATION REPORT
model: problem1_model
status: FAIL
checks:
- id: V-OPT-1
  status: FAIL
  detail: constraints violated
approved_for_paper: false
""",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "model-verify", "--report", str(report))

            self.assertEqual(result.returncode, 1)
            self.assertIn("blocked", result.stdout.lower())

    def test_paper_gate_passes_approved_registry_and_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            self.write_pass_report(workspace)
            self.write_registry(workspace)
            (workspace / "output" / "final_paper.md").write_text(
                "Q1 result uses R1.\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("GATE PASS paper_audit", result.stdout)
            qa_report = (workspace / "reports" / "qa_report.md").read_text(encoding="utf-8")
            self.assertIn("Status: PASS", qa_report)

    def test_paper_gate_blocks_unapproved_registry_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            self.write_pass_report(workspace)
            registry = workspace / "memory" / "result_registry.json"
            registry.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "results": [
                            {
                                "id": "R1",
                                "subproblem": "Q1",
                                "source_script": "src/models/problem1.py",
                                "run_timestamp": "2026-05-07T00:00:00+00:00",
                                "values": {"objective": 42},
                                "figures": [],
                                "verification_report": "reports/verification/problem1_report.md",
                                "verification_status": "PASS",
                                "approved_for_paper": False,
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (workspace / "output" / "final_paper.md").write_text(
                "Q1 result uses R1.\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("unapproved", result.stdout.lower())

    def test_paper_gate_blocks_placeholder_text_and_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            placeholder = "\u5f85\u586b\u5199"
            self.write_pass_report(workspace)
            self.write_registry(workspace)
            (workspace / "output" / "final_paper.md").write_text(
                f"Q1 result uses R1. {placeholder} sensitivity notes.\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("blocked", result.stdout.lower())
            qa_report = (workspace / "reports" / "qa_report.md").read_text(encoding="utf-8")
            self.assertIn(f"output/final_paper.md contains placeholder text: {placeholder}", qa_report)

    def test_paper_gate_blocks_missing_relative_figure_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            self.write_pass_report(workspace)
            self.write_registry(workspace, figures=["figures/missing.png"])

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing figure: figures/missing.png", result.stdout)

    def test_paper_gate_passes_relative_figure_path_under_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            figure = workspace / "figures" / "result.png"
            figure.write_text("png placeholder\n", encoding="utf-8")
            self.write_pass_report(workspace)
            self.write_registry(workspace, figures=["figures/result.png"])

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("GATE PASS paper_audit", result.stdout)

    def test_paper_gate_blocks_absolute_figure_path_outside_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            outside_figure = root / "outside.png"
            outside_figure.write_text("png placeholder\n", encoding="utf-8")
            self.write_pass_report(workspace)
            self.write_registry(workspace, figures=[str(outside_figure)])

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing figure", result.stdout)

    def test_paper_gate_blocks_missing_registry_verification_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            self.write_registry(workspace, verification_report="reports/verification/missing_report.md")
            (workspace / "output" / "final_paper.md").write_text(
                "Q1 result uses R1.\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing verification_report", result.stdout)

    def test_paper_gate_blocks_registry_verification_report_that_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            report = workspace / "reports" / "verification" / "problem1_report.md"
            report.write_text(
                """VERIFICATION REPORT
model: problem1_model
status: FAIL
checks:
- id: V-OPT-1
  status: FAIL
  detail: constraints violated
approved_for_paper: false
""",
                encoding="utf-8",
            )
            self.write_registry(workspace)
            (workspace / "output" / "final_paper.md").write_text(
                "Q1 result uses R1.\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("verification_report", result.stdout)

    def test_paper_gate_blocks_unregistered_numeric_literal_in_paper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            self.write_pass_report(workspace)
            self.write_registry(workspace, values={"objective": 42})
            (workspace / "output" / "final_paper.md").write_text(
                "Q1 result uses R1. Extra objective is 42.7.\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("unregistered numeric literal: 42.7", result.stdout)

    def test_paper_gate_blocks_unregistered_result_id_next_to_chinese_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            self.write_pass_report(workspace)
            self.write_registry(workspace)
            (workspace / "output" / "final_paper.md").write_text(
                "引用R2结果。\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("unregistered result id: R2", result.stdout)

    def test_paper_gate_blocks_registry_verification_report_not_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            report = workspace / "reports" / "verification" / "problem1_report.md"
            report.write_text(
                """VERIFICATION REPORT
model: problem1_model
status: PASS
checks:
- id: V-OPT-1
  status: PASS
  detail: constraints satisfied
approved_for_paper: false
""",
                encoding="utf-8",
            )
            self.write_registry(workspace)
            (workspace / "output" / "final_paper.md").write_text(
                "Q1 result uses R1.\n",
                encoding="utf-8",
            )

            result = self.run_quality_gate(root, "paper-audit")

            self.assertEqual(result.returncode, 1)
            self.assertIn("verification_report is not approved", result.stdout)


if __name__ == "__main__":
    unittest.main()
