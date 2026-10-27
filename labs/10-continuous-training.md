# Lab 10: Continuous Training (CT)

**Goal:** Models retrain automatically on a schedule, on config changes, or on demand,
and only good models get published.

## Theory
- **MLOps maturity levels** (Google): 0 = manual notebooks, 1 = automated training
  pipeline (CT), 2 = automated CI/CD *of the pipeline itself*.
- **Triggers:** schedule, new data, a param/code change, a drift alert (lab 12), or manual.
- **Gates:** the quality gate in `train.py` stops regressions. Real systems also compare
  against the current champion.
- Read `.github/workflows/ml-pipeline.yml`.

## Tasks
1. In GitHub → Actions → **ML Pipeline** → *Run workflow*, choose `logistic_regression`.
2. Open the run summary to see the metrics table, then download the model artefact.
3. Change `max_depth` in `params.yaml`, push to `main`, and confirm the path filter
   triggers retraining.
4. Push a change that makes the gate fail (`min_accuracy: 0.999`). The run goes red and
   no artefact is published.

## Checkpoint
- Three successful runs with different triggers and one correctly blocked run.

## Challenges
- **Champion/challenger gate:** download the previous artefact, compare accuracy, and
  only publish if the new model is at least as good.
- Make the pipeline log to a hosted MLflow (e.g. DagsHub free tier) and register the model.
- Trigger this workflow from the drift detector via `gh workflow run` (closing the loop
  in lab 12).
- Re-implement the pipeline in an orchestrator: **Prefect**, **Airflow**, or **Kubeflow
  Pipelines** on minikube.

## Interview questions
- What triggers retraining in production, and what are the risks of retraining too often?
- How do you prevent a retrained model from being worse than the current one?
- CI vs CD vs CT?
