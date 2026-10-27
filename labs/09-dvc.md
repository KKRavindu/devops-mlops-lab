# Lab 09: Reproducible Pipelines & Data Versioning (DVC)

**Goal:** Version data and models like code, and re-run only what changed.

## Theory
- Git can't hold large datasets or models. **DVC** stores them in remote storage and keeps
  small `.dvc`/`dvc.lock` pointer files (content hashes) in Git.
- `dvc.yaml` defines a **DAG** of stages with deps/params/outs. `dvc repro` skips stages
  whose inputs are unchanged, like `make`, but for ML.
- `dvc.lock` records the exact hashes of each run, so `git checkout <old-commit> && dvc
  checkout` brings back the exact data and model of that commit.

## Tasks
1. Initialise (inside your git repo):
   ```bash
   source .venv/bin/activate
   dvc init
   dvc remote add -d localremote /tmp/dvc-store     # use S3/GCS/MinIO in real life
   git add .dvc dvc.yaml && git commit -m "chore: init dvc"
   ```
2. Run and inspect the pipeline:
   ```bash
   dvc dag
   dvc repro
   git add dvc.lock && git commit -m "ml: baseline model"
   dvc push
   ```
3. See the caching: run `dvc repro` again (nothing runs). Change `train.max_depth` in
   `params.yaml`, run `dvc repro`, and only `train` re-runs.
4. Compare experiments:
   ```bash
   dvc params diff
   dvc metrics diff
   ```
5. Time travel:
   ```bash
   git log --oneline
   git checkout <baseline-commit> -- dvc.lock params.yaml && dvc checkout
   cat models/metadata.json
   ```

## Checkpoint
- `dvc repro` is a no-op on a clean tree, and you can restore a past model from Git history.

## Break it
- Delete `models/` and run `dvc checkout`. It comes back from the cache.
- Edit `data/train.csv` by hand and run `dvc status`.

## Challenges
- Use `dvc exp run -S train.n_estimators=200` to run experiments without committing.
- Add a CI step that runs `dvc repro` and posts `dvc metrics diff main` as a PR comment (CML).

## Interview questions
- How do you version a 50 GB dataset?
- How does DVC decide what to re-run?
- DVC vs MLflow: overlap and differences?
