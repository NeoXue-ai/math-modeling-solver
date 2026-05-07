#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


STAGES = [
    "problem_parse",
    "model_route_review",
    "assumption_review",
    "data_audit",
    "data_preprocess",
    "model_build",
    "model_verify",
    "sensitivity_analysis",
    "result_review",
    "paper_draft",
    "paper_quality_audit",
    "final_compile",
    "complete",
]


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def workspace_path(project):
    return project / "CUMCM_Workspace"


def state_path(project):
    return workspace_path(project) / "state" / "pipeline.json"


def load_state(project):
    workspace = workspace_path(project)
    if not workspace.exists():
        raise RuntimeError(f"missing workspace: {workspace}")

    path = state_path(project)
    if not path.exists():
        raise RuntimeError(f"missing pipeline: {path}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid pipeline: {exc}") from exc


def save_state(project, state):
    state["updated_at"] = utc_timestamp()
    path = state_path(project)
    temporary_path = path.with_name(f".{path.name}.tmp")
    temporary_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(path)


def stage_order(state):
    stages = state.get("stages")
    if isinstance(stages, dict) and stages:
        return list(stages.keys())
    return list(STAGES)


def validate_stage(state, stage):
    order = stage_order(state)
    if stage not in order:
        raise ValueError(f"unknown stage: {stage}")
    if "stages" not in state or not isinstance(state["stages"], dict):
        state["stages"] = {}
    if stage not in state["stages"]:
        state["stages"][stage] = initial_stage_state()
    return order


def initial_stage_state():
    return {
        "status": "not_started",
        "started_at": None,
        "completed_at": None,
        "approved_at": None,
        "review_round": 0,
        "notes": "",
    }


def next_stage(order, stage):
    index = order.index(stage)
    if index + 1 < len(order):
        return order[index + 1]
    return stage


def state_file(project, name):
    return workspace_path(project) / "state" / name


def append_text(path, text):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def read_text_if_exists(path):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def cmd_status(args):
    state = load_state(args.project)
    print(f"Current stage: {state.get('current_stage', '')}")
    for stage in stage_order(state):
        stage_state = state.get("stages", {}).get(stage, {})
        print(f"{stage}: {stage_state.get('status', 'not_started')}")
    return 0


def cmd_start_stage(args):
    state = load_state(args.project)
    validate_stage(state, args.stage)
    stage_state = state["stages"][args.stage]
    if stage_state.get("status") != "in_progress":
        stage_state["status"] = "in_progress"
        if not stage_state.get("started_at"):
            stage_state["started_at"] = utc_timestamp()
    state["current_stage"] = args.stage
    save_state(args.project, state)
    return 0


def cmd_request_review(args):
    state = load_state(args.project)
    validate_stage(state, args.stage)
    validate_stage(state, args.next_stage)
    state["stages"][args.stage]["status"] = "pending_review"
    state["current_stage"] = args.stage
    content = (
        f"# Review Request\n\n"
        f"Stage: {args.stage}\n\n"
        f"Summary:\n{args.summary}\n\n"
        f"Next stage: {args.next_stage}\n"
    )
    state_file(args.project, "review_request.md").write_text(content, encoding="utf-8")
    save_state(args.project, state)
    return 0


def approve_stage(state, stage):
    order = validate_stage(state, stage)
    stage_state = state["stages"][stage]
    if stage_state.get("status") != "approved":
        now = utc_timestamp()
        stage_state["status"] = "approved"
        if not stage_state.get("approved_at"):
            stage_state["approved_at"] = now
        if not stage_state.get("completed_at"):
            stage_state["completed_at"] = now
    state["current_stage"] = next_stage(order, stage)


def cmd_approve(args):
    state = load_state(args.project)
    already_approved = state.get("stages", {}).get(args.stage, {}).get("status") == "approved"
    approve_stage(state, args.stage)
    decisions_path = state_file(args.project, "user_decisions.md")
    decisions = read_text_if_exists(decisions_path)
    if not already_approved or args.decision not in decisions:
        append_text(
            decisions_path,
            f"\n## {args.stage} - {utc_timestamp()}\n\n{args.decision}\n",
        )
    save_state(args.project, state)
    return 0


def cmd_rework(args):
    state = load_state(args.project)
    validate_stage(state, args.stage)
    stage_state = state["stages"][args.stage]
    log_path = state_file(args.project, "stage_log.md")
    stage_log = read_text_if_exists(log_path)
    duplicate_rework = stage_state.get("status") == "rework" and args.feedback in stage_log
    stage_state["status"] = "rework"
    if not duplicate_rework:
        stage_state["review_round"] = int(stage_state.get("review_round") or 0) + 1
    state["current_stage"] = args.stage
    if not duplicate_rework:
        append_text(log_path, f"\n## {args.stage} rework - {utc_timestamp()}\n\n{args.feedback}\n")
    save_state(args.project, state)
    return 0


def cmd_advance(args):
    state = load_state(args.project)
    approve_stage(state, args.stage)
    save_state(args.project, state)
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Manage CUMCM pipeline state.")
    parser.add_argument("--project", required=True, type=Path, help="Project root path.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status")
    status.set_defaults(func=cmd_status)

    start_stage = subparsers.add_parser("start-stage")
    start_stage.add_argument("stage")
    start_stage.set_defaults(func=cmd_start_stage)

    request_review = subparsers.add_parser("request-review")
    request_review.add_argument("--stage", required=True)
    request_review.add_argument("--summary", required=True)
    request_review.add_argument("--next", required=True, dest="next_stage")
    request_review.set_defaults(func=cmd_request_review)

    approve = subparsers.add_parser("approve")
    approve.add_argument("--stage", required=True)
    approve.add_argument("--decision", required=True)
    approve.set_defaults(func=cmd_approve)

    rework = subparsers.add_parser("rework")
    rework.add_argument("--stage", required=True)
    rework.add_argument("--feedback", required=True)
    rework.set_defaults(func=cmd_rework)

    advance = subparsers.add_parser("advance")
    advance.add_argument("stage")
    advance.set_defaults(func=cmd_advance)

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        return args.func(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
