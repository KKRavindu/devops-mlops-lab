"""Send realistic traffic to the API. Use --drift to simulate production data drift.

  python scripts/simulate_traffic.py --n 300
  python scripts/simulate_traffic.py --n 300 --drift 0.5     # shift features by +50%
"""
import argparse
import json
import random
import time
import urllib.error
import urllib.request

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--n", type=int, default=200, help="number of requests")
    ap.add_argument("--rps", type=float, default=20, help="requests per second")
    ap.add_argument("--drift", type=float, default=0.0, help="relative shift applied to features")
    # Sample from the training distribution: resampling the tiny test set (36 rows)
    # hundreds of times is itself detectable as "drift" and causes false alarms.
    ap.add_argument("--data", default="data/train.csv")
    args = ap.parse_args()

    X = np.loadtxt(args.data, delimiter=",", skiprows=1)[:, :-1]
    # Drift affects a fixed subset of features, like a sensor recalibration would.
    drift_cols = [0, 4, 9, 12]
    ok = err = 0
    for i in range(args.n):
        row = X[random.randrange(len(X))] * np.random.normal(1.0, 0.03, X.shape[1])
        row[drift_cols] *= 1 + args.drift
        req = urllib.request.Request(
            f"{args.url}/predict",
            data=json.dumps({"features": [row.round(4).tolist()]}).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(req, timeout=5).read()
            ok += 1
        except (urllib.error.URLError, TimeoutError):
            err += 1
        if (i + 1) % 50 == 0:
            print(f"sent {i + 1}/{args.n}  ok={ok} err={err}")
        time.sleep(1 / args.rps)
    print(f"done: ok={ok} err={err}")


if __name__ == "__main__":
    main()
