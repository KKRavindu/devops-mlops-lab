"""Pipeline stage 2: train, evaluate, enforce a quality gate, save the model.

If MLFLOW_TRACKING_URI is set, params/metrics/model are also logged to MLflow
and the model is registered as "wine-classifier".
"""
import json
import os
import sys
from datetime import datetime, timezone

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.common import MODEL_DIR, load_params, load_split

CLASS_NAMES = ["class_0", "class_1", "class_2"]


def build_model(p: dict):
    if p["model"] == "random_forest":
        return RandomForestClassifier(
            n_estimators=p["n_estimators"], max_depth=p["max_depth"], random_state=p["seed"]
        )
    if p["model"] == "logistic_regression":
        return Pipeline(
            [("scale", StandardScaler()), ("clf", LogisticRegression(C=p["C"], max_iter=1000))]
        )
    raise ValueError(f"unknown model type: {p['model']}")


def log_to_mlflow(p: dict, metrics: dict, model) -> None:
    import mlflow
    import mlflow.sklearn

    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT", "wine-classifier"))
    with mlflow.start_run():
        mlflow.log_params(p)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model", registered_model_name="wine-classifier")
    print(f"[train] logged run to MLflow at {os.environ['MLFLOW_TRACKING_URI']}")


def main() -> None:
    p = load_params()["train"]
    # Env overrides let CI / Docker build variants without editing params.yaml.
    p["model"] = os.getenv("TRAIN_MODEL", p["model"])

    X_train, y_train, feature_names = load_split("train")
    X_test, y_test, _ = load_split("test")

    model = build_model(p).fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "f1_macro": round(f1_score(y_test, preds, average="macro"), 4),
    }
    print(f"[train] model={p['model']} metrics={metrics}")

    # Quality gate: never ship a model that is worse than the agreed baseline.
    if metrics["accuracy"] < p["min_accuracy"]:
        print(f"[train] FAILED quality gate: accuracy < {p['min_accuracy']}", file=sys.stderr)
        sys.exit(1)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_DIR / "model.joblib")
    metadata = {
        "version": os.getenv("MODEL_VERSION", datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")),
        "model_type": p["model"],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_names": feature_names,
        "class_names": CLASS_NAMES,
        "metrics": metrics,
        "params": p,
    }
    (MODEL_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2))
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[train] saved {MODEL_DIR}/model.joblib (version {metadata['version']})")

    if os.getenv("MLFLOW_TRACKING_URI"):
        log_to_mlflow(p, metrics, model)


if __name__ == "__main__":
    main()
