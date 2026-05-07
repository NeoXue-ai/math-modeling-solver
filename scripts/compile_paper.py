#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path

XELATEX_TIMEOUT_SECONDS = 120


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Compile the final CUMCM paper.")
    parser.add_argument("--project", required=True, type=Path, help="Project root path.")
    return parser.parse_args(argv)


def write_compile_report(workspace, reason, details=""):
    reports_dir = workspace / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report = reports_dir / "compile_report.md"
    content = ["# Compile Report", "", f"Status: FAIL", "", f"Reason: {reason}", ""]
    if details:
        content.extend(["Details:", "", "```", details.rstrip(), "```", ""])
    report.write_text("\n".join(content), encoding="utf-8")
    return report


def text_output(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def run_xelatex(paper_dir):
    command = ["xelatex", "-interaction=nonstopmode", "main.tex"]
    first = subprocess.run(
        command,
        cwd=paper_dir,
        text=True,
        capture_output=True,
        check=False,
        timeout=XELATEX_TIMEOUT_SECONDS,
    )
    second = subprocess.run(
        command,
        cwd=paper_dir,
        text=True,
        capture_output=True,
        check=False,
        timeout=XELATEX_TIMEOUT_SECONDS,
    )
    if first.returncode != 0:
        return first
    return second


def main(argv=None):
    args = parse_args(argv)
    workspace = args.project / "CUMCM_Workspace"
    paper_dir = workspace / "paper"
    output_dir = workspace / "output"
    reports_dir = workspace / "reports"
    main_tex = paper_dir / "main.tex"
    markdown = output_dir / "final_paper.md"

    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not main_tex.exists():
        if markdown.exists():
            print("LaTeX source not found; Markdown output is available")
            return 0
        reason = "LaTeX source not found and Markdown fallback is unavailable"
        write_compile_report(workspace, reason)
        print(reason)
        return 1

    if shutil.which("xelatex") is None:
        if not markdown.exists():
            reason = "xelatex not found and Markdown fallback is unavailable"
            write_compile_report(workspace, reason)
            print(reason)
            return 1
        print("xelatex not found; Markdown fallback remains available at CUMCM_Workspace/output/final_paper.md")
        return 0

    try:
        result = run_xelatex(paper_dir)
    except subprocess.TimeoutExpired as exc:
        reason = "xelatex timed out while compiling paper/main.tex"
        details = "\n".join(
            part
            for part in [str(exc), text_output(exc.stdout), text_output(exc.stderr)]
            if part
        )
        write_compile_report(workspace, reason, details)
        print(reason)
        return 1
    if result.returncode != 0:
        reason = "xelatex failed while compiling paper/main.tex"
        details = "\n".join(
            part
            for part in [
                f"returncode: {result.returncode}",
                "stdout:",
                result.stdout,
                "stderr:",
                result.stderr,
            ]
            if part is not None
        )
        write_compile_report(workspace, reason, details)
        print(reason)
        return 1

    pdf = paper_dir / "main.pdf"
    if not pdf.exists():
        reason = "xelatex completed but paper/main.pdf was not produced"
        write_compile_report(workspace, reason, result.stdout + result.stderr)
        print(reason)
        return 1

    shutil.copyfile(pdf, output_dir / "final_paper.pdf")
    print("LaTeX compiled successfully: CUMCM_Workspace/output/final_paper.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
