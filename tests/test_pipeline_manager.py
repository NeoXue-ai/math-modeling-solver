import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SETUP = SKILL_ROOT / "scripts" / "setup_workspace.py"
PIPELINE = SKILL_ROOT / "scripts" / "pipeline_manager.py"


class PipelineManagerTests(unittest.TestCase):
    def setup_workspace(self, root):
        result = subprocess.run(
            [sys.executable, str(SETUP), "--project", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return root / "CUMCM_Workspace"

    def run_pipeline(self, root, *args):
        return subprocess.run(
            [sys.executable, str(PIPELINE), "--project", str(root), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def read_state(self, workspace):
        return json.loads((workspace / "state" / "pipeline.json").read_text(encoding="utf-8"))

    def test_review_approval_records_decision_and_advances(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)

            start_result = self.run_pipeline(root, "start-stage", "problem_parse")
            self.assertEqual(start_result.returncode, 0, start_result.stderr)

            review_result = self.run_pipeline(
                root,
                "request-review",
                "--stage",
                "model_route_review",
                "--summary",
                "Route A, Route B, Route C",
                "--next",
                "assumption_review",
            )
            self.assertEqual(review_result.returncode, 0, review_result.stderr)
            review_request = (workspace / "state" / "review_request.md").read_text(encoding="utf-8")
            self.assertIn("model_route_review", review_request)
            self.assertIn("Route A, Route B, Route C", review_request)
            self.assertIn("assumption_review", review_request)

            approve_result = self.run_pipeline(
                root,
                "approve",
                "--stage",
                "model_route_review",
                "--decision",
                "Choose Route B",
            )
            self.assertEqual(approve_result.returncode, 0, approve_result.stderr)

            state = self.read_state(workspace)
            self.assertEqual(state["stages"]["model_route_review"]["status"], "approved")
            self.assertEqual(state["current_stage"], "assumption_review")

            rerun_result = self.run_pipeline(
                root,
                "approve",
                "--stage",
                "model_route_review",
                "--decision",
                "Choose Route B",
            )
            self.assertEqual(rerun_result.returncode, 0, rerun_result.stderr)
            decisions = (workspace / "state" / "user_decisions.md").read_text(encoding="utf-8")
            self.assertEqual(decisions.count("Choose Route B"), 1)

    def test_invalid_stage_exits_code_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_workspace(root)

            result = self.run_pipeline(root, "start-stage", "not_a_stage")

            self.assertEqual(result.returncode, 2)
            self.assertIn("unknown stage", result.stderr)

    def test_missing_workspace_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_pipeline(root, "status")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing workspace", result.stderr)

    def test_start_stage_rerun_preserves_started_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)

            first = self.run_pipeline(root, "start-stage", "problem_parse")
            self.assertEqual(first.returncode, 0, first.stderr)
            first_started_at = self.read_state(workspace)["stages"]["problem_parse"]["started_at"]

            second = self.run_pipeline(root, "start-stage", "problem_parse")
            self.assertEqual(second.returncode, 0, second.stderr)
            second_started_at = self.read_state(workspace)["stages"]["problem_parse"]["started_at"]

            self.assertEqual(second_started_at, first_started_at)

    def test_advance_rerun_preserves_approval_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)

            first = self.run_pipeline(root, "advance", "problem_parse")
            self.assertEqual(first.returncode, 0, first.stderr)
            first_state = self.read_state(workspace)
            first_approved_at = first_state["stages"]["problem_parse"]["approved_at"]
            first_completed_at = first_state["stages"]["problem_parse"]["completed_at"]

            second = self.run_pipeline(root, "advance", "problem_parse")
            self.assertEqual(second.returncode, 0, second.stderr)
            second_state = self.read_state(workspace)

            self.assertEqual(second_state["stages"]["problem_parse"]["approved_at"], first_approved_at)
            self.assertEqual(second_state["stages"]["problem_parse"]["completed_at"], first_completed_at)
            self.assertEqual(second_state["current_stage"], "model_route_review")

    def test_rework_rerun_with_same_feedback_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)

            first = self.run_pipeline(
                root,
                "rework",
                "--stage",
                "model_route_review",
                "--feedback",
                "Need clearer assumptions.",
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            second = self.run_pipeline(
                root,
                "rework",
                "--stage",
                "model_route_review",
                "--feedback",
                "Need clearer assumptions.",
            )
            self.assertEqual(second.returncode, 0, second.stderr)

            state = self.read_state(workspace)
            stage_log = (workspace / "state" / "stage_log.md").read_text(encoding="utf-8")
            self.assertEqual(state["stages"]["model_route_review"]["review_round"], 1)
            self.assertEqual(stage_log.count("Need clearer assumptions."), 1)


if __name__ == "__main__":
    unittest.main()
