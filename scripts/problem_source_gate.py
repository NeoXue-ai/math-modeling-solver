#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

VALID_SOURCE_TYPES = {"official_file", "pasted_statement", "mock_problem"}


def workspace_for(project):
    return project / "CUMCM_Workspace"


def load_source(workspace):
    path = workspace / "memory" / "problem_source.json"
    if not path.exists():
        return None, f"missing problem source metadata: {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"invalid problem_source.json: {exc.msg}"
    if not isinstance(data, dict):
        return None, "problem_source.json must be a JSON object"
    return data, None


def resolve_workspace_path(workspace, value):
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if not path.is_absolute():
        path = workspace / path
    try:
        workspace_resolved = workspace.resolve()
        path_resolved = path.resolve()
    except OSError:
        return None
    if path_resolved != workspace_resolved and workspace_resolved not in path_resolved.parents:
        return None
    return path_resolved


def nonempty_file(path):
    try:
        return path.exists() and path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


def validate_source(workspace, source):
    issues = []
    source_type = source.get("source_type", "unknown")

    if source.get("official_claim") is True and source_type not in {"official_file", "pasted_statement"}:
        issues.append("official contest claim requires source evidence")

    if source_type == "unknown":
        issues.append("source_type is unknown")
    elif source_type not in VALID_SOURCE_TYPES:
        issues.append(f"invalid source_type: {source_type}")

    if source_type == "official_file":
        files = source.get("source_files", [])
        if not isinstance(files, list) or not files:
            issues.append("official_file source requires at least one source file")
        else:
            for item in files:
                path = resolve_workspace_path(workspace, item)
                if path is None or not nonempty_file(path):
                    issues.append(f"missing source file: {item}")

    if source_type in {"pasted_statement", "mock_problem"}:
        path = resolve_workspace_path(workspace, source.get("statement_path", ""))
        if path is None or not nonempty_file(path):
            issues.append(f"{source_type} requires a non-empty statement_path")

    if source.get("ready_for_modeling") is not True:
        issues.append("ready_for_modeling is not true")

    return issues


def cmd_validate(args):
    workspace = workspace_for(args.project)
    source, error = load_source(workspace)
    if error:
        print(f"SOURCE BLOCKED: {error}")
        return 1

    issues = validate_source(workspace, source)
    if issues:
        print(f"SOURCE BLOCKED: {issues[0]}")
        return 1
    print(f"SOURCE PASS: {source['source_type']}")
    return 0


def cmd_status(args):
    workspace = workspace_for(args.project)
    source, error = load_source(workspace)
    if error:
        print(error)
        return 1
    print(json.dumps(source, ensure_ascii=False, indent=2))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Validate problem source evidence before modeling.")
    parser.add_argument("--project", required=True, type=Path, help="Project root path.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.set_defaults(func=cmd_validate)
    status = subparsers.add_parser("status")
    status.set_defaults(func=cmd_status)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
