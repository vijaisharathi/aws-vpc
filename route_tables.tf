# ==============================================================================
# Route Tables, Routes, and Subnet Associations
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Public Route Table
# Handles routing for the public web subnet (public-subnet-1).
# Note: AWS automatically installs the implicit local route (10.0.0.0/16 -> local).
# ------------------------------------------------------------------------------
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${local.name_prefix}-public-rt"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Public-Routing"
  }
}

# Default outbound Internet route directing non-VPC traffic (0.0.0.0/0) to the Internet Gateway
resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

# Associate Public Route Table exclusively with the Public Subnet (public-subnet-1)
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ------------------------------------------------------------------------------
# 2. Private Route Table
# Handles routing for private-subnet-1 (App) and private-subnet-2 (DB).
# Note: AWS automatically installs the implicit local route (10.0.0.0/16 -> local).
# ------------------------------------------------------------------------------
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${local.name_prefix}-private-rt"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Private-Routing"
  }
}

# Conditional outbound route directing non-VPC traffic (0.0.0.0/0) to the NAT Gateway
# Only created when var.enable_nat_gateway is true.
resource "aws_route" "private_nat" {
  count                  = var.enable_nat_gateway ? 1 : 0
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main[0].id
}

# Associate Private Route Table with Private Subnet 1 (private-subnet-1)
resource "aws_route_table_association" "private_app" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# Associate Private Route Table with Private Subnet 2 (private-subnet-2)
resource "aws_route_table_association" "private_db" {
  subnet_id      = aws_subnet.private_db.id
  route_table_id = aws_route_table.private.id
}
