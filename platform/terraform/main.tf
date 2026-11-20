# Platform bootstrap on an existing cluster: Argo CD and one root application.
# Argo CD then installs everything under platform/apps from Git.

locals {
  proxied   = var.egress_proxy != ""
  custom_ca = var.ca_bundle_path != ""
  no_proxy  = "localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,.svc,.cluster.local,kubernetes.default.svc"
  ca_path   = "/etc/ssl/certs/ca-certificates.crt"
  proxy_env = local.proxied ? [
    { name = "HTTPS_PROXY", value = var.egress_proxy },
    { name = "NO_PROXY", value = local.no_proxy },
  ] : []
}

provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kubeconfig_context
}

provider "helm" {
  kubernetes = {
    config_path    = var.kubeconfig_path
    config_context = var.kubeconfig_context
  }
}

# Forgejo admin credentials are generated here and never written to Git.
resource "random_password" "forgejo_admin" {
  length  = 24
  special = false
}

resource "kubernetes_namespace_v1" "forgejo" {
  metadata {
    name = "forgejo"
  }
}

resource "kubernetes_secret_v1" "forgejo_admin" {
  metadata {
    name      = "forgejo-admin"
    namespace = kubernetes_namespace_v1.forgejo.metadata[0].name
  }
  data = {
    username = "forge-admin"
    password = random_password.forgejo_admin.result
  }
}

resource "kubernetes_namespace_v1" "argocd" {
  metadata {
    name = "argocd"
  }
}

resource "kubernetes_config_map_v1" "trusted_ca" {
  count = local.custom_ca ? 1 : 0
  metadata {
    name      = "trusted-ca"
    namespace = kubernetes_namespace_v1.argocd.metadata[0].name
  }
  data = {
    "ca-certificates.crt" = file(var.ca_bundle_path)
  }
}

resource "helm_release" "argocd" {
  name       = "argocd"
  namespace  = kubernetes_namespace_v1.argocd.metadata[0].name
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = var.argocd_chart_version
  wait       = true
  timeout    = 900

  values = [yamlencode({
    configs = {
      params = { "server.insecure" = true }
      # The Forgejo chart is published as an OCI artifact.
      repositories = {
        forgejo-helm = {
          type      = "helm"
          name      = "forgejo-helm"
          url       = "code.forgejo.org/forgejo-helm"
          enableOCI = "true"
        }
      }
    }
    dex           = { enabled = false }
    notifications = { enabled = false }
    repoServer = {
      env = local.proxy_env
      volumes = local.custom_ca ? [{
        name      = "trusted-ca"
        configMap = { name = "trusted-ca" }
      }] : []
      volumeMounts = local.custom_ca ? [{
        name      = "trusted-ca"
        mountPath = local.ca_path
        subPath   = "ca-certificates.crt"
        readOnly  = true
      }] : []
    }
  })]

  depends_on = [kubernetes_config_map_v1.trusted_ca]
}

resource "helm_release" "root" {
  name       = "root"
  namespace  = kubernetes_namespace_v1.argocd.metadata[0].name
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argocd-apps"
  version    = var.argocd_apps_chart_version

  values = [yamlencode({
    applications = {
      root = {
        namespace = "argocd"
        project   = "default"
        source = {
          repoURL        = var.git_repo_url
          targetRevision = var.git_revision
          path           = "platform/apps"
        }
        destination = {
          server    = "https://kubernetes.default.svc"
          namespace = "argocd"
        }
        syncPolicy = {
          automated = { prune = true, selfHeal = true }
        }
      }
    }
  })]

  depends_on = [helm_release.argocd, kubernetes_secret_v1.forgejo_admin]
}
