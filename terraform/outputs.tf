output "namespaces" {
  value = [for ns in kubernetes_namespace.env : ns.metadata[0].name]
}
