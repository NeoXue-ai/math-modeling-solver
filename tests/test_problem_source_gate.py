import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SETUP = SKILL_ROOT / "scripts" / "setup_workspace.py"
GATE = SKILL_ROOT / "scripts" / "problem_source_gate.py"
SKILL = SKILL_ROOT / "SKILL.md"
WORKFLOW_REFERENCE = SKILL_ROOT / "references" / "cumcm_workflow.md"


class ProblemSourceGateTests(unittest.TestCase):
    def setup_workspace(self, root):
        result = subprocess.run(
            [sys.executable, str(SETUP), "--project", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return root / "CUMCM_Workspace"

    def run_gate(self, root):
        return subprocess.run(
            [sys.executable, str(GATE), "--project", str(root), "validate"],
            text=True,
            capture_output=True,
            check=False,
        )

    def write_source(self, workspace, payload):
        path = workspace / "memory" / "problem_source.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_unknown_source_blocks_modeling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_workspace(root)

            result = self.run_gate(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("source_type is unknown", result.stdout)

    def test_official_claim_without_source_evidence_blocks_modeling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            self.write_source(
                workspace,
                {
                    "schema_version": 1,
                    "source_type": "unknown",
                    "ready_for_modeling": False,
                    "contest_claim": "2026 CUMCM",
                    "problem_code": "B",
                    "official_claim": True,
                    "statement_path": "",
                    "source_files": [],
                    "notes": "No source evidence.",
                },
            )

            result = self.run_gate(root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("official contest claim requires source evidence", result.stdout)

    def test_pasted_statement_passes_when_statement_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            statement = workspace / "problem" / "statement.md"
            statement.write_text("# 题面\n\n这是用户粘贴的模拟题题面。\n", encoding="utf-8")
            self.write_source(
                workspace,
                {
                    "schema_version": 1,
                    "source_type": "pasted_statement",
                    "ready_for_modeling": True,
                    "contest_claim": "",
                    "problem_code": "",
                    "official_claim": False,
                    "statement_path": "problem/statement.md",
                    "source_files": [],
                    "notes": "User pasted statement.",
                },
            )

            result = self.run_gate(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SOURCE PASS", result.stdout)

    def test_official_file_passes_when_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            official = workspace / "problem" / "attachments" / "B.pdf"
            official.write_text("fake pdf bytes for source gate test\n", encoding="utf-8")
            self.write_source(
                workspace,
                {
                    "schema_version": 1,
                    "source_type": "official_file",
                    "ready_for_modeling": True,
                    "contest_claim": "CUMCM",
                    "problem_code": "B",
                    "official_claim": True,
                    "statement_path": "",
                    "source_files": ["problem/attachments/B.pdf"],
                    "notes": "User supplied official file.",
                },
            )

            result = self.run_gate(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SOURCE PASS", result.stdout)

    def test_skill_instructions_require_source_gate(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("problem_source_gate.py", text)
        self.assertIn("Do not infer or fabricate a problem statement", text)
        self.assertIn("Official contest claims require source evidence", text)

    def test_workflow_reference_requires_source_gate_before_parse(self):
        text = WORKFLOW_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("Passing `problem_source_gate`", text)
        self.assertIn("Do not invent contest year", text)


if __name__ == "__main__":
    unittest.main()
