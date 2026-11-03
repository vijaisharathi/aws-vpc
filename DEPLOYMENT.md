# Deployment & Operations Runbook

**Project Title**: VPC with Public and Private Subnets  
**Target Environment**: Amazon Web Services (AWS)  
**IaC Tool**: HashiCorp Terraform (v1.5.0+)  

---

## 1. Deployment Workflow Diagram

```mermaid
flowchart TD
    Start(["Start: Academic Deployment"]) --> Prereq["1. Verify Prerequisites<br/>(Terraform >= 1.5.0 & AWS CLI v2)"]
    Prereq --> Auth["2. Configure AWS Credentials<br/>(aws configure or IAM Role)"]
    Auth --> Clone["3. Prepare Workspace & Variables<br/>(cp terraform.tfvars.example terraform.tfvars)"]
    Clone --> Init["4. Execute terraform init<br/>(Downloads hashicorp/aws v5.x provider)"]
    Init --> Validate["5. Execute terraform validate<br/>(Confirms HCL syntax & references)"]
    Validate --> Plan["6. Execute terraform plan<br/>(Previews exact resource creation)"]
    Plan --> Approval{"7. Review & Approve Plan?"}
    Approval -- No --> Abort(["Abort Deployment"])
    Approval -- Yes --> Apply["8. Execute terraform apply<br/>(Provisions VPC, Subnets, EC2, RDS, IAM)"]
    Apply --> Verify["9. Post-Deployment Verification<br/>(Access Web Dashboard & Test SQL)"]
    Verify --> Complete(["10. Demonstration & Evaluation"])
    Complete --> Teardown["11. Safe Teardown<br/>(terraform destroy)"]
```

---

## 2. Prerequisites & Tooling Setup

### 2.1 Install Required Tools

#### Windows (PowerShell via Winget or Chocolatey)
```powershell
# Using Windows Package Manager (winget)
winget install HashiCorp.Terraform
winget install Amazon.AWSCLI

# Refresh current shell environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

#### Ubuntu / Debian Linux
```bash
# Install AWS CLI
sudo apt-get update && sudo apt-get install -y unzip curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform
```

### 2.2 Configure AWS Authentication
Configure credentials for an IAM principal possessing permissions to create VPC, Subnet, Route Table, IGW, NAT, EC2, RDS, CloudWatch, and IAM resources:
```bash
aws configure
```
Prompts:
- **AWS Access Key ID**: `AKIAXXXXXXXXXXXXXXXX`
- **AWS Secret Access Key**: `****************************************`
- **Default region name**: `us-east-1`
- **Default output format**: `json`

---

## 3. Step-by-Step Terraform Deployment

### Step 1: Initialize Variables Configuration
Copy the template variable definition file:
```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```
Review and customize parameters in `terraform.tfvars`:
- `aws_region = "us-east-1"`
- `enable_nat_gateway = false` (keep `false` for zero hourly NAT fees)
- `enable_rds_instance = true`
- `enable_cloudwatch_alarms = true`

### Step 2: Initialize Provider Plugins
```powershell
terraform init
```
Downloads and locks the AWS provider plugin (`hashicorp/aws v5.100.0`).

### Step 3: Validate Configuration Syntax
```powershell
terraform validate
```
Expected output: `Success! The configuration is valid.`

### Step 4: Generate Execution Plan (Dry Run)
```powershell
terraform plan -out=tfplan
```
Inspect the planned infrastructure changes. Confirms that no existing resources will be destructively modified.

### Step 5: Provision Infrastructure
```powershell
terraform apply "tfplan"
```
Provisions the custom VPC, subnets, route tables, internet gateway, security groups, IAM instance profile, EC2 instance with user-data, Amazon RDS MySQL instance, and CloudWatch alarms.

---

## 4. Post-Deployment Verification

### 4.1 Access the Web Dashboard
Retrieve the web server URL from outputs:
```powershell
terraform output web_server_url
```
Open the returned URL in your web browser:
```text
http://<web_server_public_ip>/
```
- Verify page title: `AWS VPC – Public and Private Subnet Demonstration`.
- Verify Apache status: `Running`.
- Verify RDS status: Switches to `Connected (Port 3306)` once database initialization completes.

### 4.2 Test Visitor Registration
1. Complete the visitor form on the dashboard:
   - Full Name: `Katherine Johnson`
   - Email: `katherine.johnson@nasa.gov`
2. Click **Register in Database**.
3. Confirm that the record is persisted into MySQL and appears immediately in the live visitor table.

### 4.3 Keyless Terminal Access via AWS Systems Manager (SSM)
Connect to the EC2 server without an SSH key pair or open port 22:
```powershell
aws ssm start-session --target (terraform output -raw web_server_instance_id)
```

---

## 5. Troubleshooting & Diagnostic Commands

| Issue | Diagnostic Command | Remediation Action |
| :--- | :--- | :--- |
| **Cloud-Init user-data not completed** | `sudo cat /var/log/user-data.log` | Check for package installation failures or APT lock delays during boot. |
| **Flask backend not running** | `sudo systemctl status vpc-app`<br/>`sudo journalctl -u vpc-app -n 50` | Verify Python virtual environment in `/opt/vpc-backend/venv` and check `/var/log/vpc-app/error.log`. |
| **Apache reverse proxy error (502 Bad Gateway)** | `sudo tail -n 50 /var/log/apache2/vpc_app_error.log` | Confirms Flask backend is listening on `127.0.0.1:5000`. Run `sudo systemctl restart vpc-app`. |
| **RDS connection timeout (Port 3306)** | `nc -zvw5 <rds_address> 3306` | Verify RDS is in `available` state; check that `db-sg` ingress permits `web-sg`. |
| **AWS Secrets Manager access denied** | `aws secretsmanager get-secret-value --secret-id <secret_arn>` | Verify EC2 IAM role has `secrets_read` policy attached. |

---

## 6. Safe Teardown & Decommissioning

To avoid ongoing charges for EC2, EBS, or public IPv4 addresses when academic grading or lab work is complete:
```powershell
terraform destroy
```
When prompted, type `yes` to permanently remove all provisioned infrastructure.
