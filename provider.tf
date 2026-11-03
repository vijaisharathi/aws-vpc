# ==============================================================================
# AWS Provider Configuration
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

provider "aws" {
  region = var.aws_region

  # Default tags automatically inherited by all resources managed by this configuration
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.owner
      ManagedBy   = "Terraform"
    }
  }
}
