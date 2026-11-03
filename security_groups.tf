# ==============================================================================
# Security Groups Configuration (Least Privilege Network Security)
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Web Tier Security Group (Apache Web Server on EC2)
# Implements strict least-privilege inbound and outbound rules.
# ------------------------------------------------------------------------------
resource "aws_security_group" "web" {
  name        = "${local.name_prefix}-web-sg"
  description = "Controls inbound web and restricted management traffic for EC2 Web Server"
  vpc_id      = aws_vpc.main.id

  # Inbound HTTP (Port 80) from public internet
  ingress {
    description = "Allow inbound HTTP web traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_http_cidr]
  }

  # Inbound HTTPS (Port 443) from public internet
  ingress {
    description = "Allow inbound HTTPS web traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_http_cidr]
  }

  # Optional Inbound SSH (Port 22) - strictly restricted, never 0.0.0.0/0
  dynamic "ingress" {
    for_each = var.enable_ssh_ingress ? [1] : []
    content {
      description = "Allow restricted administrative SSH access from authorized CIDR only"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [var.allowed_ssh_cidr]
    }
  }

  # ----------------------------------------------------------------------------
  # Least-Privilege Outbound Rules (Replaces arbitrary 0.0.0.0/0 all-traffic egress)
  # ----------------------------------------------------------------------------

  # Outbound HTTPS (Port 443): AWS Systems Manager (SSM), AWS APIs, package downloads
  egress {
    description = "Allow outbound HTTPS for AWS SSM Agent, AWS APIs, and secure packages"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound HTTP (Port 80): Ubuntu package mirror updates (archive.ubuntu.com)
  egress {
    description = "Allow outbound HTTP for Debian/Ubuntu package mirrors"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound DNS (Port 53 UDP & TCP): Domain name resolution
  egress {
    description = "Allow outbound DNS query over UDP"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound DNS query over TCP"
    from_port   = 53
    to_port     = 53
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound NTP (Port 123 UDP): Network Time Protocol clock synchronization
  egress {
    description = "Allow outbound NTP for server clock synchronization"
    from_port   = 123
    to_port     = 123
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound MySQL (Port 3306): Restricted strictly to internal VPC network
  egress {
    description = "Allow outbound MySQL connections strictly inside the internal VPC network"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name        = "${local.name_prefix}-web-sg"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Web-Security"
  }
}

# ------------------------------------------------------------------------------
# 2. Database Tier Security Group (Amazon RDS MySQL)
# Restricts MySQL (Port 3306) access strictly to the Web Server Security Group.
# Never permits 0.0.0.0/0 ingress or arbitrary internet outbound.
# ------------------------------------------------------------------------------
resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db-sg"
  description = "Controls database traffic to RDS MySQL strictly from the Web Tier SG"
  vpc_id      = aws_vpc.main.id

  # Inbound MySQL (Port 3306) strictly referenced from the Web Security Group ID
  ingress {
    description     = "Allow MySQL access strictly from EC2 Web Security Group ID"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  # Outbound Rule: Restricted strictly to the internal VPC CIDR (No direct internet egress)
  egress {
    description = "Allow outbound communication strictly within internal VPC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name        = "${local.name_prefix}-db-sg"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Database-Security"
  }
}
