# ==============================================================================
# Gateways Configuration (Internet Gateway and NAT Gateway)
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Internet Gateway (IGW)
# Provides bidirectional communication between resources in the public subnet
# and the public internet. Attached directly to the custom VPC.
# ------------------------------------------------------------------------------
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${local.name_prefix}-igw"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Gateway"
  }
}

# ------------------------------------------------------------------------------
# 2. Elastic IP for NAT Gateway (Conditional)
# Allocated only when var.enable_nat_gateway is true to prevent ongoing idle
# IPv4 address billing (~$3.60/month).
# ------------------------------------------------------------------------------
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = {
    Name        = "${local.name_prefix}-nat-eip"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Network-EIP"
  }

  depends_on = [aws_internet_gateway.main]
}

# ------------------------------------------------------------------------------
# 3. NAT Gateway (Conditional)
# Deployed specifically in the PUBLIC subnet (public-subnet-1) to allow instances
# residing in private subnets to originate outbound internet traffic without
# exposing their private interfaces to incoming internet connections.
# ------------------------------------------------------------------------------
resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public.id

  tags = {
    Name        = "${local.name_prefix}-nat-gw"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Network-NAT"
  }

  # Strict dependency: The Internet Gateway must be successfully attached to the VPC
  # before the NAT Gateway can be provisioned.
  depends_on = [aws_internet_gateway.main]
}
