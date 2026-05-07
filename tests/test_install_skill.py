import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = SKILL_ROOT / "scripts" / "install_skill.py"


class InstallSkillTests(unittest.TestCase):
    def run_installer(self, home, *args):
        return subprocess.run(
            [
                sys.executable,
                str(INSTALL_SCRIPT),
                "--source",
                str(SKILL_ROOT),
                "--home",
                str(home),
                *args,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_install_both_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)

            result = self.run_installer(home, "--target", "both")

            self.assertEqual(result.returncode, 0, result.stderr)
            codex = home / ".codex" / "skills" / "math-modeling-solver"
            claude = home / ".claude" / "skills" / "math-modeling-solver"
            self.assertTrue((codex / "SKILL.md").exists())
            self.assertTrue((codex / "scripts" / "setup_workspace.py").exists())
            self.assertTrue((claude / "SKILL.md").exists())
            self.assertTrue((claude / "references" / "model_library.md").exists())
            self.assertFalse((codex / ".git").exists())
            self.assertFalse((claude / ".git").exists())

    def test_install_codex_skips_when_source_is_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            target = home / ".codex" / "skills" / "math-modeling-solver"
            target.mkdir(parents=True)
            marker = target / "SKILL.md"
            marker.write_text("source marker\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL_SCRIPT),
                    "--source",
                    str(target),
                    "--home",
                    str(home),
                    "--target",
                    "codex",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("already installed", result.stdout)
            self.assertEqual(marker.read_text(encoding="utf-8"), "source marker\n")


if __name__ == "__main__":
    unittest.main()
