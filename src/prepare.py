"""Pipeline stage 1: fetch the raw dataset and split it into train/test CSVs."""
import numpy as np
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split

from src.common import DATA_DIR, load_params


def main() -> None:
    params = load_params()["prepare"]
    ds = load_wine()
    X_train, X_test, y_train, y_test = train_test_split(
        ds.data,
        ds.target,
        test_size=params["test_size"],
        random_state=params["seed"],
        stratify=ds.target,
    )

    DATA_DIR.mkdir(exist_ok=True)
    header = ",".join(list(ds.feature_names) + ["target"])
    for name, X, y in [("train", X_train, y_train), ("test", X_test, y_test)]:
        np.savetxt(
            DATA_DIR / f"{name}.csv",
            np.column_stack([X, y]),
            delimiter=",",
            header=header,
            comments="",
            fmt="%.6g",
        )
    print(f"[prepare] train={len(y_train)} test={len(y_test)} rows -> {DATA_DIR}/")


if __name__ == "__main__":
    main()
