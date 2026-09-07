output "aws_region" {
  description = "AWS region configured for the infrastructure."
  value       = var.aws_region
}

output "project_name" {
  description = "Project name used in resource naming."
  value       = var.project_name
}

output "environment" {
  description = "Environment name used in resource naming."
  value       = var.environment
}

output "resource_prefix" {
  description = "Common prefix used for AWS resource names."
  value       = local.resource_prefix
}
