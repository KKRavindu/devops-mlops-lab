# Lab 15: Capstone (Incident Drills & Chaos Engineering)

**Goal:** Operate the platform like an on-call engineer. For each drill, detect it from
dashboards and alerts *first*, then diagnose, mitigate, and write a short postmortem.

Get a friend to run the "inject" commands without telling you which one, or pick a
random drill: `shuf -i 1-8 -n 1`.

## The response loop
1. **Detect:** which alert or dashboard panel told you?
2. **Triage:** what is the user impact? How bad is it?
3. **Mitigate first:** roll back, scale up, or shift traffic. Fix the root cause later.
4. **Diagnose:** `kubectl describe / logs / events`, PromQL, `drift_report.json`
5. **Postmortem:** use the blameless template below.

## Drills

| # | Inject | Symptom to find |
|---|---|---|
| 1 | `kubectl -n wine-dev set env deploy/wine-api FAULT_ERROR_RATE=0.3` | HighErrorRate |
| 2 | `kubectl -n wine-dev set env deploy/wine-api FAULT_LATENCY_MS=800` | HighLatencyP95, HPA reaction |
| 3 | `kubectl -n wine-dev set image deploy/wine-api api=wine-api:typo` | Rollout stuck, ImagePullBackOff (old pods keep serving, so why is there no outage?) |
| 4 | `kubectl -n wine-dev patch deploy wine-api --type=json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"60Mi"}]'` | OOMKilled / CrashLoopBackOff |
| 5 | `kubectl -n wine-dev patch deploy wine-api --type=json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/x"}]'` | Pods Running but 0 endpoints |
| 6 | `make traffic-drift` (Compose stack) with `--n 2000 --drift 1.5` | LowPredictionConfidence / class skew, HTTP all 200 |
| 7 | Set `min_accuracy: 0.999` and push | CT pipeline red: is prod affected? |
| 8 | `minikube ssh -- sudo systemctl stop kubelet` (then start it again!) | Node NotReady, pod eviction after ~5 min |

## Postmortem template (`notes/postmortem-<n>.md`)
```markdown
## Summary
## Impact (who, how long, how many requests)
## Timeline (detect -> mitigate -> resolve)
## Root cause
## What went well / what went badly
## Action items (owner, due date) - prevent, detect faster, mitigate faster
```

## Final capstone project
Combine everything into one demo you can show in an interview:
1. Fork → push a param change → CI tests, scans and builds → CT retrains → Argo CD deploys.
2. Inject drift → the Grafana alert fires → the drift check fails → retraining gets
   triggered → a new model ships as a canary → it gets promoted.
3. Record a 5-minute screen-capture walkthrough and add it to the README.

## Where to go next
- **Cloud:** rebuild on EKS/GKE/AKS with Terraform (VPC, cluster, IAM, registry).
- **Serving at scale:** KServe / Seldon / BentoML / Ray Serve, GPU nodes, model batching.
- **Feature stores:** Feast. **Orchestration:** Airflow / Kubeflow / Prefect.
- **LLMOps:** prompt versioning, evaluation harnesses, guardrails, token cost monitoring.
- **Certs:** CKA/CKAD, Terraform Associate, a cloud associate cert (AWS/GCP/Azure).
