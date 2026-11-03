# AWS Cloud Cost Estimation & Free Tier Architecture Guide

**Project Title**: AWS VPC with Public and Private Subnets  
**Evaluation Standard**: AWS Pricing Model & AWS Free Tier Program  
**Region Evaluated**: `us-east-1` (US East - N. Virginia)  

---

## 1. Executive Cost Summary

This academic cloud architecture is specifically engineered to operate within the **AWS Free Tier (12-Month Tier and Always Free Tier)**. All major compute, database, and storage parameters are configured to prevent unexpected charges during student laboratory work and academic grading.

### Key Cost Optimizations:
1. **NAT Gateway Disabled by Default**: AWS charges **$0.045/hour (~$32.40/month)** plus $0.045/GB data processed for every active NAT Gateway. In our code, `enable_nat_gateway = false` ensures zero NAT charges.
2. **Single-AZ RDS Database**: Configured as Single-AZ (`multi_az = false`) on `db.t3.micro`, consuming 0 paid Multi-AZ replica hours.
3. **Free Tier Sized Storage**: EC2 root volume is 20 GB gp3 (under the 30 GB monthly EBS free tier limit); RDS storage is 20 GB gp2 (under the 20 GB monthly RDS storage free tier limit).
4. **Secrets Manager Immediate Deletion**: Secrets declare `recovery_window_in_days = 0`, allowing instant teardown upon `terraform destroy` without retention fees.

---

## 2. Resource-by-Resource Cost Breakdown

| Component | AWS Resource | AWS Free Tier Allowance | Standard On-Demand Rate (us-east-1) | Estimated Monthly Cost (Free Tier Active) | Estimated Monthly Cost (Post-Free Tier) |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Custom VPC & Subnets** | `aws_vpc`, `aws_subnet` | **Always Free** | $0.00 / hour | **$0.00** | **$0.00** |
| **Route Tables & Associations**| `aws_route_table` | **Always Free** | $0.00 / hour | **$0.00** | **$0.00** |
| **Internet Gateway** | `aws_internet_gateway` | **Always Free** | $0.00 / hour | **$0.00** | **$0.00** |
| **EC2 Compute** | `t2.micro` or `t3.micro` | **750 hours/month** (12-Month Free Tier) | $0.0104 / hour (~$7.49/mo) | **$0.00** | $7.49 |
| **EBS Root Volume** | 20 GB gp3 Volume | **30 GB/month** (12-Month Free Tier) | $0.08 / GB-month | **$0.00** | $1.60 |
| **Amazon RDS MySQL** | `db.t3.micro` Single-AZ | **750 hours/month** (12-Month Free Tier) | $0.017 / hour (~$12.24/mo) | **$0.00** | $12.24 |
| **RDS Storage & Backup** | 20 GB gp2 + 20 GB Backup | **20 GB Storage + 20 GB Backup** | $0.115 / GB-month | **$0.00** | $2.30 |
| **Public IPv4 Address** | EC2 In-Use Public IPv4 | No free tier (AWS policy effective Feb 2024) | $0.005 / hour (~$3.60/mo) | **~$3.60** | ~$3.60 |
| **AWS Systems Manager (SSM)** | Core Session Manager | **Always Free** | $0.00 / hour | **$0.00** | **$0.00** |
| **AWS Secrets Manager** | Database Secret (1 secret) | 30-day free trial on new secrets | $0.40 / secret-month | **$0.00** | $0.40 |
| **Amazon CloudWatch** | 10 Metrics + 10 Alarms | **Always Free** (Up to 10 alarms) | $0.10 / alarm-month | **$0.00** | $0.00 |
| **AWS NAT Gateway** | `aws_nat_gateway` + EIP | **No free tier** | $0.045 / hr + $0.005 / hr EIP | **$0.00** *(Disabled)* | **$0.00** *(Disabled)* |
| **Total Estimated Cost** | — | — | — | **~$3.60 / month** | **~$27.63 / month** |

*Note: For student evaluation sessions running 2 to 4 hours, total AWS billing will be approximately **$0.05 to $0.10**.*

---

## 3. High-Cost Resources & How They Are Controlled

### 3.1 AWS NAT Gateway ($32.40+/month)
- **Why It Incurs Charges**: AWS deploys a dedicated, managed network device with redundant data planes, billing $0.045 per hour plus $0.045 per gigabyte of data processed.
- **How It is Controlled**:
  In [`variables.tf`](file:///D:/Kottai%20kannan/variables.tf#L108-L113):
  ```hcl
  variable "enable_nat_gateway" {
    type        = bool
    description = "Controls deployment of the AWS NAT Gateway..."
    default     = false
  }
  ```
  When set to `false`, Terraform evaluates `count = 0` on both `aws_nat_gateway.main` and `aws_eip.nat`, allocating zero gateways.

### 3.2 In-Use Public IPv4 Address Pricing ($3.60/month)
- **Why It Incurs Charges**: Effective February 1, 2024, AWS charges $0.005/hour for all public IPv4 addresses, regardless of whether an instance is in the Free Tier.
- **How It is Controlled**: Keep instances active only during evaluation. Execute `terraform destroy` when finished.

### 3.3 Storage Auto-Scaling Surprises
- **Why It Incurs Charges**: If an RDS database receives large bursts of data, default AWS settings may automatically expand storage up to 1,000 GB, generating unintended EBS storage charges.
- **How It is Controlled**:
  In [`rds.tf`](file:///D:/Kottai%20kannan/rds.tf#L35):
  ```hcl
  max_allocated_storage = var.db_allocated_storage
  ```
  Storage auto-scaling is capped strictly to the initial 20 GB allocation.

---

## 4. Cost Avoidance & Teardown Protocol

To ensure 100% cost avoidance after completing academic demonstration:
```powershell
# Decommission all provisioned resources
terraform destroy
```
- Destroys the EC2 instance and terminates public IPv4 billing.
- Destroys the RDS database without taking an expensive final snapshot (`skip_final_snapshot = true`).
- Deletes the Secrets Manager secret without a 30-day retention lock (`recovery_window_in_days = 0`).
- Removes the VPC, subnets, route tables, and security groups.
