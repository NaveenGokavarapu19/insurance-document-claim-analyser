locals {
  default_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
    ManagedBy   = "terraform"
  }

  resource_prefix = "${var.project_name}-${var.environment}"
}
