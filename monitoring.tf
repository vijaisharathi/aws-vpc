# ==============================================================================
# Amazon CloudWatch Monitoring, Metrics, and Alarms
# Project: AWS VPC – Public and Private Subnet Demonstration
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. EC2 Web Server High CPU Utilization Alarm
# Alerts when EC2 CPU exceeds threshold for two consecutive 5-minute periods.
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "ec2_high_cpu" {
  count               = var.enable_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${local.name_prefix}-ec2-high-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = var.alarm_cpu_threshold
  alarm_description   = "Triggers when EC2 Apache/Flask instance CPU utilization exceeds ${var.alarm_cpu_threshold}%"

  dimensions = {
    InstanceId = aws_instance.web.id
  }

  tags = {
    Name        = "${local.name_prefix}-ec2-high-cpu-alarm"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# ------------------------------------------------------------------------------
# 2. RDS MySQL High CPU Utilization Alarm (Conditional)
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "rds_high_cpu" {
  count               = var.enable_cloudwatch_alarms && var.enable_rds_instance ? 1 : 0
  alarm_name          = "${local.name_prefix}-rds-high-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.alarm_cpu_threshold
  alarm_description   = "Triggers when Amazon RDS MySQL CPU utilization exceeds ${var.alarm_cpu_threshold}%"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.mysql[0].identifier
  }

  tags = {
    Name        = "${local.name_prefix}-rds-high-cpu-alarm"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# ------------------------------------------------------------------------------
# 3. RDS MySQL Low Freeable Memory Alarm (Conditional)
# Alerts when available database memory falls below 64 MB.
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "rds_low_memory" {
  count               = var.enable_cloudwatch_alarms && var.enable_rds_instance ? 1 : 0
  alarm_name          = "${local.name_prefix}-rds-low-memory"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 67108864 # 64 Megabytes in bytes
  alarm_description   = "Triggers when RDS freeable memory drops below 64 MB"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.mysql[0].identifier
  }

  tags = {
    Name        = "${local.name_prefix}-rds-low-memory-alarm"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# ------------------------------------------------------------------------------
# 4. Centralized CloudWatch Operations Dashboard
# Combines compute and database metrics into a single unified monitoring console.
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "EC2 Web Server: CPU Utilization (%)"
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.web.id]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "EC2 Network I/O (Bytes)"
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/EC2", "NetworkIn", "InstanceId", aws_instance.web.id],
            ["AWS/EC2", "NetworkOut", "InstanceId", aws_instance.web.id]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "Amazon RDS MySQL: CPU Utilization (%)"
          view    = "timeSeries"
          stacked = false
          metrics = var.enable_rds_instance ? [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", aws_db_instance.mysql[0].identifier]
          ] : []
          period = 300
          stat   = "Average"
          region = var.aws_region
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "Amazon RDS MySQL: Database Connections & Free Memory"
          view    = "timeSeries"
          stacked = false
          metrics = var.enable_rds_instance ? [
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", aws_db_instance.mysql[0].identifier],
            ["AWS/RDS", "FreeableMemory", "DBInstanceIdentifier", aws_db_instance.mysql[0].identifier]
          ] : []
          period = 300
          stat   = "Average"
          region = var.aws_region
        }
      }
    ]
  })
}
