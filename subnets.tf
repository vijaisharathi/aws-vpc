# ==============================================================================
# Subnets Configuration
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Public Subnet (10.0.1.0/24) - First Selected Availability Zone
# Hosts: Apache Web Server (EC2) and NAT Gateway
# Auto-assign public IPv4: Enabled
# ------------------------------------------------------------------------------
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = local.selected_azs[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = var.public_subnet_name
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Public"
    AZ          = local.selected_azs[0]
  }
}

# ------------------------------------------------------------------------------
# 2. Private Subnet 1 (10.0.2.0/24) - First Selected Availability Zone
# Hosts: Private Application Workloads and RDS DB Subnet Group Member 1
# Auto-assign public IPv4: Disabled
# ------------------------------------------------------------------------------
resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidr
  availability_zone       = local.selected_azs[0]
  map_public_ip_on_launch = false

  tags = {
    Name        = var.private_subnet_1_name
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Private-App"
    AZ          = local.selected_azs[0]
  }
}

# ------------------------------------------------------------------------------
# 3. Private Subnet 2 (10.0.3.0/24) - Second Selected Availability Zone
# Hosts: RDS DB Subnet Group Member 2 (Fulfills AWS RDS Multi-AZ coverage rule)
# Auto-assign public IPv4: Disabled
# ------------------------------------------------------------------------------
resource "aws_subnet" "private_db" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_db_subnet_cidr
  availability_zone       = local.selected_azs[1]
  map_public_ip_on_launch = false

  tags = {
    Name        = var.private_subnet_2_name
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Private-DB"
    AZ          = local.selected_azs[1]
  }
}
