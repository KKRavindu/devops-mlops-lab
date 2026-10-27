# Lab 06: Kustomize Environments, Config and Scaling

**Goal:** One base, many environments, without copy-pasting YAML. Then autoscale under load.

## Theory
- **Kustomize** = base + overlays + patches. No templating language, just YAML transforms.
  It's built into `kubectl -k`.
- `configMapGenerator` adds a **hash suffix** to the ConfigMap name. Change a value and the
  Deployment spec changes, so pods roll automatically. (Plain ConfigMaps don't do this.)
- **HPA** scales on observed CPU vs *requests* and needs metrics-server.
- **PDB** limits voluntary disruptions (node drains), so at least N pods stay up.

## Tasks
1. Compare rendered output:
   ```bash
   kubectl kustomize k8s/overlays/dev  > /tmp/dev.yaml
   kubectl kustomize k8s/overlays/prod > /tmp/prod.yaml
   diff /tmp/dev.yaml /tmp/prod.yaml
   ```
2. Change config and watch an automatic rollout: in `k8s/overlays/dev/kustomization.yaml`
   set `LOG_LEVEL=warning`, then `make k8s-deploy ENV=dev` and
   `kubectl -n wine-dev get rs`. A new ReplicaSet appears. Why?
3. Autoscaling:
   ```bash
   kubectl -n wine-dev get hpa -w             # terminal 1
   make k8s-forward ENV=dev                   # terminal 2
   .venv/bin/python scripts/simulate_traffic.py --url http://localhost:8080 --n 5000 --rps 200   # terminal 3
   ```
   Or generate load from inside the cluster:
   `kubectl -n wine-dev run load --rm -it --image=busybox -- sh -c 'while true; do wget -qO- http://wine-api/health >/dev/null; done'`
4. Deploy prod too (`make k8s-deploy ENV=prod`) and compare replica counts.

## Checkpoint
- You can explain each difference in the dev/prod diff, and you saw the HPA add replicas.

## Break it
- Remove `resources.requests` from the deployment. What does the HPA report? (`<unknown>`)
- Drain the minikube node with the PDB in place: `kubectl drain minikube --ignore-daemonsets --delete-emptydir-data --dry-run=server`

## Challenges
- Add a `staging` overlay.
- Rewrite the base as a **Helm chart** and compare it to Kustomize. When would you choose each?
- Install **KEDA** and scale on a Prometheus query (requests/sec) instead of CPU.

## Interview questions
- Helm vs Kustomize?
- Why does the HPA need resource requests?
- How do you manage secrets in Kubernetes properly? (Sealed Secrets, External Secrets, SOPS, Vault)
