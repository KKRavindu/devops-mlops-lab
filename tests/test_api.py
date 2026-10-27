import json

import numpy as np

SAMPLE = [13.2, 1.78, 2.14, 11.2, 100, 2.65, 2.76, 0.26, 1.28, 4.38, 1.05, 3.4, 1050]


def test_health_and_ready(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200


def test_predict(client):
    r = client.post("/predict", json={"features": [SAMPLE]})
    assert r.status_code == 200
    pred = r.json()["predictions"][0]
    assert pred["class"] == "class_0"
    assert 0 <= pred["confidence"] <= 1


def test_predict_matches_test_set(client, workdir):
    data = np.loadtxt(workdir / "data/test.csv", delimiter=",", skiprows=1)
    r = client.post("/predict", json={"features": data[:, :-1].tolist()})
    got = [int(p["class"].split("_")[1]) for p in r.json()["predictions"]]
    accuracy = np.mean(np.array(got) == data[:, -1])
    assert accuracy >= 0.85


def test_wrong_feature_count_rejected(client):
    assert client.post("/predict", json={"features": [[1.0, 2.0]]}).status_code == 422


def test_ragged_rows_rejected(client):
    assert client.post("/predict", json={"features": [SAMPLE, SAMPLE[:5]]}).status_code == 422


def test_empty_request_rejected(client):
    assert client.post("/predict", json={"features": []}).status_code == 422


def test_predictions_are_logged(client, workdir):
    client.post("/predict", json={"features": [SAMPLE]})
    lines = (workdir / "predictions.jsonl").read_text().strip().splitlines()
    assert json.loads(lines[-1])["features"] == SAMPLE


def test_metrics_exposed(client):
    client.post("/predict", json={"features": [SAMPLE]})
    body = client.get("/metrics").text
    assert "model_predictions_total" in body
    assert "api_request_latency_seconds" in body


def test_fault_injection(client, monkeypatch):
    monkeypatch.setenv("FAULT_ERROR_RATE", "1.0")
    assert client.post("/predict", json={"features": [SAMPLE]}).status_code == 500
