# Scoring Rubric Alignment

Use this before `paper_quality_audit` to make sure scoring evidence appears in the paper.

| Scoring point | Evidence required | Paper location |
| --- | --- | --- |
| Problem understanding | Accurate task decomposition, objectives, constraints, and deliverables. | 问题重述, 问题分析 |
| Assumption quality | Necessary assumptions with justification and likely effect. | 模型假设 |
| Data handling | Clear data audit, preprocessing, missing-value treatment, and unit consistency. | 数据预处理, 附录 |
| Model appropriateness | Baseline and improved models match each subproblem and data scale. | 问题分析, 模型建立与求解 |
| Mathematical rigor | Variables, objective functions, constraints, derivations, and algorithm steps are coherent. | 符号说明, 模型建立与求解 |
| Computational reproducibility | Code paths, parameters, seeds, and outputs can be rerun. | 附录, 验证报告 |
| Verification strength | Independent checks pass, baseline comparisons are shown, and sensitivity is discussed. | 模型检验与敏感性分析 |
| Result usability | Answers are concrete, interpretable, and tied to contest questions. | 摘要, 模型建立与求解, 结论-style paragraphs |
| Paper clarity | Figures, tables, formulas, and text are consistent and readable. | 全文 |
| Innovation or extension | Improved route or scenario extension adds defensible value beyond the baseline. | 模型评价与推广 |

## Final Audit Questions

- Does the abstract answer every subproblem with approved evidence?
- Are all assumptions approved and used consistently?
- Can each table, figure, and number be traced to code and registry entries?
- Are weak data quality, model limits, and sensitivity findings stated honestly?
- Would a reviewer understand why the selected model is better than the baseline?
- Are all referenced figures present and readable?
- Is the appendix sufficient for reproducing core computations?
