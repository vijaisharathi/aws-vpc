# ==============================================================================
# Terraform Version and Provider Requirements
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

