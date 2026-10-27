variable "kubeconfig_path" {
  type    = string
  default = "~/.kube/config"
}

variable "kube_context" {
  type    = string
  default = "minikube"
}

variable "environments" {
  description = "One namespace per environment, each with its own resource budget."
  type = map(object({
    cpu_limit    = string
    memory_limit = string
    max_pods     = number
  }))
  default = {
    dev  = { cpu_limit = "4", memory_limit = "4Gi", max_pods = 10 }
    prod = { cpu_limit = "6", memory_limit = "6Gi", max_pods = 30 }
  }
}
