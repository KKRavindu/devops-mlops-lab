# Lab 11: Observability (Metrics, Dashboards, Alerts)

**Goal:** Know the health of both the *service* and the *model* at a glance, and get
paged before users notice.

## Theory
- **Three pillars:** metrics (Prometheus), logs (structured JSON), traces (OpenTelemetry).
- **Golden signals:** latency, traffic, errors, saturation. **RED** for services:
  Rate, Errors, Duration.
- **ML adds a fourth dimension:** a model can return HTTP 200 with garbage. Monitor the
  *prediction distribution* and *confidence* too (`model_predictions_total`,
  `model_prediction_confidence`).
- **SLI / SLO / error budget:** SLI = "% of /predict under 300 ms with non-5xx", SLO = 99.5%
  over 30 days, and the error budget = the 0.5% you're allowed to burn.
- Use histograms (not averages) for latency and percentiles (`histogram_quantile`).

## Tasks
1. `make up && make traffic`. Then in Prometheus (http://localhost:9090), run these:
   ```promql
   sum(rate(api_requests_total{path="/predict"}[1m]))
   histogram_quantile(0.95, sum by (le) (rate(api_request_latency_seconds_bucket{path="/predict"}[1m])))
   sum by (class_name) (rate(model_predictions_total[5m]))
   ```
2. Look at http://localhost:9090/alerts and read every rule in `monitoring/alert_rules.yml`.
3. **Fire HighErrorRate:**
   ```bash
   FAULT_ERROR_RATE=0.2 docker compose up -d api
   .venv/bin/python scripts/simulate_traffic.py --n 2000 --rps 20
   ```
   Watch the alert go *pending* → *firing* and the Grafana error panel go red. Reset with
   `docker compose up -d api`.
4. **Fire HighLatencyP95** with `FAULT_LATENCY_MS=700`.
5. **Fire an ML alert:** `make traffic-drift` with more requests (`--n 2000 --drift 1.5`).
   Watch confidence drop and class skew rise, while the service looks perfectly healthy.

## Checkpoint
- You triggered at least one service alert and one model alert, and you can explain each
  PromQL expression.

## Challenges
- Add an SLO recording rule and a **multi-window burn-rate alert**.
- Add Loki + Promtail for logs and correlate them with metrics in Grafana.
- Instrument with OpenTelemetry and view traces in Jaeger or Tempo.
- In Kubernetes, install `kube-prometheus-stack` with Helm and add a ServiceMonitor.

## Interview questions
- Counter vs gauge vs histogram vs summary?
- Why alert on symptoms (user-facing) rather than causes (CPU)?
- How do you monitor an ML model when ground-truth labels arrive days later?
