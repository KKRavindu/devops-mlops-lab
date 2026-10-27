# Lab 14: GitOps with Argo CD

**Goal:** The cluster deploys itself from Git. Nobody runs `kubectl apply` against prod.

## Theory
- **GitOps principles:** declarative, versioned in Git, *pulled* automatically by an agent
  in the cluster, and continuously reconciled.
- **Push vs pull:** CI doesn't need cluster credentials, because Argo CD pulls. Better security.
- **Flow in this repo:** merge → CI builds `sha-abc123` → the `gitops-bump` job rewrites
  `k8s/overlays/prod/kustomization.yaml` → Argo CD sees the commit → syncs → the new pods
  roll out. Rollback = `git revert`.
- `selfHeal: true` reverts manual changes, and `prune: true` deletes what was removed from Git.

## Tasks
1. Install Argo CD:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.12.4/manifests/install.yaml
   kubectl -n argocd rollout status deploy/argocd-server
   kubectl -n argocd port-forward svc/argocd-server 8443:443
   # password for user "admin":
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
   ```
   Open https://localhost:8443.
2. Edit `k8s/argocd/application.yaml` → set `repoURL` to your fork. Commit, push, then:
   `kubectl apply -f k8s/argocd/application.yaml`
3. **Image access:** prod uses `ghcr.io/<you>/wine-api`. Make the package public (GitHub →
   Packages → settings), or create an imagePullSecret.
4. Make a code change, merge it, and watch CI bump the tag and Argo CD sync it with no
   `kubectl` from you.
5. **Self-heal:** `kubectl -n wine-prod scale deploy/wine-api --replicas=1` and watch Argo
   CD revert it.
6. **Rollback via Git:** `git revert <bump-commit> && git push`.

## Checkpoint
- A merge to `main` reaches the cluster with no manual steps, and manual drift gets reverted.

## Challenges
- Use the **App of Apps** pattern to manage dev + prod + monitoring from one root app.
- Add **Argo CD Image Updater** instead of the CI bump job. Compare the two approaches.
- Manage a Secret the GitOps way with **Sealed Secrets**.
- Try **Flux** and compare it with Argo CD.

## Interview questions
- What problem does GitOps solve that CI-driven `kubectl apply` doesn't?
- How do you handle secrets in GitOps?
- How do you promote between environments in GitOps? (folders, branches, or tags?)
