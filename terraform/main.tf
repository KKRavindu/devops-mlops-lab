# Platform layer: namespaces, quotas and default limits for each environment.
# The app layer (k8s/overlays/*) is deployed on top by kubectl / Argo CD.

resource "kubernetes_namespace" "env" {
  for_each = var.environments

  metadata {
    name = "wine-${each.key}"
    labels = {
      env          = each.key
      "managed-by" = "terraform"
    }
  }
}

resource "kubernetes_resource_quota" "env" {
  for_each = var.environments

  metadata {
    name      = "compute-quota"
    namespace = kubernetes_namespace.env[each.key].metadata[0].name
  }
  spec {
    hard = {
      "limits.cpu"    = each.value.cpu_limit
      "limits.memory" = each.value.memory_limit
      pods            = each.value.max_pods
    }
  }
}

# Containers without explicit resources get these defaults, so the quota never blocks them.
resource "kubernetes_limit_range" "env" {
  for_each = var.environments

  metadata {
    name      = "default-limits"
    namespace = kubernetes_namespace.env[each.key].metadata[0].name
  }
  spec {
    limit {
      type            = "Container"
      default         = { cpu = "500m", memory = "384Mi" }
      default_request = { cpu = "100m", memory = "128Mi" }
    }
  }
}
