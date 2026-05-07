# Paper Structure

Use this when drafting `output/final_paper.md` or `paper/main.tex`. The paper should read from durable artifacts, not from chat memory.

The default LaTeX asset is `assets/cumcm_template.tex`. It is a CUMCM-like template built on `ctexart`, not on external classes such as `cumcmthesis`, so it can compile in more environments.

## Required Style

- Use 逐问题摘要: one compact abstract paragraph for each subproblem.
- Use competition-style sections: 问题重述, 问题分析, 模型假设, 符号说明, 数据预处理, 模型的建立与求解, 模型的检验与敏感性分析, 模型的评价与改进, 参考文献, 附录.
- In 模型的建立与求解, each subproblem should use the pattern: 模型建立, 模型求解, 求解结果.
- Include a 符号说明表 using `tabularx` and `booktabs`.
- Include result tables and figures only when their source files exist and their values are approved in `result_registry.json`.
- Include 附录 with 文件列表 and 代码附录.

## Section Sources

| Section | Purpose | Allowed sources |
| --- | --- | --- |
| 题目与封面 | Match contest problem title, problem number, team metadata. | Problem statement, user-provided metadata |
| 摘要 | State methods, key verified results, and conclusions for each subproblem. | Approved registry results, verification summaries, sensitivity report |
| 关键词 | 3-5 domain and method terms. | Modeling route and final paper content |
| 问题重述 | Restate background, tasks, objectives, and deliverables without solving them. | Problem statement, attachment descriptions |
| 问题分析 | Explain subproblem decomposition and route logic. | `memory/problem_analysis.md`, approved `memory/modeling_route.md` |
| 模型假设 | List approved assumptions and justifications. | `memory/assumptions.md`, `state/user_decisions.md` |
| 符号说明 | Define variables, parameters, units, and indexes. | Model code, formulas, data audit |
| 数据预处理 | Describe data source, cleaning, missingness, outliers, normalization, and feature construction. | `data/data_audit.md`, preprocessing scripts, cleaned data summaries |
| 模型的建立与求解 | Present formulas, solver process, parameters, and verified results for each subproblem. | `src/models/`, verification reports, approved registry results |
| 模型的检验与敏感性分析 | Show validation checks, robustness, limitations, and scenario sensitivity. | `reports/verification/`, sensitivity scripts and figures |
| 模型的评价与改进 | Discuss strengths, weaknesses, applicability, and possible extensions. | Verification findings, sensitivity findings, route risks |
| 参考文献 | Cite standards, datasets, papers, and methods actually used. | Source files and external references used during solution |
| 附录 | Include 文件列表, code appendix, extra tables, and reproducibility notes. | `src/`, `data/cleaned/`, reports |

## Drafting Rules

- Each subproblem needs a visible answer in the abstract and body.
- Every numeric statement must trace to an approved registry result.
- Every figure path must exist under the workspace before final audit.
- Do not invent data sources, parameter values, or external citations.
- Keep formulas close to variable definitions and explain decision variables before constraints.
- Separate model result interpretation from model limitation discussion.
- Prefer tables with `booktabs` and `tabularx`; avoid raw, oversized data dumps.
- For paired plots, use side-by-side `minipage` or `subcaption` only when both figures exist.

## Abstract Pattern

Use one compact paragraph per main task:

1. Start with `针对问题一/二/三/四`.
2. State the modeling method.
3. State the verified result or decision.
4. State robustness, sensitivity, or limitation.
5. End with the overall conclusion or recommended action.

## Result-To-Paper Boundary

- The paper may cite a result as `R1`, `R2`, etc. only when that ID exists in `memory/result_registry.json`.
- The registry entry must have `verification_status: PASS` and `approved_for_paper: true`.
- The registry entry's `verification_report` must point to a report that parses and passes.
- If a value is not in the registry, keep it out of the abstract, result tables, conclusions, and figures.
