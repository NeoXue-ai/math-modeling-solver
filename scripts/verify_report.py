#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class ReportParseError(ValueError):
    def __init__(self, path: Path, message: str):
        super().__init__(f"{path}: {message}")
        self.path = path
        self.message = message


def _non_empty_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError("approved_for_paper must be true or false")


def _parse_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"expected key/value line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _parse_checks(lines: list[str], start_index: int) -> tuple[list[dict], int]:
    checks: list[dict] = []
    index = start_index
    while index < len(lines):
        line = lines[index]
        if line.startswith("approved_for_paper:"):
            break
        if not line.startswith("- id:"):
            raise ValueError(f"expected check id line: {line}")
        check = {"id": line.split(":", 1)[1].strip()}
        index += 1
        while index < len(lines) and not lines[index].startswith("- id:") and not lines[index].startswith("approved_for_paper:"):
            key, value = _parse_key_value(lines[index].strip())
            check[key] = value
            index += 1
        for required in ("id", "status", "detail"):
            if required not in check or not check[required]:
                raise ValueError(f"check missing required key: {required}")
        if check["status"] not in {"PASS", "FAIL"}:
            raise ValueError(f"check status must be PASS or FAIL: {check['status']}")
        checks.append(check)
    return checks, index


def parse_report(path: Path) -> dict:
    path = Path(path)
    lines = _non_empty_lines(path.read_text(encoding="utf-8"))
    if not lines or lines[0] != "VERIFICATION REPORT":
        raise ReportParseError(path, "first non-empty line must be VERIFICATION REPORT")

    data: dict[str, object] = {}
    saw_checks = False
    index = 1
    try:
        while index < len(lines):
            line = lines[index]
            if line == "checks:":
                saw_checks = True
                checks, index = _parse_checks(lines, index + 1)
                data["checks"] = checks
                continue
            key, value = _parse_key_value(line)
            if key == "approved_for_paper":
                data[key] = _parse_bool(value)
            else:
                data[key] = value
            index += 1
    except ValueError as exc:
        raise ReportParseError(path, str(exc)) from exc

    for required in ("model", "status", "approved_for_paper"):
        if required not in data:
            raise ReportParseError(path, f"missing required key: {required}")
    if not saw_checks:
        raise ReportParseError(path, "missing required section: checks")
    if not data.get("checks"):
        raise ReportParseError(path, "checks section must contain at least one check")
    if data["status"] not in {"PASS", "FAIL"}:
        raise ReportParseError(path, f"status must be PASS or FAIL: {data['status']}")

    return {
        "model": data["model"],
        "status": data["status"],
        "checks": data["checks"],
        "approved_for_paper": data["approved_for_paper"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse a structured verification report.")
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        parsed = parse_report(args.report)
    except (OSError, ValueError) as exc:
        print(f"verify_report parse error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
