# Lab 13: Release Strategies (Rolling, Canary, Rollback)

**Goal:** Ship a new *model* to production with limited blast radius, and roll back in seconds.

## Theory
- **Rolling update** (our default): replace pods gradually. `maxUnavailable: 0` means
  capacity never drops.
- **Blue/green:** run two full environments and switch the Service selector at once.
  Instant rollback, at double the cost.
- **Canary:** send a small % of traffic to the new version, compare metrics, then promote
  or abort. Our Service selects only `app: wine-api`, so a second Deployment labelled
  `track: canary` receives traffic in proportion to its replicas.
- **Shadow (dark launch):** the new model receives a copy of traffic, but its answers are
  not returned. This is very common for ML because you can compare predictions risk-free.
- **Rollback:** Kubernetes keeps old ReplicaSets (`revisionHistoryLimit`), so `rollout undo`
  is instant.

## Tasks
1. Build v2 (a different model type) and load it:
   ```bash
   docker build --build-arg TRAIN_MODEL=logistic_regression --build-arg MODEL_VERSION=v2 -t wine-api:v2 .
   minikube image load wine-api:v2
   ```
2. **Canary (25%):**
   ```bash
   kubectl -n wine-dev scale deploy/wine-api --replicas=3
   kubectl -n wine-dev patch hpa wine-api -p '{"spec":{"minReplicas":3}}'
   kubectl -n wine-dev apply -f k8s/canary/deployment-canary.yaml
   kubectl -n wine-dev get pods -L track
   make k8s-forward ENV=dev
   for i in $(seq 40); do curl -s -X POST localhost:8080/predict -H 'Content-Type: application/json' \
     -d '{"features":[[13.2,1.78,2.14,11.2,100,2.65,2.76,0.26,1.28,4.38,1.05,3.4,1050]]}' | grep -o '"model_version":"[^"]*"'; done | sort | uniq -c
   ```
   (`port-forward` pins to one pod. For a real split, curl the Service from inside the
   cluster: `kubectl -n wine-dev run c --rm -it --image=curlimages/curl -- sh`.)
3. **Promote:** `kubectl -n wine-dev set image deploy/wine-api api=wine-api:v2`, then delete
   the canary Deployment.
4. **Rollback:**
   ```bash
   kubectl -n wine-dev rollout history deploy/wine-api
   kubectl -n wine-dev rollout undo deploy/wine-api
   kubectl -n wine-dev rollout status deploy/wine-api
   curl localhost:8080/model | grep version
   ```
5. Prove zero downtime: run `scripts/simulate_traffic.py --url http://localhost:8080`
   during a rollout and confirm `err=0`. (Restart the port-forward if its pod is replaced,
   or test from inside the cluster.)

## Checkpoint
- You ran a canary, promoted it, rolled back, and can explain when to use each strategy.

## Break it
- **The shutdown race:** delete the `lifecycle.preStop` block from
  `k8s/base/deployment.yaml`, redeploy, and repeat task 5 from *inside* the cluster:
  ```bash
  kubectl -n wine-dev run load --rm -i --restart=Never --image=curlimages/curl:8.10.1 -- sh -c \
    'ok=0; fail=0; for i in $(seq 1500); do c=$(curl -s -o /dev/null -w "%{http_code}" -m 3 http://wine-api/ready); \
     [ "$c" = 200 ] && ok=$((ok+1)) || fail=$((fail+1)); done; echo "ok=$ok fail=$fail"'
  ```
  and run `kubectl -n wine-dev rollout restart deploy/wine-api` meanwhile. Requests now
  fail (in testing, ~2% of requests failed across one promote + rollback). Why? SIGTERM
  arrives at the same time as endpoint removal starts, and kube-proxy on each node still
  routes to the dying pod for a moment. The `sleep 10` preStop keeps the pod serving until
  routing has caught up. Restore it and confirm `fail=0`.
- **Quota vs surge:** if you did lab 07, the namespace has a ResourceQuota. Set the dev
  `cpu_limit` back to `"2"` in `terraform/variables.tf`, `terraform apply`, and repeat the
  canary + promote. The rollout hangs because the surge pod (`maxSurge: 1`) doesn't fit.
  Find the reason in `kubectl -n wine-dev describe rs` and explain why capacity planning
  must include rollout headroom.

## Challenges
- Install **Argo Rollouts** and do an automated canary that aborts when Prometheus shows
  error rate > 5% (an AnalysisTemplate).
- Implement **shadow deployment**: the API sends each request to v2 asynchronously and logs
  disagreements.
- A/B test two models and decide the winner with a statistical test.

## Interview questions
- Canary vs blue/green vs shadow: costs, risks, and when to use each for ML?
- What metrics decide whether a model canary is healthy?
- How do you roll back a model when the database schema also changed?
