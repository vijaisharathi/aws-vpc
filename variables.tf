# ==============================================================================
# Input Variables
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# ------------------------------------------------------------------------------
# General Project Metadata & Governance
# ------------------------------------------------------------------------------
variable "aws_region" {
  type        = string
  description = "The AWS region where all infrastructure resources will be deployed."
  default     = "ap-southeast-2"
}

variable "project_name" {
  type        = string
  description = "Prefix name used for naming resources across this project."
  default     = "vpc-academic-project"
}

variable "environment" {
  type        = string
  description = "Deployment environment name (e.g., dev, test, prod, academic)."
  default     = "academic"
}

variable "owner" {
  type        = string
  description = "Project ownership tag for resource governance and accounting."
  default     = "Academic Lab"
}

# ------------------------------------------------------------------------------
# VPC and Subnet Network Specifications
# ------------------------------------------------------------------------------
variable "vpc_cidr" {
  type        = string
  description = "The CIDR block allocated to the custom Virtual Private Cloud (VPC)."
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0)) && tonumber(split("/", var.vpc_cidr)[1]) >= 16 && tonumber(split("/", var.vpc_cidr)[1]) <= 24
    error_message = "vpc_cidr must be a valid IPv4 CIDR block with a prefix length between /16 and /24."
  }
}

variable "public_subnet_cidr" {
  type        = string
  description = "The CIDR block allocated to the public web subnet (e.g., Apache EC2)."
  default     = "10.0.1.0/24"

  validation {
    condition     = can(cidrhost(var.public_subnet_cidr, 0)) && tonumber(split("/", var.public_subnet_cidr)[1]) >= 16 && tonumber(split("/", var.public_subnet_cidr)[1]) <= 28
    error_message = "public_subnet_cidr must be a valid IPv4 CIDR block with a prefix length between /16 and /28."
  }
}

variable "private_subnet_cidr" {
  type        = string
  description = "The CIDR block allocated to private subnet 1 (App Tier / DB Subnet AZ-A)."
  default     = "10.0.2.0/24"

  validation {
    condition     = can(cidrhost(var.private_subnet_cidr, 0)) && tonumber(split("/", var.private_subnet_cidr)[1]) >= 16 && tonumber(split("/", var.private_subnet_cidr)[1]) <= 28 && var.private_subnet_cidr != var.public_subnet_cidr
    error_message = "private_subnet_cidr must be a valid IPv4 CIDR block and cannot overlap with public_subnet_cidr."
  }
}

variable "private_db_subnet_cidr" {
  type        = string
  description = "The CIDR block allocated to private subnet 2 (DB Subnet AZ-B for RDS Multi-AZ compliance)."
  default     = "10.0.3.0/24"

  validation {
    condition     = can(cidrhost(var.private_db_subnet_cidr, 0)) && tonumber(split("/", var.private_db_subnet_cidr)[1]) >= 16 && tonumber(split("/", var.private_db_subnet_cidr)[1]) <= 28 && var.private_db_subnet_cidr != var.public_subnet_cidr && var.private_db_subnet_cidr != var.private_subnet_cidr
    error_message = "private_db_subnet_cidr must be a valid IPv4 CIDR block and cannot overlap with public_subnet_cidr or private_subnet_cidr."
  }
}

# ------------------------------------------------------------------------------
# Subnet Naming Tags
# ------------------------------------------------------------------------------
variable "public_subnet_name" {
  type        = string
  description = "The Name tag assigned to the public subnet."
  default     = "public-subnet-1"
}

variable "private_subnet_1_name" {
  type        = string
  description = "The Name tag assigned to private subnet 1."
  default     = "private-subnet-1"
}

variable "private_subnet_2_name" {
  type        = string
  description = "The Name tag assigned to private subnet 2."
  default     = "private-subnet-2"
}

# ------------------------------------------------------------------------------
# Configurable Availability Zones
# ------------------------------------------------------------------------------
variable "availability_zones" {
  type        = list(string)
  description = "Configurable list of Availability Zones to deploy into (e.g. [\"us-east-1a\", \"us-east-1b\"]). If left empty, the first two available AZs in the configured AWS region will be selected dynamically."
  default     = []

  validation {
    condition     = length(var.availability_zones) == 0 || length(var.availability_zones) >= 2
    error_message = "If explicitly specifying availability_zones, at least 2 Availability Zones must be provided to ensure Multi-AZ RDS DB Subnet Group compliance."
  }
}

# ------------------------------------------------------------------------------
# Cost Control & Gateway Configurations
# ------------------------------------------------------------------------------
variable "enable_nat_gateway" {
  type        = bool
  description = "Controls deployment of the AWS NAT Gateway and its Elastic IP. Set to false to avoid hourly NAT Gateway charges (~$32.40/month plus data transfer fees). When false, private subnets will not have direct outbound internet access."
  default     = false
}

# ------------------------------------------------------------------------------
# Security & Access Control
# ------------------------------------------------------------------------------
variable "allowed_http_cidr" {
  type        = string
  description = "CIDR block permitted for inbound HTTP (Port 80) access to the Apache web server."
  default     = "0.0.0.0/0"
}

variable "enable_ssh_ingress" {
  type        = bool
  description = "Controls whether inbound SSH (Port 22) is permitted on the EC2 security group. Default is false because AWS Systems Manager (SSM) provides secure, keyless browser terminal access without opening inbound ports."
  default     = false
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "Specific CIDR block permitted for inbound SSH (Port 22) administrative access. Strict security requirement: must NEVER be 0.0.0.0/0."
  default     = "127.0.0.1/32"

  validation {
    condition     = var.allowed_ssh_cidr != "0.0.0.0/0"
    error_message = "Security policy violation: SSH port 22 must never be exposed to the entire internet (0.0.0.0/0). Specify a specific administrative IP/CIDR (e.g., 203.0.113.25/32)."
  }
}

# ------------------------------------------------------------------------------
# EC2 Web Server Configuration
# ------------------------------------------------------------------------------
variable "ec2_instance_type" {
  type        = string
  description = "EC2 instance size for the Ubuntu Apache web server. t3.micro is AWS Free Tier eligible."
  default     = "t3.micro"
}

variable "ec2_key_name" {
  type        = string
  description = "Optional name of an existing EC2 Key Pair to enable traditional SSH access. Leave blank if utilizing AWS Systems Manager (SSM) Session Manager."
  default     = ""
}

# ------------------------------------------------------------------------------
# Amazon RDS MySQL Database Configuration
# ------------------------------------------------------------------------------
variable "enable_rds_instance" {
  type        = bool
  description = "Controls whether the Amazon RDS MySQL instance is provisioned. Set to false during early testing to minimize AWS billing."
  default     = true
}

variable "db_instance_class" {
  type        = string
  description = "Compute and memory capacity of the RDS DB instance. db.t3.micro and db.t4g.micro are AWS Free Tier eligible."
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  type        = number
  description = "Allocated storage size in Gigabytes (GB). AWS Free Tier includes up to 20 GB of gp2 storage."
  default     = 20
}

variable "db_name" {
  type        = string
  description = "Name of the initial MySQL database created inside the RDS instance. Must be alphanumeric."
  default     = "academicdb"
}

variable "db_username" {
  type        = string
  description = "Master administrator username for the MySQL RDS instance."
  default     = "dbadmin"
}

variable "db_password" {
  type        = string
  description = "Master administrator password for the MySQL RDS instance. Used when manage_master_user_password is false."
  default     = "AcademicPass2026!Db"
  sensitive   = true
}

variable "manage_master_user_password" {
  type        = bool
  description = "Enables AWS-managed master user password stored automatically in AWS Secrets Manager. When true, avoids storing plaintext credentials."
  default     = true
}

variable "enable_deletion_protection" {
  type        = bool
  description = "Controls database deletion protection. Keep false for easy academic project teardown."
  default     = false
}

variable "db_backup_retention_period" {
  type        = number
  description = "The number of days to retain automated database backups. Set between 1 and 35, or 0 to disable automated backups."
  default     = 1
}

variable "db_skip_final_snapshot" {
  type        = bool
  description = "Determines whether a final DB snapshot is created before the DB instance is deleted. Defaults to true for academic tear down."
  default     = true
}

# ------------------------------------------------------------------------------
# Amazon CloudWatch Monitoring & Observability
# ------------------------------------------------------------------------------
variable "enable_cloudwatch_alarms" {
  type        = bool
  description = "Controls provisioning of Amazon CloudWatch metric alarms for EC2 and RDS. AWS Free Tier includes 10 free alarms per month."
  default     = true
}

variable "alarm_cpu_threshold" {
  type        = number
  description = "Percentage CPU utilization threshold for triggering CloudWatch alarms."
  default     = 80
}


