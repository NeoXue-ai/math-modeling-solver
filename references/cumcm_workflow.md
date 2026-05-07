# CUMCM Workflow Reference

Use this file to decide what each stage must consume, produce, and review. Keep all durable outputs inside `CUMCM_Workspace/`.

## Stage Responsibilities

| Stage | Entry artifacts | Required work | Exit artifacts | Stop? |
| --- | --- | --- | --- | --- |
| `problem_parse` | Passing `problem_source_gate`, problem statement, attachments | Extract tasks, objectives, constraints, deliverables, data files, units, and implicit assumptions. | `memory/problem_analysis.md` | No |
| `model_route_review` | Problem analysis, data audit preview | Propose 2-3 routes with baseline model, improved model, validation plan, evidence, and risks. | `memory/modeling_route.md`, `state/review_request.md` | Yes |
| `assumption_review` | Approved route | Draft assumptions with justification, affected variables, and expected effect on results. | `memory/assumptions.md`, `state/review_request.md` | Yes |
| `data_audit` | Raw data, attachments | Inspect schema, missingness, outliers, units, encoding, sampling period, and leakage risks. | `data/data_audit.md` | No |
| `data_preprocess` | Audit notes, raw data | Write reproducible cleaning code; preserve raw files; save cleaned data and preprocessing notes. | `data/cleaned/`, preprocessing script or notebook | No |
| `model_build` | Approved assumptions, cleaned data | Implement solver code for each subproblem; save outputs deterministically. | `src/models/`, model outputs, figures | No |
| `model_verify` | Solver outputs | Run independent checks and write one structured report per model or subproblem. | `reports/verification/*.md` | Gate |
| `sensitivity_analysis` | Verified model code | Vary key parameters and data perturbations; record robustness and failure ranges. | Sensitivity report, figures | No |
| `result_review` | Verification and sensitivity reports | Summarize registry results, figures, limitations, and paper inclusion candidates. | Updated `memory/result_registry.json`, `state/review_request.md` | Yes |
| `paper_draft` | Approved registry results, paper structure reference | Draft Chinese paper with traceable claims and figure references. | `output/final_paper.md`, optional `paper/main.tex` | No |
| `paper_quality_audit` | Draft paper, registry, figures | Run paper gate; repair missing evidence, placeholders, broken figure paths, and inconsistencies. | `reports/qa_report.md` | Gate |
| `final_compile` | Audited paper | Compile LaTeX if available; preserve Markdown fallback. | `output/final_paper.pdf` or Markdown output | No |
| `complete` | Final outputs | Summarize deliverables and residual risks. | Final status | No |

## Approval Rules

- At approval stages, write a concise review request before asking the user.
- Do not continue past `model_route_review`, `assumption_review`, or `result_review` until the user confirms or edits the proposal.
- Record the user decision with `pipeline_manager.py approve --stage <stage> --decision <text>`.
- If the user rejects a proposal, record feedback with `pipeline_manager.py rework --stage <stage> --feedback <text>` and revise only the affected artifacts.

## Artifact Discipline

- `memory/problem_source.json` is the source of truth for whether the problem statement is official, pasted, or mock. If it is `unknown`, stop before `problem_parse`.
- Do not invent contest year, problem code, title, data files, or subproblem text. Extract them only from source evidence.
- Conversation memory is not a source of truth. Durable files under `CUMCM_Workspace/` are.
- Every figure in the paper must exist under the workspace and be listed by an approved registry result or an audited paper section note.
- Every reported number should be reproducible from `src/`, data files, and a verification report.
