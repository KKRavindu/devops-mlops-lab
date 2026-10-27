# Lab 08: Experiment Tracking & Model Registry (MLflow)

**Goal:** Every training run is recorded (params, metrics, artefact), and models get
versioned in a registry with aliases like `champion` and `challenger`.

## Theory
- Without tracking, "which model is in prod and how was it trained?" is unanswerable.
- **Experiment tracking:** a run stores params + metrics + artefacts + code version.
- **Model registry:** a named model (`wine-classifier`) with numbered versions and aliases.
  Deployments reference an alias, and promotion = moving the alias.
- `train.py` logs to MLflow only when `MLFLOW_TRACKING_URI` is set, so the same code works
  in CI, Docker and locally.

## Tasks
1. Make sure MLflow is running (`make up`), then train several variants:
   ```bash
   export MLFLOW_TRACKING_URI=http://localhost:5000
   make train
   TRAIN_MODEL=logistic_regression make train
   ```
   Edit `params.yaml` (e.g. `n_estimators: 10`, `max_depth: 2`) and train again.
2. In http://localhost:5000, compare runs side by side (select runs → Compare) and sort by
   accuracy.
3. Open **Models → wine-classifier**. Set alias `champion` on the best version and
   `challenger` on another.
4. Load a model by alias from Python:
   ```python
   import mlflow
   mlflow.set_tracking_uri("http://localhost:5000")
   m = mlflow.sklearn.load_model("models:/wine-classifier@champion")
   print(m)
   ```

## Checkpoint
- At least 4 runs, a registry with 3+ versions, and a `champion` alias you can load.

## Break it
- Train with the MLflow server stopped. What happens? Should training fail or continue
  when tracking is down? Argue both sides.

## Challenges
- Change `serve.py` to load `models:/wine-classifier@champion` from MLflow when
  `MLFLOW_MODEL_URI` is set, so promotion no longer needs a rebuild.
- Log the git commit SHA and the data hash as run tags.
- Write a `promote.py` that sets `champion` only if the challenger beats it on the test set.
- Use MinIO (S3) as the MLflow artefact store, like production setups do.

## Interview questions
- What do you need to reproduce a model exactly?
- How do you promote a model from staging to production safely?
- Baking the model into the image vs loading it from a registry at start-up: trade-offs?
