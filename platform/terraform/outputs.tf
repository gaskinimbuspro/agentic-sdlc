output "forgejo_admin_password" {
  description = "Generated Forgejo admin password (user forge-admin)."
  value       = random_password.forgejo_admin.result
  sensitive   = true
}
