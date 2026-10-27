import json

import numpy as np


def test_data_split_written(workdir):
    train = np.loadtxt(workdir / "data/train.csv", delimiter=",", skiprows=1)
    test = np.loadtxt(workdir / "data/test.csv", delimiter=",", skiprows=1)
    assert train.shape[1] == test.shape[1] == 14  # 13 features + target
    assert len(train) > len(test)


def test_model_passes_quality_gate(workdir):
    meta = json.loads((workdir / "models/metadata.json").read_text())
    assert meta["metrics"]["accuracy"] >= meta["params"]["min_accuracy"]
    assert len(meta["feature_names"]) == 13
