"""Model serving API (FastAPI).

Endpoints:  /health (liveness)  /ready (readiness)  /model  /predict  /metrics

Env vars:
  MODEL_DIR          where model.joblib + metadata.json live (default: models)
  PREDICTION_LOG     if set, every prediction is appended here as JSONL (used for drift checks)
  FAULT_LATENCY_MS   chaos drill: add artificial latency to /predict
  FAULT_ERROR_RATE   chaos drill: fraction (0-1) of /predict calls that return 500
"""
import json
import logging
import os
import random
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='{"ts":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
log = logging.getLogger("wine-api")

REQUESTS = Counter("api_requests_total", "HTTP requests", ["path", "status"])
LATENCY = Histogram("api_request_latency_seconds", "HTTP request latency", ["path"])
PREDICTIONS = Counter("model_predictions_total", "Predictions by class", ["class_name"])
CONFIDENCE = Histogram(
    "model_prediction_confidence",
    "Max class probability per prediction",
    buckets=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
)
MODEL_INFO = Gauge("model_info", "Currently loaded model", ["version", "model_type"])

state: dict = {}
_log_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_dir = Path(os.getenv("MODEL_DIR", "models"))
    try:
        state["model"] = joblib.load(model_dir / "model.joblib")
        state["meta"] = json.loads((model_dir / "metadata.json").read_text())
        MODEL_INFO.labels(state["meta"]["version"], state["meta"]["model_type"]).set(1)
        log.info(f"loaded model version={state['meta']['version']}")
    except FileNotFoundError:
        log.error(f"no model found in {model_dir} - /ready will return 503")
    yield
    state.clear()


app = FastAPI(title="Wine Classifier API", lifespan=lifespan)


class PredictRequest(BaseModel):
    features: list[list[float]] = Field(..., min_length=1, max_length=1000)


@app.middleware("http")
async def observe(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    path = request.url.path
    LATENCY.labels(path).observe(time.perf_counter() - start)
    REQUESTS.labels(path, str(response.status_code)).inc()
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    if "model" not in state:
        raise HTTPException(503, "model not loaded")
    return {"status": "ready", "model_version": state["meta"]["version"]}


@app.get("/model")
def model_info():
    if "meta" not in state:
        raise HTTPException(503, "model not loaded")
    return state["meta"]


@app.post("/predict")
def predict(req: PredictRequest):
    if "model" not in state:
        raise HTTPException(503, "model not loaded")

    fault_latency = float(os.getenv("FAULT_LATENCY_MS", "0"))
    if fault_latency:
        time.sleep(fault_latency / 1000)
    if random.random() < float(os.getenv("FAULT_ERROR_RATE", "0")):
        raise HTTPException(500, "injected fault")

    meta = state["meta"]
    n_features = len(meta["feature_names"])
    if any(len(row) != n_features for row in req.features):
        raise HTTPException(422, f"every row must have exactly {n_features} features")

    proba = state["model"].predict_proba(np.asarray(req.features))
    labels = proba.argmax(axis=1)
    results = []
    for row, idx, p in zip(req.features, labels, proba, strict=True):
        name = meta["class_names"][idx]
        PREDICTIONS.labels(name).inc()
        CONFIDENCE.observe(float(p.max()))
        results.append({"class": name, "confidence": round(float(p.max()), 4)})
        _log_prediction(row, name, meta["version"])

    return {"model_version": meta["version"], "predictions": results}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _log_prediction(features: list[float], prediction: str, version: str) -> None:
    path = os.getenv("PREDICTION_LOG")
    if not path:
        return
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "features": features,
        "prediction": prediction,
        "model_version": version,
    }
    with _log_lock, open(path, "a") as f:
        f.write(json.dumps(record) + "\n")
