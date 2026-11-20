output "kubeconfig_path" {
  description = "Kubeconfig for the created cluster."
  value       = kind_cluster.this.kubeconfig_path
}

output "forgejo_admin_password" {
  description = "Generated Forgejo admin password (user forge-admin)."
  value       = random_password.forgejo_admin.result
  sensitive   = true
}
