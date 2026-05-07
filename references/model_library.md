# Model Library

Use this table to propose routes. Each route should include one simple baseline, one improved route, validation metrics, and risk controls.

| Family | Typical CUMCM tasks | Baseline | Improved route | Validation metric | Main risk |
| --- | --- | --- | --- | --- | --- |
| Optimization and planning | Scheduling, allocation, layout, pricing, routing with constraints | Linear/integer programming or greedy heuristic | Mixed-integer programming, nonlinear programming, dynamic programming, metaheuristic with exact baseline comparison | Feasibility rate, objective value, constraint violation count, runtime | Hidden constraints, unstable objective scaling, infeasible formulation |
| Prediction and regression | Forecast demand, performance, population, environmental indicators | Linear regression, ARIMA, moving average | Regularized regression, tree ensembles, gradient boosting, time-series cross-validation, uncertainty intervals | RMSE, MAE, MAPE, out-of-sample residual checks | Leakage, overfitting, poor extrapolation, nonstationarity |
| Evaluation and decision | Ranking, comprehensive evaluation, risk scoring, site selection | Entropy weight, TOPSIS, z-score scoring | AHP-entropy hybrid, fuzzy comprehensive evaluation, PCA robustness, rank aggregation | Rank stability, weight sensitivity, expert-consistency ratio | Subjective weights, scale effects, correlated indicators |
| Classification and clustering | Type recognition, segmentation, anomaly grouping | k-means, logistic regression, decision tree | Random forest, SVM, DBSCAN, Gaussian mixture, feature selection with validation | Accuracy, F1, silhouette score, confusion matrix, stability under resampling | Label imbalance, arbitrary cluster count, uninterpretable features |
| Graph and network | Transport, supply chain, epidemic/contact networks, influence propagation | Shortest path, minimum spanning tree, max flow | Multi-commodity flow, network robustness, centrality ensemble, community detection | Path cost, flow feasibility, robustness after node or edge removal | Oversimplified topology, ignored capacity, disconnected components |
| Simulation and mechanism | Queues, spread processes, physical mechanisms, policy scenarios | Deterministic equations or Monte Carlo prototype | Agent-based simulation, system dynamics, cellular automata, calibrated mechanism model | Calibration error, confidence interval width, scenario monotonicity, sensitivity | Uncalibrated parameters, stochastic noise, unverifiable mechanism |

## Route Selection Heuristics

- Prefer a transparent baseline even when the improved route is stronger.
- Match model complexity to available data; sparse data usually needs simpler assumptions and stronger sensitivity analysis.
- For each subproblem, state whether the output is a decision, prediction, ranking, explanation, or simulation scenario.
- Avoid stacking models unless each added model improves evidence quality or covers a stated weakness.
- If data quality is weak, route design must include robust checks, missing-data handling, and a fallback interpretation.

## Route Proposal Format

For each candidate route, provide:

- Subproblems covered.
- Baseline model and why it is defensible.
- Improved model and why the extra complexity is justified.
- Required data and preprocessing.
- Verification plan and metrics.
- Figures/tables expected for the paper.
- Key risks and backup plan.
