import os
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def workdir(tmp_path_factory):
    """Run the full pipeline (prepare -> train) in an isolated temp dir."""
    from src import prepare, train

    wd = tmp_path_factory.mktemp("pipeline")
    shutil.copy(ROOT / "params.yaml", wd / "params.yaml")
    old = os.getcwd()
    os.chdir(wd)
    prepare.main()
    train.main()
    yield wd
    os.chdir(old)


@pytest.fixture()
def client(workdir, monkeypatch):
    from fastapi.testclient import TestClient

    from src.serve import app

    monkeypatch.setenv("MODEL_DIR", str(workdir / "models"))
    monkeypatch.setenv("PREDICTION_LOG", str(workdir / "predictions.jsonl"))
    with TestClient(app) as c:
        yield c
