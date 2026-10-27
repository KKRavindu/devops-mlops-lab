# Lab 07: Infrastructure as Code with Terraform

**Goal:** Manage the *platform layer* (namespaces, quotas, default limits) declaratively,
with plan/apply, state and drift detection.

## Theory
- **Terraform workflow:** `init` → `plan` (diff of desired vs actual) → `apply`.
- **State** maps your code to real resources. Real teams keep it in a remote backend
  (S3+DynamoDB, GCS, Terraform Cloud) with locking.
- **Layering:** Terraform owns *platform* (clusters, namespaces, IAM, buckets), while
  Kustomize/Argo CD own *apps*. Two tools must never manage the same object.
- `for_each` over a map gives one resource per environment, with no duplication.

## Tasks
1. Install Terraform: https://developer.hashicorp.com/terraform/install
2. Hand the namespaces over to Terraform. `make k8s-deploy` created them earlier, so
   delete them first (or `terraform import` them):
   ```bash
   make k8s-delete ENV=dev; make k8s-delete ENV=prod
   kubectl delete ns wine-dev wine-prod --ignore-not-found
   cd terraform
   terraform init
   terraform fmt -check && terraform validate
   terraform plan
   terraform apply
   kubectl get ns -l managed-by=terraform
   kubectl -n wine-prod describe quota,limitrange
   cd .. && make k8s-deploy ENV=dev
   ```
3. Add a `staging` entry to `var.environments` and run `plan`. Only the new resources appear.
4. **Drift detection:** change something by hand, then let Terraform notice:
   ```bash
   kubectl label ns wine-dev managed-by=me --overwrite
   cd terraform && terraform plan     # shows it will revert the label
   ```

## Checkpoint
- `terraform plan` reports "No changes" after apply, and you understand what's in
  `terraform.tfstate`.

## Break it
- Lower the dev `max_pods` to `1` and apply, then scale the deployment to 3. Read the
  ReplicaSet events (`kubectl -n wine-dev describe rs`).
- Delete `terraform.tfstate` and run `plan`. Why is a remote, locked backend essential?

## Challenges
- Move state to a remote backend (e.g. MinIO via the S3 backend).
- Turn this into a reusable **module** and call it once per environment.
- Use the `helm` provider to install kube-prometheus-stack from Terraform.
- Add `tflint` and `checkov` to CI.

## Interview questions
- What is Terraform state and why is it sensitive?
- `count` vs `for_each`?
- How do you handle drift? How do you import existing resources?
