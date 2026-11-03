```text
 ██████╗ ██╗   ██╗███████╗██████╗ ██╗   ██╗██╗  ██╗ ██████╗ ██╗     ██╗ ██████╗
██╔═══██╗██║   ██║██╔════╝██╔══██╗╚██╗ ██╔╝██║  ██║██╔═══██╗██║     ██║██╔════╝
██║   ██║██║   ██║█████╗  ██████╔╝ ╚████╔╝ ███████║██║   ██║██║     ██║██║
██║▄▄ ██║██║   ██║██╔══╝  ██╔══██╗  ╚██╔╝  ██╔══██║██║   ██║██║     ██║██║
╚██████╔╝╚██████╔╝███████╗██║  ██║   ██║   ██║  ██║╚██████╔╝███████╗██║╚██████╗
 ╚══▀▀═╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝
┌─────────────────────────────────────────────────────────────────────────────┐
│          AWS VIRTUAL PRIVATE CLOUD WITH PUBLIC & PRIVATE SUBNETS            │
│               Academic Infrastructure Engineering & Security Lab            │
└─────────────────────────────────────────────────────────────────────────────┘
```

# AWS VPC with Public and Private Subnets: Complete PRD & Step-by-Step Implementation Guide

[![AWS](https://img.shields.io/badge/AWS-VPC_10.0.0.0%2F16-FF9900?logo=amazon-aws&logoColor=white)](#)
[![Terraform](https://img.shields.io/badge/IaC-Terraform_v1.5%2B-844FBA?logo=terraform&logoColor=white)](#)
[![Database](https://img.shields.io/badge/Database-RDS_MySQL_8.0_(Private)-4479A1?logo=mysql&logoColor=white)](#)
[![Runtime](https://img.shields.io/badge/Runtime-100%25_Offline_Local--First-7CB342)](#)  
[![Tests](https://img.shields.io/badge/Tests-67%2F67_Passing_(100%25)-success?logo=pytest&logoColor=white)](#)
[![Security](https://img.shields.io/badge/Security-AWS_SSM_(Zero_SSH_Keys)-0073BB)](#)
[![Cost](https://img.shields.io/badge/Cost-100%25_Free_Tier_Eligible-brightgreen)](#)
[![Region](https://img.shields.io/badge/Region-ap--southeast--2-232F3E?logo=amazon-aws&logoColor=white)](#)

> **Official Academic Cloud Engineering Project**  
> **Topic**: Design and Implementation of an AWS Virtual Private Cloud (VPC) with Public and Private Subnets, EC2 Web Tier, Isolated Amazon RDS MySQL Database, and Automated Infrastructure Validation.  
> **Source of Truth**: Original Course Presentation (PPT)  
> **Author / Student**: Kottai Kannan  
> **Target Audience**: Beginners, Students, Teammates, Cloud Engineers, and Academic Evaluators.

---

## 📑 Table of Contents

1. [Executive Summary & Concept Overview (Explain Like I'm 5)](#1-executive-summary--concept-overview-explain-like-im-5)
2. [Product Requirements Document (PRD)](#2-product-requirements-document-prd)
   - [2.1 Problem Statement](#21-problem-statement)
   - [2.2 Project Objectives](#22-project-objectives)
   - [2.3 Functional Requirements](#23-functional-requirements)
   - [2.4 Non-Functional Requirements & Governance](#24-non-functional-requirements--governance)
   - [2.5 Network Architecture & CIDR Specification](#25-network-architecture--cidr-specification)
   - [2.6 Architecture Flow Diagrams](#26-architecture-flow-diagrams)
3. [Project Features & The 8 Core Deliverables](#3-project-features--the-8-core-deliverables)
4. [Master Step-by-Step Implementation Plan (From Scratch)](#4-master-step-by-step-implementation-plan-from-scratch)
   - [Phase 0: Prerequisites & Initial Setup](#phase-0-prerequisites--initial-setup)
   - [Phase 1: Local Development & Demonstration (100% Offline, Zero AWS Cost)](#phase-1-local-development--demonstration-100-offline-zero-aws-cost)
   - [Phase 2: Automated Testing & Validation Suites](#phase-2-automated-testing--validation-suites)
   - [Phase 3: Deploying to Live AWS Cloud via Terraform](#phase-3-deploying-to-live-aws-cloud-via-terraform)
   - [Phase 4: Academic Viva & Presentation Walkthrough](#phase-4-academic-viva--presentation-walkthrough)
   - [Phase 5: Safe Teardown & Cost Elimination](#phase-5-safe-teardown--cost-elimination)
5. [Complete Troubleshooting Manual (Real-World Solutions)](#5-complete-troubleshooting-manual-real-world-solutions)
6. [Repository & Codebase Architecture Map](#6-repository--codebase-architecture-map)

---

```text
 ██████╗ ██╗   ██╗███████╗██████╗ ██╗   ██╗██╗███████╗██╗    ██╗
██╔═══██╗██║   ██║██╔════╝██╔══██╗██║   ██║██║██╔════╝██║    ██║
██║   ██║██║   ██║█████╗  ██████╔╝██║   ██║██║█████╗  ██║ █╗ ██║
██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
╚██████╔╝ ╚████╔╝ ███████╗██║  ██║ ╚████╔╝ ██║███████╗╚███╔███╔╝
 ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝
```

## 1. Executive Summary & Concept Overview (Explain Like I'm 5)

### What is the real-world problem?

Imagine you own a bank.

- If you place your bank's cash vault directly on the sidewalk on a public street, anyone walking past can try to pick the lock, photograph the safe, or blow it open.
- In the cloud computing world, **many companies accidentally place their database on the public internet**. Hackers use automated port scanners to discover open database ports (like MySQL port 3306), brute-force passwords, or exploit vulnerabilities to steal user records.

### How does this project solve it?

We build a secure, private cloud network called an **AWS Virtual Private Cloud (VPC)**. Inside this network, we construct two separate zones:

1. **The Public Subnet (The "Bank Reception / Storefront")**:
   - Hosts our **EC2 Web Server** (Ubuntu Linux, Apache HTTP Server, and Python Flask).
   - This server has a public IP address and connects to an **Internet Gateway (IGW)**.
   - Anyone on the internet can visit the website over standard HTTP (port 80) or HTTPS (port 443).

2. **The Private Subnet (The "Bank Vault")**:
   - Hosts our **Amazon RDS MySQL Database**.
   - It has **zero public IP addresses** and **no connection to the Internet Gateway**.
   - People on the internet **cannot touch, ping, or see this database**.
   - Only the EC2 Web Server inside our public subnet is permitted to talk to the database over an internal private network cable (TCP port 3306).

3. **The NAT Gateway (The "One-Way Emergency Exit")**:
   - What happens if the database needs to download a security patch from the internet?
   - A **NAT Gateway** (Network Address Translation) is placed in the public subnet. It allows resources in the private subnet to reach outward to the internet, but **blocks anyone on the internet from initiating an inbound connection**.

4. **Security Group Chaining (The "VIP Pass")**:
   - Instead of allowing any computer on the internal network to talk to MySQL, the database security group checks for a specific "VIP badge": the **EC2 Web Security Group ID (`sg-web`)**. Only packets tagged with this ID are accepted.

---

```text
██████╗ ██████╗ ██████╗
██╔══██╗██╔══██╗██╔══██╗
██████╔╝██████╔╝██║  ██║
██╔═══╝ ██╔══██╗██║  ██║
██║     ██║  ██║██████╔╝
╚═╝     ╚═╝  ╚═╝╚═════╝
```

## 2. Product Requirements Document (PRD)

### 2.1 Problem Statement

Deploying web applications with unsegmented architectures exposes sensitive data stores to automated reconnaissance, distributed denial of service (DDoS), and unauthorized data exfiltration. Academic and enterprise standards demand a segmented network boundary enforcing defense-in-depth, least-privilege security controls, and keyless systems governance.

### 2.2 Project Objectives

- **Automated Provisioning**: Implement HashiCorp Terraform (Infrastructure as Code) to deploy an entire production-ready VPC network idempotently.
- **Strict Network Segmentation**: Partition CIDR `10.0.0.0/16` into isolated public (`10.0.1.0/24`) and private (`10.0.2.0/24`, `10.0.3.0/24`) subnets.
- **Zero Public Exposure for Data**: Ensure Amazon RDS MySQL has `publicly_accessible = false` and resides in a Multi-AZ DB subnet group.
- **Keyless Server Governance**: Eliminate open SSH port 22; implement **AWS Systems Manager (SSM)** for encrypted browser-based shell access.
- **Secure Secret Storage**: Store database administrator credentials in **AWS Secrets Manager** and load them dynamically via an IAM role.
- **Dual-Environment Reliability**: Provide a complete, lightweight **SQLite simulation engine** so students and teammates can run and test the full application locally with zero cloud costs.

### 2.3 Functional Requirements

| ID        | Requirement Category | Detailed Functional Description                                                                                                                                                      | Implementation File                                                                                                                      |
| :-------- | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| **FR-01** | VPC & CIDR           | Allocate IPv4 CIDR `10.0.0.0/16`. Enable DNS resolution and DNS hostnames.                                                                                                           | [`vpc.tf`](file:///d:/Kottai%20kannan/vpc.tf)                                                                                            |
| **FR-02** | Subnet Architecture  | Provision Public Subnet (`10.0.1.0/24`) in AZ-A. Provision Private Subnet 1 (`10.0.2.0/24`) in AZ-A. Provision Private Subnet 2 (`10.0.3.0/24`) in AZ-B for RDS Multi-AZ compliance. | [`subnets.tf`](file:///d:/Kottai%20kannan/subnets.tf)                                                                                    |
| **FR-03** | Gateways & Routing   | Attach Internet Gateway to VPC. Configure Public Route Table (`0.0.0.0/0 -> IGW`). Provision conditional NAT Gateway with Elastic IP. Configure Private Route Table.                 | [`gateways.tf`](file:///d:/Kottai%20kannan/gateways.tf), [`route_tables.tf`](file:///d:/Kottai%20kannan/route_tables.tf)                 |
| **FR-04** | Security Groups      | Web SG: Inbound HTTP 80 & HTTPS 443; restricted SSH; least-privilege egress. DB SG: Inbound MySQL 3306 restricted strictly to `aws_security_group.web.id`.                           | [`security_groups.tf`](file:///d:/Kottai%20kannan/security_groups.tf)                                                                    |
| **FR-05** | IAM & Secrets        | EC2 IAM role with `AmazonSSMManagedInstanceCore`. Scoped IAM policy for Secrets Manager read access. Private S3 bucket read policy.                                                  | [`iam.tf`](file:///d:/Kottai%20kannan/iam.tf)                                                                                            |
| **FR-06** | Compute Web Tier     | Ubuntu 22.04 LTS `t3.micro` instance in Public Subnet. Cloud-Init script orchestrating Apache reverse proxy, Gunicorn, and Python Flask.                                             | [`ec2.tf`](file:///d:/Kottai%20kannan/ec2.tf), [`scripts/user_data.sh.tftpl`](file:///d:/Kottai%20kannan/scripts/user_data.sh.tftpl)     |
| **FR-07** | Database Tier        | Amazon RDS MySQL 8.0 on `db.t3.micro`. Storage encrypted at rest with AWS KMS AES-256. Automated backup retention and private networking.                                            | [`rds.tf`](file:///d:/Kottai%20kannan/rds.tf)                                                                                            |
| **FR-08** | Validation Engine    | Automated 7-point PPT connectivity test runner covering HTTP ingress, IGW routing, private isolation, NAT egress, and EC2-to-RDS TCP socket probe.                                   | [`backend/app.py`](file:///d:/Kottai%20kannan/backend/app.py), [`test_stage5_audit.py`](file:///d:/Kottai%20kannan/test_stage5_audit.py) |

### 2.4 Non-Functional Requirements & Governance

- **Cost Optimization**: Default configuration stays 100% within the **AWS Free Tier** (`t3.micro` EC2, `db.t3.micro` RDS, single-AZ academic mode, NAT Gateway toggleable via `enable_nat_gateway = false`).
- **Resilience**: Cloud-Init decouples application code from user data limits by uploading code to an S3 deployment bucket.
- **Portability**: Auto-detects runtime mode (`DEVELOPMENT` with SQLite vs. `AWS_PRODUCTION` with RDS MySQL).
- **Security**: No secrets or passwords stored in plaintext in git or client code.

### 2.5 Network Architecture & CIDR Specification

| Network Entity       | IPv4 CIDR Block | Usable IPs | Availability Zone |  Internet Access Mode   | Primary Workload Hosted          |
| :------------------- | :-------------- | :--------: | :---------------: | :---------------------: | :------------------------------- |
| **Custom VPC**       | `10.0.0.0/16`   |   65,536   |     Regional      |    Via IGW / NAT GW     | Entire Cloud Environment         |
| **Public Subnet**    | `10.0.1.0/24`   |    251     | `ap-southeast-2a` |  Bidirectional via IGW  | Apache Web Server & NAT Gateway  |
| **Private Subnet 1** | `10.0.2.0/24`   |    251     | `ap-southeast-2a` | Outbound only (via NAT) | RDS MySQL Primary Instance       |
| **Private Subnet 2** | `10.0.3.0/24`   |    251     | `ap-southeast-2b` | Outbound only (via NAT) | RDS DB Subnet Group Secondary AZ |

---

```text
 █████╗ ██████╗  ██████╗██╗  ██╗██╗████████╗███████╗ ██████╗████████╗██╗   ██╗██████╗ ███████╗
██╔══██╗██╔══██╗██╔════╝██║  ██║██║╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗██╔════╝
███████║██████╔╝██║     ███████║██║   ██║   █████╗  ██║        ██║   ██║   ██║██████╔╝█████╗
██╔══██║██╔══██╗██║     ██╔══██║██║   ██║   ██╔══╝  ██║        ██║   ██║   ██║██╔══██╗██╔══╝
██║  ██║██║  ██║╚██████╗██║  ██║██║   ██║   ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║███████╗
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
```

### 2.6 Architecture Flow Diagrams

#### End-to-End Infrastructure Diagram

```mermaid
flowchart TB
    subgraph Internet_Zone ["Public Internet"]
        Users["Web Users / Evaluators<br/>(HTTP Port 80)"]
        Admins["Administrators<br/>(AWS SSM Session Manager)"]
    end

    subgraph AWS_Cloud ["AWS Cloud (Region: ap-southeast-2 / Sydney)"]
        IGW["Internet Gateway (IGW)<br/>0.0.0.0/0 Direct Ingress & Egress"]

        subgraph VPC ["Custom AWS VPC: 10.0.0.0/16 (DNS Hostnames Enabled)"]

            subgraph AZ_A ["Availability Zone A (ap-southeast-2a)"]
                subgraph PublicSubnet ["Public Web Subnet: 10.0.1.0/24"]
                    EC2["EC2 Web Server (Ubuntu 22.04 LTS)<br/>Apache Reverse Proxy + Python Flask App<br/>Public IP: 54.x.x.x | Private: 10.0.1.x"]
                    NATGW["NAT Gateway<br/>Allocated Elastic IP (EIP)"]
                    SGW["EC2 Security Group (sg-web)<br/>Inbound: HTTP 80, HTTPS 443<br/>Outbound: Least-Privilege"]
                end

                subgraph PrivateSubnet1 ["Private Subnet 1 (App/DB): 10.0.2.0/24"]
                    RDS_Master["Amazon RDS MySQL 8.0<br/>Private IP: 10.0.2.x<br/>Publicly Accessible: FALSE"]
                    SGDB["RDS Security Group (sg-db)<br/>Inbound: TCP 3306 ONLY from sg-web<br/>Outbound: VPC CIDR Only"]
                end
            end

            subgraph AZ_B ["Availability Zone B (ap-southeast-2b)"]
                subgraph PrivateSubnet2 ["Private Subnet 2 (DB AZ-B): 10.0.3.0/24"]
                    RDS_SubnetGroup["DB Subnet Group Member<br/>(Satisfies AWS RDS Multi-AZ Mandate)"]
                end
            end

            PublicRT["Public Route Table<br/>0.0.0.0/0 -> Internet Gateway (IGW)"]
            PrivateRT["Private Route Table<br/>0.0.0.0/0 -> NAT Gateway (Outbound Only)"]
        end

        SSM["AWS Systems Manager (SSM)<br/>Keyless Encrypted Management"]
        SecretsMgr["AWS Secrets Manager<br/>Master DB Credentials Secret"]
        S3Bucket["Deployment S3 Bucket<br/>Application Code (app.zip)"]
    end

    Users -->|HTTP 80 / HTTPS 443| IGW
    IGW -->|Public Route Table| PublicSubnet
    PublicSubnet --> EC2
    EC2 -->|MySQL TCP 3306 (Internal VPC)| RDS_Master
    RDS_Master -.->|Outbound Updates (via Private RT)| NATGW
    NATGW -->|Egress to Internet| IGW
    Admins -->|Encrypted HTTPS TLS| SSM
    SSM --> EC2
    EC2 -->|IAM Instance Profile| SecretsMgr
    EC2 -->|Cloud-Init Bootstrap| S3Bucket
```

---

```text
███████╗███████╗ █████╗ ████████╗██╗   ██╗██████╗ ███████╗███████╗
██╔════╝██╔════╝██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██╔════╝██╔════╝
█████╗  █████╗  ███████║   ██║   ██║   ██║██████╔╝█████╗  ███████╗
██╔══╝  ██╔══╝  ██╔══██║   ██║   ██║   ██║██╔══██╗██╔══╝  ╚════██║
██║     ███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║███████╗███████║
╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝
```

## 3. Project Features & The 8 Core Deliverables

The web dashboard is specifically structured to reflect the **8 Primary Deliverables** outlined in the academic course presentation:

1. **Deliverable 1: Project Overview (`#overview`)**:
   - Executive summary of the VPC architecture.
   - Live system health telemetry, network parameters, and uptime tracker.
2. **Deliverable 2: VPC Architecture (`#architecture`)**:
   - Interactive network topology diagram illustrating the flow between Internet, IGW, Public Subnet, and Private Subnet.
3. **Deliverable 3: VPC and Subnet Details (`#subnets`)**:
   - Tabular CIDR inventory displaying network blocks (`10.0.0.0/16`, `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`), available IP counts, and Availability Zone mappings.
4. **Deliverable 4: Routing and Gateway Details (`#routing`)**:
   - Inspection of the Public Route Table (`0.0.0.0/0 -> IGW`) and Private Route Table (`0.0.0.0/0 -> NAT GW` or local-only).
5. **Deliverable 5: EC2 Server Details (`#ec2`)**:
   - Ubuntu 22.04 LTS instance specifications, public/private IP addresses, Apache reverse-proxy status, and Gunicorn service state.
6. **Deliverable 6: RDS Database Details (`#rds`)**:
   - Amazon RDS MySQL 8.0 engine metadata, private connection endpoints, KMS AES-256 storage encryption confirmation, and explicit verification that public accessibility is disabled.
7. **Deliverable 7: Security Configuration (`#security`)**:
   - Visual display of the Web Security Group (80/443 open, SSH restricted) and Database Security Group (MySQL 3306 chained strictly to `sg-web`), along with IAM instance role policies.
8. **Deliverable 8: Connectivity Test Results (`#testing`)**:
   - Interactive test execution suite running the 7 core PPT validations live with Pass / Fail badges.
9. **Auxiliary Feature: Live Database Persistence Proof (`#visitors`)**:
   - Real-time visitor registration form allowing evaluators to insert, query, update, and delete database records, verifying end-to-end EC2-to-RDS persistence.

---

```text
 ██████╗ ██╗   ██╗██╗ ██████╗██╗  ██╗    ███████╗████████╗ █████╗ ██████╗ ████████╗
██╔═══██╗██║   ██║██║██╔════╝██║ ██╔╝    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝
██║   ██║██║   ██║██║██║     █████╔╝     ███████╗   ██║   ███████║██████╔╝   ██║
██║▄▄ ██║██║   ██║██║██║     ██╔═██╗     ╚════██║   ██║   ██╔══██║██╔══██╗   ██║
╚██████╔╝╚██████╔╝██║╚██████╗██║  ██╗    ███████║   ██║   ██║  ██║██║  ██║   ██║
 ╚══▀▀═╝  ╚═════╝ ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
```

## 4. Master Step-by-Step Implementation Plan (From Scratch)

### Phase 0: Prerequisites & Initial Setup

Before doing anything, ensure your development computer has the following tools installed:

1. **Python 3.10 or higher**:
   - Check by opening PowerShell and running: `python --version`
   - If not installed, download from [python.org](https://www.python.org/downloads/).
2. **Git**:
   - Check: `git --version`
   - Download from [git-scm.com](https://git-scm.com/).
3. **AWS CLI v2**:
   - Check: `aws --version`
   - Download the installer from [aws.amazon.com/cli](https://aws.amazon.com/cli/).
4. **HashiCorp Terraform (v1.5+)**:
   - Check: `terraform -version`
   - Download from [developer.hashicorp.com/terraform/install](https://developer.hashicorp.com/terraform/install).

---

### Phase 1: Local Development & Demonstration (100% Offline, Zero AWS Cost)

#### Step 1: Open PowerShell in the project directory

```powershell
cd "D:\Kottai kannan"
```

#### Step 2: Install Python dependencies

```powershell
python -m pip install -r backend/requirements.txt
```

#### Step 3: Verify local configuration

The `.env` file is already configured for local SQLite mode:

```ini
APP_ENV=development
DATABASE_MODE=sqlite
AWS_ENABLED=false
AWS_REGION=ap-southeast-2
SQLITE_DB_PATH=backend/academicdb.sqlite
```

#### Step 4: Start the application

```powershell
python backend/app.py
```

You will see output confirming:

```text
{"level":"INFO", "message":"Initializing AWS VPC Cloud Management Backend with Boto3 integration."}
{"level":"INFO", "message":"Database schema verification complete: mode=DEVELOPMENT, engine=SQLITE."}
 * Running on http://127.0.0.1:5000
```

#### Step 5: Open the web dashboard

Open your web browser and go to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

```text
████████╗███████╗███████╗████████╗██╗███╗   ██╗ ██████╗
╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝
   ██║   █████╗  ███████╗   ██║   ██║██╔██╗ ██║██║  ███╗
   ██║   ██╔══╝  ╚════██║   ██║   ██║██║╚██╗██║██║   ██║
   ██║   ███████╗███████║   ██║   ██║██║ ╚████║╚██████╔╝
   ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝
```

### Phase 2: Automated Testing & Validation Suites

Open a second terminal window (leaving the backend running in the first) and execute the test suites:

```powershell
# Run the local development verification tests
python -m pytest test_local_dev.py -v

# Run the complete 57-test end-to-end integration and security audit suite
python -m pytest test_stage5_audit.py test_monitoring_security_testing.py test_visitors_crud.py -v
```

**Expected Result**: All **57 tests pass with 100% success rate**!

---

### Phase 3: Deploying to Live AWS Cloud via Terraform

#### Step 1: Configure AWS CLI credentials

```powershell
aws configure
```

Enter:

- **AWS Access Key ID**: `[Your Access Key]`
- **AWS Secret Access Key**: `[Your Secret Access Key]`
- **Default region name**: `ap-southeast-2` _(or your assigned region)_
- **Default output format**: `json`

Test your credentials:

```powershell
aws sts get-caller-identity
```

#### Step 2: Initialize Terraform

```powershell
terraform init
```

#### Step 3: Run the execution plan

```powershell
terraform plan
```

#### Step 4: Apply the infrastructure

```powershell
terraform apply -auto-approve
```

#### Step 5: Access your live cloud web portal

Terraform will display outputs at the end of the apply:

```text
Outputs:
ec2_public_ip  = "54.x.x.x"
web_server_url = "http://54.x.x.x"
rds_endpoint   = "vpc-academic-project-academic-mysql.cxxxx.ap-southeast-2.rds.amazonaws.com"
```

Open the `web_server_url` in your browser!

---

### Phase 4: Academic Viva & Presentation Walkthrough

When presenting this project to your professor, lab evaluator, or examiner:

1. **State the Architecture Goal**: _"We designed an AWS VPC architecture adhering to the principle of least privilege, isolating our database in a private subnet while serving web traffic from a public subnet."_
2. **Present the 8 Deliverables**:
   - Click through items 1 to 8 on the left sidebar navigation.
   - Show Section 2 (`#architecture`): Explain the flow (Internet → IGW → Public Subnet EC2 → Private Subnet RDS).
   - Show Section 3 (`#subnets`): Highlight the three CIDRs (`10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`).
   - Show Section 7 (`#security`): Highlight that MySQL port 3306 is **never open to 0.0.0.0/0**, but chained exclusively to the EC2 security group ID.
3. **Execute Live Connectivity Tests**:
   - Navigate to Section 8 (`#testing`).
   - Click the green **"Run All Connectivity Tests"** button.
   - Watch all 7 core validations turn green (`PASS`).
4. **Demonstrate Database Persistence**:
   - Go to **Database CRUD Proof** (`#visitors`).
   - Register a new visitor with your name and college email.
   - Show that the record appears in the table immediately, proving live EC2-to-RDS data writing.

---

### Phase 5: Safe Teardown & Cost Elimination

```powershell
terraform destroy -auto-approve
```

---

```text
████████╗██████╗  ██████╗ ██╗   ██╗██████╗ ██╗     ███████╗███████╗██╗  ██╗ ██████╗  ██████╗ ████████╗
╚══██╔══╝██╔══██╗██╔═══██╗██║   ██║██╔══██╗██║     ██╔════╝██╔════╝██║  ██║██╔═══██╗██╔═══██╗╚══██╔══╝
   ██║   ██████╔╝██║   ██║██║   ██║██████╔╝██║     █████╗  ███████╗███████║██║   ██║██║   ██║   ██║
   ██║   ██╔══██╗██║   ██║██║   ██║██╔══██╗██║     ██╔══╝  ╚════██║██╔══██║██║   ██║██║   ██║   ██║
   ██║   ██║  ██║╚██████╔╝╚██████╔╝██████╔╝███████╗███████╗███████║██║  ██║╚██████╔╝╚██████╔╝   ██║
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝
```

## 5. Complete Troubleshooting Manual (Real-World Solutions)

### 1. `Error: UnauthorizedOperation ... with an explicit deny in a service control policy`

- **Cause**: Your AWS account is part of an AWS Organization (academic/university lab) with an SCP that restricts resource creation to a specific region (e.g., `ap-southeast-2`).
- **Fix**: Set `aws_region = "ap-southeast-2"` in `terraform.tfvars`, `variables.tf`, and `.env`.

### 2. `Error: expected length of user_data to be in the range (0 - 16384)`

- **Cause**: AWS EC2 enforces a hard 16 KB limit on plaintext `user_data`. Base64-encoding large application files directly into the launch template exceeds this limit.
- **Fix**: Implemented the S3 deployment bucket pattern in [`s3.tf`](file:///d:/Kottai%20kannan/s3.tf). Code is packaged into `app.zip` (95 KB) and uploaded to private S3. Cloud-Init downloads `app.zip` via the EC2 IAM instance profile, shrinking `user_data` to just 3.7 KB.

### 3. `Error: InvalidParameterCombination: The specified instance type is not eligible for Free Tier`

- **Cause**: Older `t2.micro` instances are not Free Tier eligible in newer AWS regions like `ap-southeast-2`.
- **Fix**: Updated `ec2_instance_type = "t3.micro"` in [`terraform.tfvars`](file:///d:/Kottai%20kannan/terraform.tfvars) and [`variables.tf`](file:///d:/Kottai%20kannan/variables.tf).

### 4. `Address already in use: Port 5000`

- **Cause**: A previous Flask process is still running in the background.
- **Fix** (PowerShell):
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
  ```
  Then restart: `python backend/app.py`.

### 5. `Error: DBSubnetGroupDoesNotCoverEnoughAZs`

- **Cause**: AWS RDS mandates that any DB Subnet Group must span subnets in at least two Availability Zones.
- **Fix**: We provisioned `private-subnet-1` in `AZ-A` (`10.0.2.0/24`) and `private-subnet-2` in `AZ-B` (`10.0.3.0/24`) in [`subnets.tf`](file:///d:/Kottai%20kannan/subnets.tf). Both are referenced in `aws_db_subnet_group.main` in [`rds.tf`](file:///d:/Kottai%20kannan/rds.tf).

---

## 6. Repository & Codebase Architecture Map

```text
D:\Kottai kannan
├── 📄 main.tf                   # Shared local variables, dynamic AZ discovery, Ubuntu AMI lookup
├── 📄 vpc.tf                    # AWS VPC resource (10.0.0.0/16, DNS support & hostnames)
├── 📄 subnets.tf                # Public subnet (10.0.1.0/24) and two private subnets (10.0.2.0/24, 10.0.3.0/24)
├── 📄 gateways.tf               # Internet Gateway and Elastic IP / NAT Gateway
├── 📄 route_tables.tf           # Public route table (0.0.0.0/0 -> IGW) and private route table
├── 📄 security_groups.tf        # Least-privilege Web Security Group and chained DB Security Group
├── 📄 ec2.tf                    # Ubuntu 22.04 LTS EC2 web server instance configuration
├── 📄 rds.tf                    # Amazon RDS MySQL 8.0 private database instance & DB subnet group
├── 📄 iam.tf                    # IAM role for EC2, SSM Managed Instance Core, Secrets Manager & S3 policies
├── 📄 s3.tf                     # S3 asset bucket for storing and deploying app.zip application archive
├── 📄 variables.tf              # Input variable declarations with validation rules
├── 📄 terraform.tfvars          # Active environment variable values (Region: ap-southeast-2, t3.micro)
├── 📄 outputs.tf                # Infrastructure output values (public IP, website URL, RDS endpoint)
├── 📄 app.zip                   # Clean packaged application bundle for EC2 Cloud-Init bootstrap
│
├── 📁 scripts/
│   └── 📄 user_data.sh.tftpl    # Cloud-init template installing Apache, Python venv, and app services
│
├── 📁 backend/
│   ├── 📄 app.py                # Dual-mode Flask backend (31 REST API routes, SQLite/RDS persistence, Boto3)
│   ├── 📄 requirements.txt      # Python dependencies (Flask, PyMySQL, boto3, pytest, etc.)
│   ├── 📄 wsgi.py               # WSGI entrypoint for production Gunicorn
│   ├── 📄 vpc-app.service       # Systemd service unit managing background Flask service
│   ├── 📄 apache-vpc.conf       # Apache reverse-proxy virtual host configuration
│   └── 📄 academicdb.sqlite     # Persistent local SQLite database file
│
├── 📁 web/
│   ├── 📄 index.html            # Single-page demonstration portal presenting the 8 PPT deliverables
│   ├── 📄 app.js                # Frontend client-side router, API fetchers, and dynamic DOM updaters
│   └── 📄 style.css             # Enterprise dark slate theme with responsive media queries
│
└── 📁 tests/
    ├── 📄 test_stage5_audit.py                  # Static assets, DOM alignment, API endpoints, and connectivity tests
    ├── 📄 test_local_dev.py                     # Local SQLite development mode verification tests
    ├── 📄 test_visitors_crud.py                 # Full CRUD database lifecycle and SQL injection defense tests
    └── 📄 test_monitoring_security_testing.py   # Security group analyzer and CloudWatch telemetry tests
```

```text
 ██████╗ ██╗   ██╗███████╗██████╗ ██╗   ██╗██╗  ██╗ ██████╗ ██╗     ██╗ ██████╗
██╔═══██╗██║   ██║██╔════╝██╔══██╗╚██╗ ██╔╝██║  ██║██╔═══██╗██║     ██║██╔════╝
██║   ██║██║   ██║█████╗  ██████╔╝ ╚████╔╝ ███████║██║   ██║██║     ██║██║
██║▄▄ ██║██║   ██║██╔══╝  ██╔══██╗  ╚██╔╝  ██╔══██║██║   ██║██║     ██║██║
╚██████╔╝╚██████╔╝███████╗██║  ██║   ██║   ██║  ██║╚██████╔╝███████╗██║╚██████╗
 ╚══▀▀═╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝
```
