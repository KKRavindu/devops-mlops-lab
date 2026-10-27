# DevOps + MLOps Practice Lab

A hands-on platform for becoming a **DevOps + MLOps engineer**. You take one real
ML service (a wine-quality classifier) from a Python script to a monitored,
auto-scaling, GitOps-deployed, self-retraining system on Kubernetes, one concept
per lab.

The ML is deliberately simple; the engineering around it is what you practise.

📘 **New here? Start with the [Learner Manual (PDF)](docs/DevOps-MLOps-Lab-Manual.pdf)**:
an introduction to the platform plus a summary of every lab: why it matters, what to do,
key commands, how you know you're done, and common pitfalls.

```
                ┌──────────── Git (single source of truth) ────────────┐
                │   code · params.yaml · Dockerfile · k8s · terraform    │
                └──────┬──────────────────────┬─────────────────────────┘
                       │ push                 │ watch (GitOps)
              ┌────────▼────────┐      ┌──────▼──────┐
  data ──► DVC pipeline ──► MLflow    │   Argo CD    │
  (prepare → train → gate)  registry  └──────┬──────┘
              │ GitHub Actions: lint → test → build → scan → push
              ▼                               ▼
        container image ───────────► Kubernetes (Terraform-managed namespaces)
                                     Deployment · HPA · PDB · canary
                                              │ /metrics      │ predictions.jsonl
                                     Prometheus → Grafana     drift_check.py
                                       alerts                    │ drift?
                                                                 └──► retrain
```

## Repository map

| Path | What it is |
|---|---|
| `src/prepare.py`, `src/train.py` | ML pipeline: data split → train → **quality gate** → model + metadata |
| `src/serve.py` | FastAPI service: `/predict`, `/health`, `/ready`, `/metrics`, fault injection |
| `tests/` | Pipeline and API tests (pytest) |
| `params.yaml`, `dvc.yaml` | Pipeline config and reproducible DAG |
| `Dockerfile` | Multi-stage, non-root image that trains the model during the build |
| `docker-compose.yml` | API + MLflow + Prometheus + Grafana |
| `monitoring/` | Prometheus scrape config, SRE and ML alert rules, Grafana dashboard |
| `k8s/` | Kustomize base + dev/prod overlays, canary, Argo CD app |
| `terraform/` | Namespaces, quotas and limit ranges as code |
| `.github/workflows/` | CI/CD pipeline and continuous-training pipeline |
| `scripts/` | Traffic simulator (with drift) and statistical drift detector |
| `labs/` | **The curriculum. Start here.** |

## Quick start

```bash
make setup      # venv + dependencies
make pipeline   # prepare data + train model
make test       # 11 tests should pass
make serve      # http://localhost:8000/docs
make help       # every command
```

## Curriculum

Work through the labs in order. Each one has **theory → tasks → checkpoint → break-it
drills → interview questions**. Tick them off as you go.

### Phase 1: Foundations
- [ ] [00 – Setup & Git workflow](labs/00-setup.md)
- [ ] [01 – Run, test and understand the app](labs/01-local-app.md)
- [ ] [02 – Docker: images, layers, multi-stage, security](labs/02-docker.md)
- [ ] [03 – Docker Compose: a multi-service stack](labs/03-compose.md)

### Phase 2: Delivery
- [ ] [04 – CI/CD with GitHub Actions](labs/04-ci-cd.md)
- [ ] [05 – Kubernetes fundamentals](labs/05-kubernetes.md)
- [ ] [06 – Kustomize environments, config and scaling](labs/06-kustomize-scaling.md)
- [ ] [07 – Infrastructure as Code with Terraform](labs/07-terraform.md)

### Phase 3: MLOps
- [ ] [08 – Experiment tracking & model registry (MLflow)](labs/08-mlflow.md)
- [ ] [09 – Reproducible pipelines & data versioning (DVC)](labs/09-dvc.md)
- [ ] [10 – Continuous training (CT)](labs/10-continuous-training.md)

### Phase 4: Operate
- [ ] [11 – Observability: metrics, dashboards, alerts](labs/11-observability.md)
- [ ] [12 – Data drift detection & the retraining loop](labs/12-drift.md)
- [ ] [13 – Release strategies: rolling, canary, rollback](labs/13-release-strategies.md)
- [ ] [14 – GitOps with Argo CD](labs/14-gitops.md)
- [ ] [15 – Capstone: incident drills (chaos engineering)](labs/15-capstone-incidents.md)

## Tools you will need

Already on your machine: `docker`, `docker compose`, `kubectl`, `minikube`, `python3`, `git`, `make`.
Installed later in the labs: `terraform` (lab 07), `argocd` CLI (lab 14, optional), a GitHub account (lab 04).

## How to get the most out of this

1. **Type, don't paste.** At least for the first run of each command.
2. **Break things on purpose.** Every lab has a "Break it" section. Debugging is the job.
3. **Write a short note after each lab** in your own words. It becomes your interview prep.
4. **Commit after each lab** so your Git history becomes your portfolio.
5. **Extend it.** The "Challenges" sections are where you become better than the tutorial.
