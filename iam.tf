# ==============================================================================
# IAM Roles, Instance Profiles, and Secrets Manager Policies
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IAM Role for EC2 Instance
# Allows EC2 instance to assume an IAM role for secure AWS service interactions
# ------------------------------------------------------------------------------
resource "aws_iam_role" "ec2_ssm_role" {
  name        = "${local.name_prefix}-ec2-role"
  description = "Allows EC2 instance to interact with AWS Systems Manager and read DB credentials"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${local.name_prefix}-ec2-role"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# ------------------------------------------------------------------------------
# 2. Attach AWS Systems Manager (SSM) Managed Policy
# Enables AWS Systems Manager Session Manager for browser-based, keyless terminal access.
# Eliminates the security risk of opening SSH Port 22 to the public internet.
# ------------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ------------------------------------------------------------------------------
# 3. AWS Secrets Manager Secret for RDS Database Credentials
# Securely stores database administrator username, password, and db name.
# ------------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${local.name_prefix}-rds-db-secret"
  description             = "Master credentials for the Amazon RDS MySQL database"
  recovery_window_in_days = 0 # Allows immediate deletion during academic teardown

  tags = {
    Name        = "${local.name_prefix}-rds-db-secret"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    engine   = "mysql"
    host     = var.enable_rds_instance ? aws_db_instance.mysql[0].address : "pending"
    port     = 3306
    username = var.db_username
    password = var.db_password
    database = var.db_name
  })
}

# ------------------------------------------------------------------------------
# 4. Least-Privilege IAM Policy for Secrets Manager
# Grants the EC2 web server permission ONLY to retrieve this specific DB secret.
# ------------------------------------------------------------------------------
resource "aws_iam_policy" "secrets_read" {
  name        = "${local.name_prefix}-secrets-read-policy"
  description = "Grants least-privilege read access strictly to the RDS database secret"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowReadSpecificDbSecret"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = distinct(compact([
          aws_secretsmanager_secret.db_credentials.arn,
          var.enable_rds_instance && var.manage_master_user_password ? try(aws_db_instance.mysql[0].master_user_secret[0].secret_arn, "") : ""
        ]))
      },
      {
        Sid    = "AllowKmsDecryptDbSecret"
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${local.name_prefix}-secrets-read-policy"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

resource "aws_iam_role_policy_attachment" "secrets_read_attach" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = aws_iam_policy.secrets_read.arn
}

# ------------------------------------------------------------------------------
# 5. IAM Instance Profile for EC2 Web Server
# ------------------------------------------------------------------------------
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${local.name_prefix}-ec2-instance-profile"
  role = aws_iam_role.ec2_ssm_role.name

  tags = {
    Name        = "${local.name_prefix}-ec2-instance-profile"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# ------------------------------------------------------------------------------
# 6. Least-Privilege IAM Policy for AWS Infrastructure Discovery
# Grants EC2 web server read-only/describe permissions to query VPC, Subnets,
# Route Tables, Gateways, EC2 metadata, RDS metadata, Security Groups,
# and CloudWatch metrics via Boto3.
# ------------------------------------------------------------------------------
resource "aws_iam_policy" "infra_read" {
  name        = "${local.name_prefix}-infra-read-policy"
  description = "Grants least-privilege describe access to VPC, EC2, RDS, and CloudWatch metrics"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowEc2InfrastructureDescribe"
        Effect = "Allow"
        Action = [
          "ec2:DescribeVpcs",
          "ec2:DescribeVpcAttribute",
          "ec2:DescribeSubnets",
          "ec2:DescribeRouteTables",
          "ec2:DescribeInternetGateways",
          "ec2:DescribeNatGateways",
          "ec2:DescribeInstances",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeAddresses",
          "ec2:DescribeAvailabilityZones"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowRdsInfrastructureDescribe"
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBSubnetGroups"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowCloudWatchMetricsRead"
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowIamRoleInspection"
        Effect = "Allow"
        Action = [
          "iam:GetInstanceProfile",
          "iam:GetRole",
          "iam:ListAttachedRolePolicies"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${local.name_prefix}-infra-read-policy"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

resource "aws_iam_role_policy_attachment" "infra_read_attach" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = aws_iam_policy.infra_read.arn
}

# ------------------------------------------------------------------------------
# 6. S3 Read Access for Application Package Bootstrap
# ------------------------------------------------------------------------------
resource "aws_iam_policy" "s3_read" {
  name        = "${local.name_prefix}-s3-read-policy"
  description = "Allows EC2 instance to download application bundle from the deployment S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3GetAppBundle"
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.assets.arn}/*"
      }
    ]
  })

  tags = {
    Name        = "${local.name_prefix}-s3-read-policy"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

resource "aws_iam_role_policy_attachment" "s3_read_attach" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = aws_iam_policy.s3_read.arn
}

