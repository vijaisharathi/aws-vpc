# ==============================================================================
# S3 Deployment Bucket (Application Package Storage)
# Project: VPC with Public and Private Subnets (Academic Project)
# ==============================================================================

# Private S3 bucket to store application zip archive for EC2 Cloud-Init bootstrap
# Eliminates the AWS EC2 user_data 16,384-byte payload limitation
resource "aws_s3_bucket" "assets" {
  bucket_prefix = "${local.name_prefix}-assets-"
  force_destroy = true

  tags = {
    Name        = "${local.name_prefix}-assets-bucket"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
    Tier        = "Storage"
  }
}

# Block all public ingress to the asset bucket
resource "aws_s3_bucket_public_access_block" "assets" {
  bucket                  = aws_s3_bucket.assets.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Upload the packaged application archive
resource "aws_s3_object" "app_bundle" {
  bucket = aws_s3_bucket.assets.id
  key    = "app.zip"
  source = "${path.module}/app.zip"
  etag   = filemd5("${path.module}/app.zip")

  tags = {
    Name        = "${local.name_prefix}-app-bundle"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

