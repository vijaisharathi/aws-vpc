# ==============================================================================
# Amazon RDS MySQL Database Configuration (Secure Private Subnet Deployment)
# Project: AWS VPC – Public and Private Subnet Demonstration
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. RDS DB Subnet Group
# AWS strictly mandates that any DB Subnet Group must span at least two
# distinct Availability Zones within the region, even when running Single-AZ.
# Subnets included: private-subnet-1 (AZ-A) and private-subnet-2 (AZ-B).
# ------------------------------------------------------------------------------
resource "aws_db_subnet_group" "main" {
  name        = "${local.name_prefix}-db-subnet-group"
  description = "Cross-AZ database subnet group spanning private-subnet-1 and private-subnet-2"
  subnet_ids  = [aws_subnet.private.id, aws_subnet.private_db.id]

  tags = {
    Name        = "${local.name_prefix}-db-subnet-group"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Database-Subnet-Group"
  }
}

# ------------------------------------------------------------------------------
# 2. Amazon RDS MySQL Instance (Conditional)
# ------------------------------------------------------------------------------
resource "aws_db_instance" "mysql" {
  count = var.enable_rds_instance ? 1 : 0

  identifier        = "${local.name_prefix}-mysql"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp2"
  port              = 3306

  # Storage Cost Control: Prevent automatic storage auto-scaling charges
  max_allocated_storage = var.db_allocated_storage

  # Database Engine Settings
  db_name  = var.db_name
  username = var.db_username

  # AWS-Managed Database Credentials through AWS Secrets Manager
  # When manage_master_user_password is true, AWS RDS creates and manages the secret
  # automatically, avoiding plaintext password storage in source files or state.
  manage_master_user_password = var.manage_master_user_password
  password                    = var.manage_master_user_password ? null : var.db_password

  # Network & Security Tiering
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  # Strict Isolation: Never allow direct public internet exposure
  publicly_accessible = false

  # Data Protection: Enable AES-256 encryption at rest
  storage_encrypted = true

  # Operational & Lifecycle Management
  backup_retention_period = var.db_backup_retention_period
  deletion_protection     = var.enable_deletion_protection
  skip_final_snapshot     = var.db_skip_final_snapshot

  # Cost Optimization for Academic Labs: Single-AZ deployment
  multi_az = false

  tags = {
    Name        = "${local.name_prefix}-mysql-db"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Database-Tier"
  }
}
