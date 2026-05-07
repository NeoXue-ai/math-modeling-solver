import os
import subprocess
import sys
import tempfile
import unittest.mock
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SETUP_SCRIPT = SKILL_ROOT / "scripts" / "setup_workspace.py"
COMPILE_SCRIPT = SKILL_ROOT / "scripts" / "compile_paper.py"


class CompilePaperTests(unittest.TestCase):
    def setup_workspace(self, root):
        setup = subprocess.run(
            [sys.executable, str(SETUP_SCRIPT), "--project", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(setup.returncode, 0, setup.stderr)
        return root / "CUMCM_Workspace"

    def test_missing_xelatex_keeps_markdown_fallback_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            (workspace / "paper" / "main.tex").write_text(
                """\\documentclass{ctexart}
\\begin{document}
Hello, CUMCM.
\\end{document}
""",
                encoding="utf-8",
            )
            markdown = workspace / "output" / "final_paper.md"
            markdown.write_text("# Final Paper\n\nMarkdown fallback.\n", encoding="utf-8")

            env = os.environ.copy()
            env["PATH"] = ""
            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("xelatex not found", result.stdout.lower())
            self.assertTrue(markdown.exists())

    def test_missing_xelatex_without_markdown_writes_compile_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            (workspace / "paper" / "main.tex").write_text(
                "\\documentclass{article}\\begin{document}x\\end{document}\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["PATH"] = ""

            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Markdown fallback is unavailable", result.stdout)
            report = (workspace / "reports" / "compile_report.md").read_text(encoding="utf-8")
            self.assertIn("xelatex not found", report)

    def test_missing_latex_source_uses_existing_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            markdown = workspace / "output" / "final_paper.md"
            markdown.write_text("# Final Paper\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("LaTeX source not found; Markdown output is available", result.stdout)

    def test_missing_latex_source_without_markdown_writes_compile_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)

            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("LaTeX source not found", result.stdout)
            report = (workspace / "reports" / "compile_report.md").read_text(encoding="utf-8")
            self.assertIn("Status: FAIL", report)

    def test_present_xelatex_is_invoked_twice_even_if_first_run_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            (workspace / "paper" / "main.tex").write_text(
                "\\documentclass{article}\\begin{document}x\\end{document}\n",
                encoding="utf-8",
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            calls = root / "xelatex_calls.txt"
            fake_xelatex = fake_bin / "xelatex"
            fake_xelatex.write_text(
                f"#!/bin/sh\nprintf 'called\\n' >> {calls}\nexit 1\n",
                encoding="utf-8",
            )
            fake_xelatex.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = str(fake_bin)

            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(calls.read_text(encoding="utf-8").count("called"), 2)

    def test_failed_xelatex_writes_compile_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            (workspace / "paper" / "main.tex").write_text(
                "\\documentclass{article}\\begin{document}x\\end{document}\n",
                encoding="utf-8",
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_xelatex = fake_bin / "xelatex"
            fake_xelatex.write_text("#!/bin/sh\necho compile failed\nexit 1\n", encoding="utf-8")
            fake_xelatex.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = str(fake_bin)

            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 1)
            report = (workspace / "reports" / "compile_report.md").read_text(encoding="utf-8")
            self.assertIn("xelatex failed", report)
            self.assertIn("compile failed", report)

    def test_successful_xelatex_copies_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            (workspace / "paper" / "main.tex").write_text(
                "\\documentclass{article}\\begin{document}x\\end{document}\n",
                encoding="utf-8",
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_xelatex = fake_bin / "xelatex"
            fake_xelatex.write_text(
                "#!/bin/sh\nprintf '%s' pdf > main.pdf\nexit 0\n",
                encoding="utf-8",
            )
            fake_xelatex.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = str(fake_bin)

            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((workspace / "output" / "final_paper.pdf").exists())

    def test_successful_xelatex_without_pdf_writes_compile_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            (workspace / "paper" / "main.tex").write_text(
                "\\documentclass{article}\\begin{document}x\\end{document}\n",
                encoding="utf-8",
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_xelatex = fake_bin / "xelatex"
            fake_xelatex.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_xelatex.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = str(fake_bin)

            result = subprocess.run(
                [sys.executable, str(COMPILE_SCRIPT), "--project", str(root)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 1)
            report = (workspace / "reports" / "compile_report.md").read_text(encoding="utf-8")
            self.assertIn("main.pdf was not produced", report)

    def test_xelatex_timeout_with_bytes_output_writes_compile_report(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("compile_paper", COMPILE_SCRIPT)
        compile_paper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(compile_paper)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = self.setup_workspace(root)
            (workspace / "paper" / "main.tex").write_text(
                "\\documentclass{article}\\begin{document}x\\end{document}\n",
                encoding="utf-8",
            )
            timeout = subprocess.TimeoutExpired(
                cmd=["xelatex"],
                timeout=1,
                output=b"bytes stdout",
                stderr=b"bytes stderr",
            )

            with unittest.mock.patch.object(compile_paper.shutil, "which", return_value="/fake/xelatex"):
                with unittest.mock.patch.object(compile_paper, "run_xelatex", side_effect=timeout):
                    result = compile_paper.main(["--project", str(root)])

            self.assertEqual(result, 1)
            report = (workspace / "reports" / "compile_report.md").read_text(encoding="utf-8")
            self.assertIn("bytes stdout", report)
            self.assertIn("bytes stderr", report)


if __name__ == "__main__":
    unittest.main()
