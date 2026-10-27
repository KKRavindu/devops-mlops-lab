"""Detect data drift between training data and live predictions.

Runs a two-sample Kolmogorov-Smirnov test per feature. Exits 1 when drift is
detected so CI / cron can trigger retraining.

  python scripts/drift_check.py --log logs/predictions.jsonl
"""
import argparse
import json
import sys

import numpy as np
from scipy.stats import ks_2samp


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="logs/predictions.jsonl")
    ap.add_argument("--reference", default="data/train.csv")
    ap.add_argument("--p-value", type=float, default=0.01)
    ap.add_argument("--max-drifted-share", type=float, default=0.2,
                    help="fail if more than this share of features drifted")
    ap.add_argument("--min-samples", type=int, default=50)
    ap.add_argument("--report", default="drift_report.json")
    args = ap.parse_args()

    with open(args.reference) as f:
        names = f.readline().strip().split(",")[:-1]
    ref = np.loadtxt(args.reference, delimiter=",", skiprows=1)[:, :-1]

    with open(args.log) as f:
        live = np.array([json.loads(line)["features"] for line in f if line.strip()])
    if len(live) < args.min_samples:
        print(f"only {len(live)} samples (< {args.min_samples}); not enough to judge drift")
        return 0

    features = {}
    for i, name in enumerate(names):
        stat, p = ks_2samp(ref[:, i], live[:, i])
        features[name] = {
            "ks_stat": round(stat, 4),
            "p_value": round(p, 6),
            "drift": bool(p < args.p_value),
        }

    drifted = [n for n, r in features.items() if r["drift"]]
    share = len(drifted) / len(names)
    report = {
        "samples": len(live),
        "drifted_features": drifted,
        "drifted_share": round(share, 3),
        "dataset_drift": share > args.max_drifted_share,
        "features": features,
    }
    with open(args.report, "w") as f:
        json.dump(report, f, indent=2)

    for name, r in features.items():
        flag = "DRIFT" if r["drift"] else "ok"
        print(f"  {name:32s} ks={r['ks_stat']:.3f} p={r['p_value']:.4f}  {flag}")
    print(f"\n{len(drifted)}/{len(names)} features drifted ({share:.0%}) -> report: {args.report}")
    if report["dataset_drift"]:
        print("DATASET DRIFT DETECTED - retraining recommended")
        return 1
    print("no significant dataset drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
