# ==============================================================================
# Outputs Configuration
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# ------------------------------------------------------------------------------
# VPC Outputs
# ------------------------------------------------------------------------------
output "vpc_id" {
  description = "The unique identifier of the custom AWS VPC."
  value       = aws_vpc.main.id
}

output "vpc_arn" {
  description = "The Amazon Resource Name (ARN) of the custom AWS VPC."
  value       = aws_vpc.main.arn
}

output "vpc_cidr_block" {
  description = "The primary CIDR block of the custom VPC (10.0.0.0/16)."
  value       = aws_vpc.main.cidr_block
}

# ------------------------------------------------------------------------------
# Subnet Outputs
# ------------------------------------------------------------------------------
output "public_subnet_id" {
  description = "Identifier of the public web subnet (public-subnet-1, 10.0.1.0/24)."
  value       = aws_subnet.public.id
}

output "private_subnet_1_id" {
  description = "Identifier of private subnet 1 (private-subnet-1, 10.0.2.0/24 in AZ-A)."
  value       = aws_subnet.private.id
}

output "private_subnet_2_id" {
  description = "Identifier of private subnet 2 (private-subnet-2, 10.0.3.0/24 in AZ-B)."
  value       = aws_subnet.private_db.id
}

output "private_subnet_id" {
  description = "Alias identifier for the first private subnet (10.0.2.0/24)."
  value       = aws_subnet.private.id
}

output "private_db_subnet_id" {
  description = "Alias identifier for the second private DB subnet (10.0.3.0/24)."
  value       = aws_subnet.private_db.id
}

output "subnet_ids" {
  description = "Map of all created subnets and their corresponding AWS IDs."
  value = {
    public_subnet_1  = aws_subnet.public.id
    private_subnet_1 = aws_subnet.private.id
    private_subnet_2 = aws_subnet.private_db.id
  }
}

output "selected_availability_zones" {
  description = "List of Availability Zones assigned to the public and private subnets."
  value       = local.selected_azs
}

# ------------------------------------------------------------------------------
# Gateways Outputs
# ------------------------------------------------------------------------------
output "internet_gateway_id" {
  description = "The identifier of the VPC Internet Gateway."
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_id" {
  description = "The identifier of the NAT Gateway, if enabled."
  value       = var.enable_nat_gateway ? aws_nat_gateway.main[0].id : "Disabled (enable_nat_gateway = false)"
}

output "nat_gateway_public_ip" {
  description = "The Elastic IP address allocated to the NAT Gateway, if enabled."
  value       = var.enable_nat_gateway ? aws_eip.nat[0].public_ip : "Disabled"
}

# ------------------------------------------------------------------------------
# Security Groups Outputs
# ------------------------------------------------------------------------------
output "web_security_group_id" {
  description = "Security Group ID for the EC2 Web Server."
  value       = aws_security_group.web.id
}

output "db_security_group_id" {
  description = "Security Group ID for the Amazon RDS MySQL Database."
  value       = aws_security_group.db.id
}

# ------------------------------------------------------------------------------
# EC2 Web Server Outputs
# ------------------------------------------------------------------------------
output "web_server_instance_id" {
  description = "The AWS EC2 Instance ID of the Ubuntu Apache web server."
  value       = aws_instance.web.id
}

output "web_server_public_ip" {
  description = "The public IPv4 address assigned to the EC2 Web Server."
  value       = aws_instance.web.public_ip
}

output "web_server_public_dns" {
  description = "The public DNS hostname assigned to the EC2 Web Server."
  value       = aws_instance.web.public_dns
}

output "web_server_private_ip" {
  description = "The private IPv4 address assigned to the EC2 Web Server inside the 10.0.1.0/24 subnet."
  value       = aws_instance.web.private_ip
}

output "web_server_url" {
  description = "Direct HTTP URL to access the deployed Apache web server."
  value       = "http://${aws_instance.web.public_ip}"
}

# ------------------------------------------------------------------------------
# Amazon RDS MySQL Outputs
# ------------------------------------------------------------------------------
output "rds_endpoint" {
  description = "The connection endpoint for the Amazon RDS MySQL instance."
  value       = var.enable_rds_instance ? aws_db_instance.mysql[0].endpoint : "RDS Disabled (enable_rds_instance = false)"
}

output "rds_address" {
  description = "The hostname address of the Amazon RDS MySQL database."
  value       = var.enable_rds_instance ? aws_db_instance.mysql[0].address : "RDS Disabled"
}

output "rds_port" {
  description = "The database connection port (MySQL default 3306)."
  value       = var.enable_rds_instance ? aws_db_instance.mysql[0].port : 3306
}

output "rds_database_name" {
  description = "The initial MySQL database name created."
  value       = var.enable_rds_instance ? aws_db_instance.mysql[0].db_name : "None"
}

output "rds_username" {
  description = "The master database administrator username."
  value       = var.enable_rds_instance ? aws_db_instance.mysql[0].username : "None"
}

output "rds_db_subnet_group_name" {
  description = "The name of the RDS DB Subnet Group spanning the private subnets."
  value       = aws_db_subnet_group.main.name
}

output "rds_master_user_secret_arn" {
  description = "The ARN of the AWS-managed Secrets Manager secret containing the RDS master password."
  value       = var.enable_rds_instance && var.manage_master_user_password ? try(aws_db_instance.mysql[0].master_user_secret[0].secret_arn, "Provisioned upon apply") : "None"
}

# ------------------------------------------------------------------------------
# Monitoring Outputs
# ------------------------------------------------------------------------------
output "cloudwatch_dashboard_name" {
  description = "The name of the unified Amazon CloudWatch operations dashboard."
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "cloudwatch_ec2_alarm_arn" {
  description = "The ARN of the EC2 High CPU Utilization CloudWatch alarm."
  value       = var.enable_cloudwatch_alarms ? aws_cloudwatch_metric_alarm.ec2_high_cpu[0].arn : "Disabled"
}



