---
name: math-modeling-solver
description: >
  CUMCM-first mathematical modeling competition workflow skill. Use when the user
  provides a Chinese mathematical modeling contest problem and wants a rigorous,
  auditable workflow from problem parsing to model selection, real solver code,
  verification, sensitivity analysis, and paper drafting. Enforces human approval
  at model route, assumptions, and result-to-paper checkpoints; forbids using
  unverified numerical results in papers.
---

# math-modeling-solver

## Purpose

Run a CUMCM-first, verification-gated mathematical modeling workflow. This skill is a rigorous workflow controller, not a black-box paper generator.

## First Action On Every Invocation

Resolve bundled scripts relative to this skill directory. Run `python scripts/pipeline_manager.py --project <project-root> status` if `CUMCM_Workspace/state/pipeline.json` exists. Also run `python scripts/problem_source_gate.py --project <project-root> status` to inspect problem source metadata.

If the workspace does not exist, ask for the problem file or pasted statement, attachment path if any, whether this is an official problem or mock problem, and existing model preference if any. Then run `python scripts/setup_workspace.py --project <project-root>`.

Before `problem_parse`, record the problem source in `CUMCM_Workspace/memory/problem_source.json` and run `python scripts/problem_source_gate.py --project <project-root> validate`. If validation blocks, stop and ask for source evidence. Do not infer or fabricate a problem statement.

Never claim a year, contest, A/B/C problem code, official title, attachment list, or data description unless it appears in a user-provided source file or pasted statement. If the user asks for a not-yet-provided official CUMCM problem, ask for the original statement or treat it explicitly as a mock problem.

## Stage Flow

Follow this order: `problem_parse`, `model_route_review`, `assumption_review`, `data_audit`, `data_preprocess`, `model_build`, `model_verify`, `sensitivity_analysis`, `result_review`, `paper_draft`, `paper_quality_audit`, `final_compile`, `complete`.

Each stage must leave recoverable artifacts under `CUMCM_Workspace/`. Do not skip stages based on chat memory.

## Problem Source Gate

`CUMCM_Workspace/memory/problem_source.json` is mandatory. The source type must be one of `official_file`, `pasted_statement`, or `mock_problem`; `unknown` blocks modeling. Official contest claims require source evidence. A missing, unreadable, or empty statement file blocks `problem_parse`.

## Human Checkpoints

Stop for user approval at `model_route_review`, `assumption_review`, and `result_review`. Record each decision in `CUMCM_Workspace/state/user_decisions.md` through `pipeline_manager.py approve`.

Use `pipeline_manager.py request-review` to summarize the proposed route, assumptions, or paper-ready results before asking. Use `pipeline_manager.py rework` when the user asks for changes.

## Verification Gates

Before `result_review`, run `quality_gate.py model-verify` for every report under `CUMCM_Workspace/reports/verification/`. A failed report blocks progress.

Before `final_compile`, run `quality_gate.py paper-audit`. Then run `compile_paper.py`; if `xelatex` is unavailable, keep the Markdown paper in `CUMCM_Workspace/output/final_paper.md`.

## Paper Boundary

The paper may use only results listed in `CUMCM_Workspace/memory/result_registry.json` with `verification_status` equal to `PASS` and `approved_for_paper` equal to `true`.

Do not place numerical claims, rankings, fitted parameters, objective values, or figure references into the paper unless they can be traced to executable code, a verification report, and the result registry.

## References

Read `references/cumcm_workflow.md` when resuming or deciding stage outputs. Read `references/model_library.md` when choosing models. Read `references/verification_rules.md` before writing verification scripts. Read `references/paper_structure.md` before drafting the paper. Read `references/scoring_rubric.md` before final audit.
