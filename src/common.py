"""Shared helpers for the pipeline stages."""
from pathlib import Path

import numpy as np
import yaml

DATA_DIR = Path("data")
MODEL_DIR = Path("models")


def load_params(path: str = "params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_split(name: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Load data/<name>.csv -> (X, y, feature_names). Last column is the target."""
    path = DATA_DIR / f"{name}.csv"
    with open(path) as f:
        header = f.readline().strip().split(",")
    arr = np.loadtxt(path, delimiter=",", skiprows=1)
    return arr[:, :-1], arr[:, -1].astype(int), header[:-1]
