# Lab 04: CI/CD with GitHub Actions

**Goal:** Every push is automatically linted, tested, built, scanned and smoke-tested,
and every merge to `main` produces a versioned image in a registry.

## Theory
- **CI** = integrate small changes often and verify them automatically.
  **CD** = every verified change is releasable (delivery) or released (deployment).
- **Shift-left security:** scan images (Trivy) in CI and fail on HIGH/CRITICAL CVEs.
- **Immutable, traceable artefacts:** images are tagged `sha-<commit>`, never just
  `latest`, so you always know what code is running.
- Read `.github/workflows/ci.yml`: `lint-test` → `build-scan-push` → `gitops-bump`.

## Tasks
1. Push the repo (lab 00) and open the **Actions** tab. Watch the `CI` run.
2. Repo Settings → Actions → General → Workflow permissions: **Read and write** (needed
   to push to GHCR and for the GitOps commit).
3. After a green run on `main`, find the image under your GitHub profile → **Packages**.
   Pull it: `docker pull ghcr.io/<you>/wine-api:sha-xxxxxxx`
4. Open a PR that breaks a test (e.g. change the expected class in `tests/test_api.py`).
   Confirm CI fails and blocks the merge (add the required status check to branch protection).
5. Run the CI steps locally before pushing:
   `make lint && make test && make docker-build`

## Checkpoint
- Green pipeline on `main`, an image in GHCR tagged with the commit SHA, and a red PR that
  could not be merged.

## Break it
- Set `min_accuracy: 0.999` in a PR. Which job fails, and why is that good?
- Add a known-vulnerable dependency (e.g. `pyyaml==5.3`) and watch Trivy catch it.

## Challenges
- Add a **matrix** to test Python 3.10/3.11/3.12.
- Add test coverage with `pytest-cov` and fail below 80%.
- Generate an SBOM (`anchore/sbom-action`) and sign the image with **cosign**.
- Add a `pre-commit` config that runs ruff locally.

## Interview questions
- Continuous delivery vs continuous deployment?
- How do you speed up a slow pipeline? (caching, parallel jobs, path filters, smaller images)
- Where should secrets live in CI, and what is OIDC federation?
