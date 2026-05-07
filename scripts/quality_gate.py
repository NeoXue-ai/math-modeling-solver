#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_report


REQUIRED_RESULT_KEYS = {
    "id",
    "subproblem",
    "source_script",
    "run_timestamp",
    "values",
    "figures",
    "verification_report",
    "verification_status",
    "approved_for_paper",
}

PLACEHOLDERS = ("\u8865\u5145", "\u5f85\u586b\u5199", "\u793a\u4f8b\u7ed3\u679c", "\u672a\u9a8c\u8bc1")
RESULT_REF_PATTERN = re.compile(r"(?<![A-Za-z0-9_])R[0-9][A-Za-z0-9_-]*(?![A-Za-z0-9_-])")
NUMERIC_LITERAL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_\\])[-+]?(?:\d+\.\d+|\d+\.\d*|\.\d+|\d{3,})(?:[eE][-+]?\d+)?%?(?![A-Za-z0-9_])"
)


def workspace_for(project: Path) -> Path:
    return project / "CUMCM_Workspace"


def block(command: str, reason: str) -> int:
    print(f"GATE BLOCKED {command}: {reason}")
    return 1


def pass_gate(command: str) -> int:
    print(f"GATE PASS {command}")
    return 0


def run_model_verify(report: Path) -> int:
    try:
        parsed = verify_report.parse_report(report)
    except (OSError, ValueError) as exc:
        return block("model_verify", f"parse error: {exc}")

    if parsed["status"] != "PASS":
        return block("model_verify", f"top-level status is {parsed['status']}")

    failed_checks = [check for check in parsed["checks"] if check.get("status") != "PASS"]
    if failed_checks:
        check_ids = ", ".join(str(check.get("id", "<missing id>")) for check in failed_checks)
        return block("model_verify", f"failed checks: {check_ids}")

    if parsed["approved_for_paper"] is not True:
        return block("model_verify", "report is not approved for paper")

    return pass_gate("model_verify")


def load_registry(registry_path: Path) -> tuple[dict | None, str | None]:
    if not registry_path.exists():
        return None, f"missing registry: {registry_path}"
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"invalid registry JSON: {exc.msg}"
    except OSError as exc:
        return None, f"cannot read registry: {exc}"
    if not isinstance(data, dict):
        return None, "registry must be a JSON object"
    if not isinstance(data.get("results"), list):
        return None, "registry results must be a list"
    return data, None


def resolve_workspace_path(workspace: Path, raw_path: str) -> Path | None:
    path = Path(raw_path)
    if not path.is_absolute():
        path = workspace / path
    try:
        resolved_workspace = workspace.resolve()
        resolved_path = path.resolve()
    except OSError:
        return None
    if resolved_path != resolved_workspace and resolved_workspace not in resolved_path.parents:
        return None
    return resolved_path


def figure_exists(workspace: Path, figure_path: str) -> bool:
    resolved_path = resolve_workspace_path(workspace, figure_path)
    if resolved_path is None:
        return False
    return resolved_path.exists()


def check_verification_report(workspace: Path, result_id: str, report_path: object) -> list[str]:
    if not isinstance(report_path, str) or not report_path:
        return [f"result {result_id} verification_report must be a non-empty string"]

    resolved_path = resolve_workspace_path(workspace, report_path)
    if resolved_path is None:
        return [f"result {result_id} verification_report must stay under workspace: {report_path}"]
    if not resolved_path.exists():
        return [f"result {result_id} missing verification_report: {report_path}"]

    try:
        parsed = verify_report.parse_report(resolved_path)
    except (OSError, ValueError) as exc:
        return [f"result {result_id} invalid verification_report: {exc}"]

    issues = []
    if parsed["status"] != "PASS":
        issues.append(f"result {result_id} verification_report status is {parsed['status']}")
    failed_checks = [check for check in parsed["checks"] if check.get("status") != "PASS"]
    if failed_checks:
        check_ids = ", ".join(str(check.get("id", "<missing id>")) for check in failed_checks)
        issues.append(f"result {result_id} verification_report failed checks: {check_ids}")
    if parsed["approved_for_paper"] is not True:
        issues.append(f"result {result_id} verification_report is not approved for paper")
    return issues


def audit_result(workspace: Path, result: object, index: int) -> list[str]:
    if not isinstance(result, dict):
        return [f"result #{index} must be an object"]

    result_id = result.get("id", f"#{index}")
    missing = sorted(REQUIRED_RESULT_KEYS - result.keys())
    issues = []
    if missing:
        issues.append(f"result {result_id} missing keys: {', '.join(missing)}")

    if result.get("verification_status") != "PASS":
        issues.append(f"result {result_id} verification_status is {result.get('verification_status')}")

    if result.get("approved_for_paper") is not True:
        issues.append(f"unapproved result {result_id}")

    if "verification_report" in result:
        issues.extend(check_verification_report(workspace, str(result_id), result.get("verification_report")))

    figures = result.get("figures", [])
    if not isinstance(figures, list):
        issues.append(f"result {result_id} figures must be a list")
    else:
        for figure in figures:
            if not isinstance(figure, str):
                issues.append(f"result {result_id} has non-string figure path")
            elif not figure_exists(workspace, figure):
                issues.append(f"result {result_id} missing figure: {figure}")

    return issues


def number_forms(value: object) -> set[str]:
    if isinstance(value, bool):
        return set()
    if isinstance(value, int):
        return {str(value)}
    if isinstance(value, float):
        forms = {str(value), format(value, "g"), format(value, ".12g")}
        if value.is_integer():
            forms.add(str(int(value)))
        return forms
    if isinstance(value, str):
        stripped = value.strip()
        if NUMERIC_LITERAL_PATTERN.fullmatch(stripped) or re.fullmatch(r"[-+]?\d+(?:[eE][-+]?\d+)?", stripped):
            return {stripped}
    return set()


def collect_allowed_numbers(value: object) -> set[str]:
    allowed = set()
    if isinstance(value, dict):
        for child in value.values():
            allowed.update(collect_allowed_numbers(child))
    elif isinstance(value, list):
        for child in value:
            allowed.update(collect_allowed_numbers(child))
    else:
        allowed.update(number_forms(value))
    return allowed


def registry_evidence(registry: dict | None) -> tuple[set[str], set[str]]:
    if not registry:
        return set(), set()
    result_ids = set()
    allowed_numbers = set()
    for result in registry.get("results", []):
        if not isinstance(result, dict):
            continue
        result_id = result.get("id")
        if isinstance(result_id, str):
            result_ids.add(result_id)
        if result.get("verification_status") == "PASS" and result.get("approved_for_paper") is True:
            allowed_numbers.update(collect_allowed_numbers(result.get("values", {})))
    return result_ids, allowed_numbers


def scan_paper_text(workspace: Path, result_ids: set[str], allowed_numbers: set[str]) -> list[str]:
    issues = []
    for relative in (Path("paper/main.tex"), Path("output/final_paper.md")):
        path = workspace / relative
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            issues.append(f"cannot read {relative}: {exc}")
            continue
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                issues.append(f"{relative} contains placeholder text: {placeholder}")
        for result_ref in sorted(set(RESULT_REF_PATTERN.findall(text))):
            if result_ref not in result_ids:
                issues.append(f"{relative} references unregistered result id: {result_ref}")
        for match in NUMERIC_LITERAL_PATTERN.finditer(text):
            literal = match.group(0)
            comparable = literal[:-1] if literal.endswith("%") else literal
            if comparable not in allowed_numbers and literal not in allowed_numbers:
                issues.append(f"{relative} contains unregistered numeric literal: {literal}")
    return issues


def write_qa_report(workspace: Path, passed: bool, issues: list[str]) -> None:
    report_dir = workspace / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# QA Report",
        "",
        f"Status: {'PASS' if passed else 'BLOCKED'}",
        "",
        "## Findings",
        "",
    ]
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- No blocking issues found.")
    lines.append("")
    (report_dir / "qa_report.md").write_text("\n".join(lines), encoding="utf-8")


def run_paper_audit(project: Path) -> int:
    workspace = workspace_for(project)
    registry_path = workspace / "memory" / "result_registry.json"
    registry, registry_error = load_registry(registry_path)
    issues: list[str] = []
    if registry_error:
        issues.append(registry_error)
    else:
        for index, result in enumerate(registry["results"], start=1):
            issues.extend(audit_result(workspace, result, index))

    result_ids, allowed_numbers = registry_evidence(registry)
    issues.extend(scan_paper_text(workspace, result_ids, allowed_numbers))
    try:
        write_qa_report(workspace, not issues, issues)
    except OSError as exc:
        issues.append(f"cannot write QA report: {exc}")

    if issues:
        return block("paper_audit", issues[0])
    return pass_gate("paper_audit")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run quality gates for modeling outputs and papers.")
    parser.add_argument("--project", required=True, type=Path, help="Project root path.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    model_verify = subparsers.add_parser("model-verify", help="Gate a verification report.")
    model_verify.add_argument("--report", required=True, type=Path, help="Verification report path.")

    subparsers.add_parser("paper-audit", help="Audit registry results and paper text.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "model-verify":
        return run_model_verify(args.report)
    if args.command == "paper-audit":
        return run_paper_audit(args.project)
    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
