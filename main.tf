# ==============================================================================
# Main Orchestration & Shared Data Sources
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

locals {
  name_prefix = "${var.project_name}-${var.environment}"

  # Configurable Availability Zones:
  # Uses var.availability_zones if explicitly provided; otherwise defaults dynamically to the first two available AZs in the configured AWS region.
  selected_azs = length(var.availability_zones) >= 2 ? var.availability_zones : slice(data.aws_availability_zones.available.names, 0, 2)
}

# ------------------------------------------------------------------------------
# Fetch Available Availability Zones in the Selected AWS Region
# ------------------------------------------------------------------------------
data "aws_availability_zones" "available" {
  state = "available"
}

# ------------------------------------------------------------------------------
# Fetch the Latest Official Canonical Ubuntu 22.04 LTS AMI (x86_64)
# ------------------------------------------------------------------------------
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical AWS Account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}
