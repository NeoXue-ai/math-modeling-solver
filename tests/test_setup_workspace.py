import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "setup_workspace.py"


class SetupWorkspaceTests(unittest.TestCase):
    def test_init_creates_required_workspace_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            workspace = root / "CUMCM_Workspace"
            self.assertTrue((workspace / "state" / "pipeline.json").exists())
            self.assertTrue((workspace / "state" / "review_request.md").exists())
            self.assertTrue((workspace / "state" / "user_decisions.md").exists())
            self.assertTrue((workspace / "memory" / "result_registry.json").exists())
            state = json.loads((workspace / "state" / "pipeline.json").read_text(encoding="utf-8"))
            self.assertEqual(state["current_stage"], "problem_parse")
            self.assertEqual(state["stages"]["problem_parse"]["status"], "not_started")


if __name__ == "__main__":
    unittest.main()
