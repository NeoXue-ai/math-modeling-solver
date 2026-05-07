# Paper Structure

Use this when drafting `output/final_paper.md` or `paper/main.tex`. The paper should read from durable artifacts, not from chat memory.

| Section | Purpose | Allowed sources |
| --- | --- | --- |
| 题目 | Match contest problem title or concise modeled title. | Problem statement |
| 摘要 | State methods, key verified results, and conclusions for each subproblem. | Approved registry results, verification summaries, sensitivity report |
| 关键词 | 3-5 domain and method terms. | Modeling route and final paper content |
| 一、问题重述 | Restate background, tasks, objectives, and deliverables without solving them. | Problem statement, attachment descriptions |
| 二、问题分析 | Explain subproblem decomposition and route logic. | `memory/problem_analysis.md`, approved `memory/modeling_route.md` |
| 三、模型假设 | List approved assumptions and justifications. | `memory/assumptions.md`, `state/user_decisions.md` |
| 四、符号说明 | Define variables, parameters, units, and indexes. | Model code, formulas, data audit |
| 五、数据预处理 | Describe data source, cleaning, missingness, outliers, normalization, and feature construction. | `data/data_audit.md`, preprocessing scripts, cleaned data summaries |
| 六、模型建立与求解 | Present formulas, solver process, parameters, and verified results. | `src/models/`, verification reports, approved registry results |
| 七、模型检验与敏感性分析 | Show validation checks, robustness, limitations, and scenario sensitivity. | `reports/verification/`, sensitivity scripts and figures |
| 八、模型评价与推广 | Discuss strengths, weaknesses, applicability, and possible extensions. | Verification findings, sensitivity findings, route risks |
| 参考文献 | Cite standards, datasets, papers, and methods actually used. | Source files and external references used during solution |
| 附录 | Include important code, extra tables, and reproducibility notes. | `src/`, `data/cleaned/`, reports |

## Drafting Rules

- Each subproblem needs a visible answer in the abstract and body.
- Every numeric statement must trace to an approved registry result.
- Every figure path must exist under the workspace before final audit.
- Do not invent data sources, parameter values, or external citations.
- Keep formulas close to variable definitions and explain decision variables before constraints.
- Separate model result interpretation from model limitation discussion.

## Abstract Pattern

Use one compact paragraph per main task:

1. State the modeling method.
2. State the verified result or decision.
3. State robustness, sensitivity, or limitation.
4. End with the overall conclusion or recommended action.
