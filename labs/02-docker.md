# Lab 02: Docker (Images, Layers, Multi-stage, Security)

**Goal:** Package the service into a small, secure, reproducible image.

## Theory
- **Layers & cache:** each instruction is a layer. `COPY requirements.txt` comes *before*
  `COPY src/`, so editing code doesn't reinstall dependencies.
- **Multi-stage builds:** our `Dockerfile` has three stages: `base` (deps), `trainer`
  (trains the model), and `runtime` (copies only the model and the code). Training tools
  and data never reach production.
- **Security basics:** non-root user (`USER 10001`), slim base, no secrets in layers,
  `.dockerignore` to keep the build context small, and a `HEALTHCHECK`.
- **Trade-off to think about:** training inside `docker build` is reproducible and simple,
  but in large systems the model comes from a **registry** (lab 08) and is loaded at
  start-up or baked in by CI. Why?

## Tasks
1. Build and run:
   ```bash
   make docker-build
   docker images wine-api
   make docker-run           # then curl localhost:8000/ready in another terminal
   ```
2. Inspect what you built:
   ```bash
   docker history wine-api:latest
   docker inspect wine-api:latest --format '{{.Config.User}} {{json .Config.Healthcheck}}'
   docker run --rm wine-api:latest id          # should NOT be root
   ```
3. Observe the cache: change a comment in `src/serve.py`, rebuild, and note which steps
   say `CACHED`. Then change `requirements.txt` and compare.
4. Build only the trainer stage: `docker build --target trainer -t wine-trainer .`
5. Build a variant model: `docker build --build-arg TRAIN_MODEL=logistic_regression --build-arg MODEL_VERSION=v2 -t wine-api:v2 .`
   (you will need this image in lab 13).
6. Scan for vulnerabilities (install [trivy](https://trivy.dev) or use the container):
   ```bash
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.56.2 image --severity HIGH,CRITICAL wine-api:latest
   ```

## Checkpoint
- The image runs as UID 10001, `docker ps` shows `(healthy)`, and you can explain each stage.

## Break it
- Move `COPY src/ src/` above `pip install` and time two rebuilds. Explain the difference.
- Remove `.dockerignore` and check the "transferring context" size.
- Add `ENV API_KEY=secret` and find it again with `docker history --no-trunc`. Lesson: never.

## Challenges
- Try a `python:3.11-slim` vs `distroless` vs `alpine` runtime and compare size and CVEs.
- Pin the base image by digest (`python:3.11-slim@sha256:...`). Why do teams do this?

## Interview questions
- CMD vs ENTRYPOINT? `COPY` vs `ADD`?
- Why run containers as non-root? What does `readOnlyRootFilesystem` add on top?
- How do you keep images small and builds fast?
