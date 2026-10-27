# Lab 05: Kubernetes Fundamentals

**Goal:** Run the service on Kubernetes and understand Pods, ReplicaSets, Deployments,
Services, probes and self-healing.

## Theory
- **Declarative model:** you describe the desired state (YAML), and controllers keep making
  the actual state match it.
- **Deployment → ReplicaSet → Pods.** A Service gives pods a stable virtual IP and DNS name.
- **Probes:** `startupProbe` (still booting), `livenessProbe` (restart me if this fails),
  and `readinessProbe` (remove me from the Service while this fails).
- **Requests/limits:** requests drive scheduling, and limits cap usage. Exceeding the
  memory limit gets the container OOMKilled.
- Read `k8s/base/deployment.yaml`. Note the security context, probes, and `maxUnavailable: 0`.

## Tasks
1. Start the cluster and load the image:
   ```bash
   make k8s-start
   make k8s-load
   ```
2. Deploy the dev environment:
   ```bash
   make k8s-deploy ENV=dev
   make k8s-status ENV=dev
   ```
3. Reach it:
   ```bash
   make k8s-forward ENV=dev     # terminal 1
   curl localhost:8080/ready    # terminal 2
   ```
4. Explore:
   ```bash
   kubectl -n wine-dev describe pod -l app=wine-api
   kubectl -n wine-dev logs -l app=wine-api --tail=20
   kubectl -n wine-dev exec deploy/wine-api -- python -c "import os; print(os.getuid())"
   kubectl -n wine-dev get events --sort-by=.lastTimestamp
   ```
5. Self-healing: delete a pod and watch a new one appear:
   `kubectl -n wine-dev delete pod -l app=wine-api` then `kubectl -n wine-dev get pods -w`.

## Checkpoint
- `/ready` responds through the port-forward, and you can draw Deployment → RS → Pod → Service.

## Break it (and debug with `describe`, `logs`, `events`)
- **ImagePullBackOff:** `kubectl -n wine-dev set image deploy/wine-api api=wine-api:doesnotexist`
  Then fix it with `kubectl -n wine-dev rollout undo deploy/wine-api`.
- **OOMKilled:** patch the memory limit to `50Mi`.
- **Not ready:** set the readiness path to `/nope`. Pods run but receive no traffic. Check
  `kubectl get endpoints`.
- **CrashLoopBackOff:** override the command to `["false"]`.

## Challenges
- Add an Ingress (`minikube addons enable ingress`) and reach the API at `wine.local`.
- Write a NetworkPolicy so only pods labelled `role=client` can call the API.

## Interview questions
- What happens, step by step, when you `kubectl apply` a Deployment?
- Liveness vs readiness vs startup probes. What goes wrong if liveness checks a dependency?
- Requests vs limits, and what QoS classes result from them?
