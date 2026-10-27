# Lab 03: Docker Compose (A Multi-service Stack)

**Goal:** Run the whole platform locally: API, MLflow, Prometheus and Grafana on one
network, with service discovery by name.

## Theory
- Compose gives each project a **network** where services resolve each other by name.
  That's why Prometheus scrapes `api:8000`, not `localhost:8000`.
- **Volumes:** a bind mount (`./logs`) shares host files. A named volume (`mlflow-data`)
  is managed by Docker and survives `down` (but not `down -v`).
- **Config via env vars** (12-factor): fault injection is toggled with
  `FAULT_LATENCY_MS` and `FAULT_ERROR_RATE` without rebuilding.

## Tasks
1. Start everything:
   ```bash
   make up
   docker compose ps
   ```
   Open: API http://localhost:8000/docs, MLflow http://localhost:5000,
   Prometheus http://localhost:9090/targets (the target should be **UP**), and Grafana
   http://localhost:3000 → Dashboards → MLOps Lab.
2. Send traffic and watch the dashboard move: `make traffic`
3. Explore networking:
   ```bash
   docker compose exec prometheus wget -qO- http://api:8000/health
   docker network ls | grep mlops-lab
   ```
4. Change config without rebuilding:
   ```bash
   FAULT_LATENCY_MS=300 docker compose up -d api
   make traffic           # watch p95 latency in Grafana
   docker compose up -d api   # back to normal
   ```
5. Tail logs: `make logs`. Notice the JSON-structured log lines.

## Checkpoint
- All four services are healthy, the Grafana dashboard shows live data, and you can explain
  why `localhost` inside a container is not your laptop.

## Break it
- Stop the API (`docker compose stop api`). How long until the `ApiDown` alert fires at
  http://localhost:9090/alerts? Start it again.
- Run `docker compose down -v` and observe what MLflow loses.

## Challenges
- Add **Alertmanager** to the stack and route alerts to a webhook (try https://webhook.site).
- Add **cAdvisor** to get container CPU/memory metrics in Prometheus.
- Add `healthcheck:` + `depends_on: condition: service_healthy` for the API.

## Interview questions
- Bind mount vs named volume?
- How does service discovery work in Compose? In Kubernetes?
- Why is Compose not a production orchestrator?
