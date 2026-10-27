SHELL := /bin/bash
PY    := .venv/bin/python
IMAGE ?= wine-api
TAG   ?= latest
ENV   ?= dev
# Keep the venv isolated from system packages (e.g. ROS adds its own to PYTHONPATH).
unexport PYTHONPATH

.DEFAULT_GOAL := help
.PHONY: help setup data train pipeline test lint fmt serve \
        docker-build docker-run up down logs traffic traffic-drift drift-check \
        k8s-start k8s-load k8s-deploy k8s-status k8s-forward k8s-delete clean

help: ## Show all commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ---------- Local development ----------
setup: ## Create .venv and install all dependencies
	python3 -m venv .venv
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements.txt -r requirements-dev.txt

data: ## Pipeline stage 1: prepare train/test data
	$(PY) -m src.prepare

train: ## Pipeline stage 2: train + quality gate
	$(PY) -m src.train

pipeline: data train ## Run full ML pipeline

test: ## Run unit + API tests
	$(PY) -m pytest -q

lint: ## Lint with ruff
	$(PY) -m ruff check .

fmt: ## Auto-format with ruff
	$(PY) -m ruff format . && $(PY) -m ruff check --fix .

serve: ## Run API locally with hot reload
	mkdir -p logs
	PREDICTION_LOG=logs/predictions.jsonl $(PY) -m uvicorn src.serve:app --reload --port 8000

# ---------- Docker ----------
docker-build: ## Build the container image
	docker build -t $(IMAGE):$(TAG) --build-arg MODEL_VERSION=$(TAG) .

docker-run: ## Run the image standalone on :8000
	docker run --rm -p 8000:8000 --name wine-api $(IMAGE):$(TAG)

up: ## Start full stack (api, mlflow, prometheus, grafana)
	mkdir -p logs && chmod 777 logs
	docker compose up -d --build
	@echo "API http://localhost:8000/docs | MLflow :5000 | Prometheus :9090 | Grafana :3000"

down: ## Stop the stack
	docker compose down

logs: ## Tail API logs
	docker compose logs -f api

traffic: ## Send normal traffic
	$(PY) scripts/simulate_traffic.py --n 300

traffic-drift: ## Send DRIFTED traffic
	$(PY) scripts/simulate_traffic.py --n 300 --drift 0.6

drift-check: ## Compare live predictions to training data
	$(PY) scripts/drift_check.py --log logs/predictions.jsonl

# ---------- Kubernetes (minikube) ----------
k8s-start: ## Start minikube with metrics-server
	minikube start --cpus 4 --memory 6g
	minikube addons enable metrics-server

k8s-load: docker-build ## Load local image into minikube
	minikube image load $(IMAGE):$(TAG)

k8s-deploy: ## Deploy overlay (ENV=dev|prod)
	kubectl create namespace wine-$(ENV) --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -k k8s/overlays/$(ENV)
	kubectl -n wine-$(ENV) rollout status deploy/wine-api --timeout=120s

k8s-status: ## Show resources in the namespace
	kubectl -n wine-$(ENV) get deploy,rs,pods,svc,hpa,pdb

k8s-forward: ## Port-forward service to localhost:8080
	kubectl -n wine-$(ENV) port-forward svc/wine-api 8080:80

k8s-delete: ## Delete the overlay
	kubectl delete -k k8s/overlays/$(ENV) --ignore-not-found

clean: ## Remove generated artifacts
	rm -rf data models logs metrics.json drift_report.json .pytest_cache .ruff_cache
