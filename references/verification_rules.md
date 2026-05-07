# Verification Rules

Every model output that may enter the paper needs a structured report under `CUMCM_Workspace/reports/verification/`.

## Report Format

```text
VERIFICATION REPORT
model: <model_name>
status: PASS
checks:
- id: <check_id>
  status: PASS
  detail: <specific evidence>
approved_for_paper: true
```

Use `status: FAIL` or `approved_for_paper: false` when any required evidence is missing. The quality gate accepts only reports where the top-level status, every check, and the approval flag pass.

## General Checks

- Re-run the exact script or command that produced the result.
- Record input data versions, random seeds, parameters, and runtime-relevant settings.
- Confirm units and dimensions for every table column used in formulas.
- Compare against a simple baseline or hand-checkable case.
- Check that saved figures and tables match the registry values.

## Optimization and Planning

- Constraint satisfaction: all hard constraints have zero or documented tolerance-level violations.
- Objective recomputation: recompute the objective from the returned decision variables.
- Baseline comparison: compare against greedy or relaxed solution.
- Feasibility stress: perturb key limits and verify expected objective direction.
- Runtime: record solver status, optimality gap if any, and timeout behavior.

## Prediction and Regression

- Data split: show train/validation/test or time-based split with no leakage.
- Residual checks: inspect residual bias, extreme errors, and heteroscedasticity where relevant.
- Metric report: include MAE/RMSE/MAPE or task-appropriate metrics.
- Baseline comparison: beat a simple mean, moving average, or linear baseline.
- Extrapolation warning: flag predictions outside the observed data range.

## Evaluation and Decision

- Indicator direction: confirm benefit/cost direction for every indicator.
- Normalization: record method and check that scales are comparable.
- Weight sensitivity: vary key weights and report rank changes.
- Consistency: for AHP, report consistency ratio; for subjective scores, record source.
- Rank stability: compare at least one alternate weighting or aggregation method.

## Clustering and Classification

- Feature audit: list features and transformations used by the model.
- Split or resampling: use validation split, cross-validation, bootstrap, or stability check.
- Metric report: classification uses confusion matrix and F1/accuracy; clustering uses silhouette or stability.
- Class or cluster interpretation: describe what separates groups in domain terms.
- Imbalance handling: report class distribution and any weighting/resampling.

## Graph and Network

- Topology validation: confirm node and edge counts, directionality, weights, and connectivity.
- Constraint check: verify capacities, conservation, and path feasibility when applicable.
- Baseline comparison: compare shortest path, max flow, or centrality baseline.
- Robustness: remove or perturb important nodes/edges and report impact.
- Visualization audit: ensure graph figures label the modeled network clearly.

## Simulation and Mechanism

- Parameter source: document every calibrated, measured, or assumed parameter.
- Randomness control: set seeds and report run count for stochastic simulation.
- Calibration: compare simulated outputs to observed or known reference values.
- Scenario monotonicity: check that parameter changes move outputs in plausible directions.
- Uncertainty: report confidence intervals or percentile ranges for stochastic results.
