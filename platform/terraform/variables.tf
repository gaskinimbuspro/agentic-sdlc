variable "cluster_name" {
  description = "Name of the kind cluster."
  type        = string
  default     = "sdlc"
}

variable "node_image" {
  description = "Pinned kind node image."
  type        = string
  default     = "kindest/node:v1.33.4"
}

variable "git_repo_url" {
  description = "Repository that holds platform/apps; Argo CD reads it."
  type        = string
  default     = "https://github.com/gaskinimbuspro/agentic-sdlc.git"
}

variable "git_revision" {
  description = "Branch, tag or commit of git_repo_url that Argo CD follows."
  type        = string
  default     = "claude/nice-dijkstra-2lc88p"
}

variable "argocd_chart_version" {
  description = "Pinned argo-cd Helm chart version."
  type        = string
  default     = "10.18.2"
}

variable "argocd_apps_chart_version" {
  description = "Pinned argocd-apps Helm chart version (root application)."
  type        = string
  default     = "2.0.8"
}

variable "egress_proxy" {
  description = "Optional HTTPS proxy that cluster workloads must use to reach the internet. Empty on a normal server."
  type        = string
  default     = ""
}

variable "ca_bundle_path" {
  description = "Optional CA bundle to trust inside nodes and Argo CD, for a TLS-intercepting proxy. Empty on a normal server."
  type        = string
  default     = ""
}
