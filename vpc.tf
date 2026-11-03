# ==============================================================================
# Virtual Private Cloud (VPC)
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${local.name_prefix}-vpc"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}
