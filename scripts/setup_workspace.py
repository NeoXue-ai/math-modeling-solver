#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_DIRS = [
    "problem/attachments",
    "state",
    "memory",
    "data/raw",
    "data/cleaned",
    "src/models",
    "src/verification",
    "reports/verification",
    "figures",
    "paper/sections",
    "output",
]

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

SEED_TEXT_FILES = {
    "state/review_request.md": "# Review Request\n\nNo review is pending.\n",
    "state/user_decisions.md": "# User Decisions\n\nNo decisions recorded.\n",
    "state/stage_log.md": "# Stage Log\n\n",
    "memory/problem_analysis.md": "# Problem Analysis\n\n",
    "memory/modeling_route.md": "# Modeling Route\n\n",
    "memory/assumptions.md": "# Assumptions\n\n",
    "data/data_audit.md": "# Data Audit\n\n",
}

RESULT_REGISTRY = {"schema_version": 1, "results": []}


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def initial_stage_state():
    return {
        "status": "not_started",
        "started_at": None,
        "completed_at": None,
        "approved_at": None,
        "review_round": 0,
        "notes": "",
    }


def initial_pipeline_state():
    now = utc_timestamp()
    return {
        "schema_version": 1,
        "contest": "CUMCM",
        "mode": "HYBRID",
        "created_at": now,
        "updated_at": now,
        "current_stage": "problem_parse",
        "stages": {stage: initial_stage_state() for stage in STAGES},
    }


def write_text_if_absent(path, content):
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def write_json_if_absent(path, payload):
    if not path.exists():
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def setup_workspace(project):
    workspace = project / "CUMCM_Workspace"
    for relative_dir in WORKSPACE_DIRS:
        (workspace / relative_dir).mkdir(parents=True, exist_ok=True)

    write_json_if_absent(workspace / "state" / "pipeline.json", initial_pipeline_state())
    write_json_if_absent(workspace / "memory" / "result_registry.json", RESULT_REGISTRY)

    for relative_file, content in SEED_TEXT_FILES.items():
        write_text_if_absent(workspace / relative_file, content)

    return workspace


def parse_args():
    parser = argparse.ArgumentParser(description="Initialize a CUMCM workspace.")
    parser.add_argument("--project", required=True, type=Path, help="Project root path.")
    return parser.parse_args()


def main():
    args = parse_args()
    workspace = setup_workspace(args.project)
    print(f"Workspace ready: {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
