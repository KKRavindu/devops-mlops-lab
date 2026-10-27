# Lab 01: Run, Test and Understand the App

**Goal:** Understand exactly what you will be operating: the ML pipeline, the API
contract, and the tests that guard both.

## Theory
- An ML system has **two artefacts**: code and a *trained model*. The model is the output
  of code + data + params. Change any of those and you get a different model.
- **Quality gate:** `train.py` refuses to save a model below `min_accuracy`. This is the
  ML equivalent of "tests must pass before deploy".
- **Liveness vs readiness:** `/health` means "the process is alive". `/ready` means "I can
  serve traffic" (the model is loaded). Kubernetes uses them differently (lab 05).

## Tasks
1. Run the pipeline and inspect the outputs:
   ```bash
   make pipeline
   head -3 data/train.csv
   cat models/metadata.json
   cat metrics.json
   ```
2. Run the tests and lint:
   ```bash
   make test
   make lint
   ```
3. Start the API and explore it:
   ```bash
   make serve          # in terminal 1
   curl localhost:8000/health
   curl localhost:8000/ready
   curl localhost:8000/model | python -m json.tool
   curl -X POST localhost:8000/predict -H 'Content-Type: application/json' \
     -d '{"features":[[13.2,1.78,2.14,11.2,100,2.65,2.76,0.26,1.28,4.38,1.05,3.4,1050]]}'
   curl -s localhost:8000/metrics | grep -E '^(api|model)_'
   ```
   Also open http://localhost:8000/docs for the interactive Swagger UI.
4. Generate load and watch the prediction log grow:
   ```bash
   make traffic
   wc -l logs/predictions.jsonl && tail -1 logs/predictions.jsonl
   ```

## Checkpoint
- All tests pass, and you can explain what each test protects against.
- You can explain every metric family exposed on `/metrics`.

## Break it
- Set `min_accuracy: 0.99` in `params.yaml` and run `make train`. What exit code do you
  get, and why does that matter for CI?
- Delete `models/` and start the API. What do `/health` and `/ready` return? Why is that
  the correct behaviour?
- Send 12 features instead of 13. What status code comes back?

## Challenges
- Add a `/predict` request-ID header that gets echoed in the logs.
- Add a test asserting `/predict` latency is under 50 ms for a single row.

## Interview questions
- Why should training fail loudly (non-zero exit) instead of saving a bad model?
- What is the difference between liveness and readiness?
- What is training/serving skew?
