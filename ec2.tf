# ==============================================================================
# Amazon EC2 Web Server Configuration
# Project: AWS VPC – Public and Private Subnet Demonstration
# ==============================================================================

# ------------------------------------------------------------------------------
# Apache Web Server & Python Flask Backend on Ubuntu Linux
# Deployed strictly within the Public Subnet (public-subnet-1)
# ------------------------------------------------------------------------------
resource "aws_instance" "web" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.ec2_instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = true
  key_name                    = var.ec2_key_name != "" ? var.ec2_key_name : null

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name        = "${local.name_prefix}-web-root-ebs"
      Environment = var.environment
      Project     = var.project_name
      Owner       = var.owner
    }
  }

  # Decoupled application tier orchestration:
  # Application bundle is securely retrieved from the deployment S3 bucket during
  # cloud-init, keeping user_data payload well below the AWS 16KB limit.
  user_data = templatefile("${path.module}/scripts/user_data.sh.tftpl", {
    project_title         = "AWS VPC – Public and Private Subnet Demonstration"
    vpc_id                = aws_vpc.main.id
    vpc_cidr              = var.vpc_cidr
    public_subnet_cidr    = var.public_subnet_cidr
    private_subnet_1_cidr = var.private_subnet_cidr
    private_subnet_2_cidr = var.private_db_subnet_cidr
    db_host               = var.enable_rds_instance ? aws_db_instance.mysql[0].address : "pending"
    db_name               = var.db_name
    db_user               = var.db_username
    db_pass               = var.manage_master_user_password ? "" : var.db_password
    db_secret_name        = var.enable_rds_instance && var.manage_master_user_password ? try(aws_db_instance.mysql[0].master_user_secret[0].secret_arn, aws_secretsmanager_secret.db_credentials.name) : aws_secretsmanager_secret.db_credentials.name
    aws_region            = var.aws_region
    assets_bucket         = aws_s3_bucket.assets.id
  })

  tags = {
    Name        = "${local.name_prefix}-web-server"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Public-Web"
    Role        = "WebServer"
  }
}
