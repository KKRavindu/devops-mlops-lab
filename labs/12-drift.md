# Lab 12: Data Drift Detection & the Retraining Loop

**Goal:** Detect when production data no longer looks like the training data, and turn
that signal into automated retraining.

## Theory
- **Data drift:** the input distribution P(X) changes (e.g. a sensor gets recalibrated).
  **Concept drift:** the relationship P(y|X) changes. Data drift is detectable without
  labels, and concept drift usually needs labels.
- `scripts/drift_check.py` runs a **Kolmogorov–Smirnov test** per feature (reference =
  training data, current = the prediction log). If more than 20% of features drift at
  p < 0.01, it flags dataset drift and exits 1.
- Exit codes make it composable: cron or CI can do `drift_check || trigger_retrain`.

## Tasks
1. Baseline with no drift:
   ```bash
   rm -f logs/predictions.jsonl
   make traffic
   make drift-check          # expect: no significant dataset drift
   ```
2. Inject drift:
   ```bash
   rm -f logs/predictions.jsonl
   make traffic-drift
   make drift-check; echo "exit code: $?"
   cat drift_report.json | python -m json.tool | head -30
   ```
   Which features drifted? Compare with `drift_cols` in `scripts/simulate_traffic.py`.
3. Find the sensitivity limit: try `--drift 0.05, 0.1, 0.2`. At what point does the test
   notice? How does `--n` (sample size) change that? (This is statistical power.)
4. Close the loop with a script:
   ```bash
   make drift-check || gh workflow run "ML Pipeline"
   ```

## Checkpoint
- A clean run exits 0 and a drifted run exits 1, and you can explain the KS statistic and
  p-value in plain words.

## Challenges
- Run the drift check as a **Kubernetes CronJob** that reads the prediction log
  (hint: share a PVC, or ship logs to object storage).
- Add **PSI** (Population Stability Index) as a second metric and compare it with KS.
- Export drift scores as Prometheus metrics (Pushgateway) and alert on them in Grafana.
- Try **Evidently** to generate an HTML drift report.
- Retrain on *recent* data plus training data and show the drift alert clears.

## Interview questions
- Data drift vs concept drift vs training/serving skew?
- Why might a statistically significant drift not matter to the business?
- How do you choose the reference window?
