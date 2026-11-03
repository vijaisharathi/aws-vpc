# Security Architecture & Network Governance Specification

**Project Title**: VPC with Public and Private Subnets  
**Security Classification**: Academic & Production-Hardened Cloud Infrastructure  
**Governing Standard**: AWS Well-Architected Framework – Security Pillar  

---

## 1. Architectural Security Overview & Principles

This cloud network architecture implements the **Principle of Least Privilege (PoLP)** and **Defense-in-Depth** across every infrastructure tier. Rather than relying on perimeter security alone, internal components are cryptographically and logically isolated from one another.

### Core Security Tenets
1. **Zero Direct Database Exposure**: The database tier possesses zero public IP addresses, has no gateway to the internet, and accepts incoming packets exclusively from authorized web servers.
2. **Keyless & Portless Administration**: Traditional SSH access (TCP 22) is disabled by default. Systems engineering and operations leverage **AWS Systems Manager (SSM) Session Manager**, which establishes TLS-encrypted outbound tunnels without opening any inbound firewall ports.
3. **Least-Privilege Egress**: Outbound communication from instances is restricted strictly to mandatory operational ports (HTTPS 443, HTTP 80, DNS 53, NTP 123, and internal MySQL 3306), neutralizing command-and-control (C2) callback vectors.
4. **Secret Governance**: Database master credentials are never baked into EC2 user-data, images, or configuration files; they are stored inside **AWS Secrets Manager** with fine-grained IAM policy scoping.

---

## 2. Inbound Traffic Rules Matrix

| Tier | Security Group | Port / Protocol | Source CIDR / Security Group ID | Security Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Web Tier** | `web-sg` | TCP 80 (HTTP) | `var.allowed_http_cidr` (`0.0.0.0/0`) | Public web ingress to Apache HTTP server. |
| **Web Tier** | `web-sg` | TCP 443 (HTTPS) | `var.allowed_http_cidr` (`0.0.0.0/0`) | Secure encrypted web client communication. |
| **Web Tier** | `web-sg` | TCP 22 (SSH) | `var.allowed_ssh_cidr` (Default: Disabled) | **Strictly prohibited from `0.0.0.0/0`**. If enabled, Terraform validation rejects open internet exposure. |
| **Database Tier** | `db-sg` | TCP 3306 (MySQL) | `aws_security_group.web.id` | **Exclusively permits traffic from Web SG**. Direct IP-based ingress from internet or untrusted VPC subnets is denied. |

---

## 3. Outbound Traffic Rules Matrix (Least Privilege Egress)

Unlike default security groups that permit unrestricted `0.0.0.0/0` outbound traffic across all ports, the Web Server security group explicitly defines permitted egress protocols:

| Source | Port / Protocol | Destination | Justification & Risk Mitigation |
| :--- | :--- | :--- | :--- |
| **EC2 Web** | TCP 443 (HTTPS) | `0.0.0.0/0` | Enables AWS SSM Session Manager agent communication, AWS API interaction, and secure OS package downloads. |
| **EC2 Web** | TCP 80 (HTTP) | `0.0.0.0/0` | Required for Ubuntu package mirror index refreshes (`apt update`) and Certificate Revocation Lists (CRL). |
| **EC2 Web** | UDP & TCP 53 (DNS) | `0.0.0.0/0` (VPC Resolver) | Required for resolving external package repositories and internal Amazon RDS endpoints. |
| **EC2 Web** | UDP 123 (NTP) | `0.0.0.0/0` | Required for Network Time Protocol synchronization with Amazon Time Sync Service. |
| **EC2 Web** | TCP 3306 (MySQL) | `var.vpc_cidr` (`10.0.0.0/16`) | Restricts database query traffic strictly to the internal VPC boundary. |
| **RDS MySQL** | All Protocols | `var.vpc_cidr` (`10.0.0.0/16`) | Egress is restricted strictly to the internal VPC. Arbitrary outbound internet egress is completely revoked. |

---

## 4. Database Access Policy

1. **Subnet Placement & Routing Isolation**:
   - The Amazon RDS instance is deployed inside an isolated `aws_db_subnet_group` containing `private-subnet-1` (`10.0.2.0/24`) and `private-subnet-2` (`10.0.3.0/24`).
   - Neither private subnet possesses a route to the Internet Gateway (`aws_internet_gateway.main`).
   - The parameter `publicly_accessible` is hard-coded to `false`. Even if a misconfigured routing entry were introduced, AWS DNS will not resolve public IP addresses for the instance.
2. **Dynamic Security Group Referencing**:
   - Ingress on port 3306 uses `security_groups = [aws_security_group.web.id]`.
   - Access is evaluated at the hypervisor Elastic Network Interface (ENI) level based on security group membership, immune to IP spoofing within the VPC.
3. **Data-at-Rest & In-Flight Encryption**:
   - Storage volumes are provisioned with encryption enabled.
   - MySQL 8.0 enforces TLS/SSL encrypted client connections for all SQL sessions originating from the web tier.

---

## 5. IAM Access Policy & Secret Governance

### 5.1 Keyless Instance Management (AWS SSM)
- The EC2 instance assumes `aws_iam_role.ec2_ssm_role` via `aws_iam_instance_profile.ec2_profile`.
- Managed policy attached: `arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore`.
- **Security Impact**: Eliminates the operational and security liability of generating, distributing, rotating, and storing private SSH `.pem` keys. All shell interactions are logged to AWS CloudTrail.

### 5.2 Least-Privilege Secrets Manager Policy
Database credentials are stored in `aws_secretsmanager_secret.db_credentials`. Access is locked down via an inline IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadSpecificDbSecret",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:vpc-academic-project-academic-rds-db-secret*"
    }
  ]
}
```

- **Scoped Resource**: The instance role can only read its own specific database secret; it is denied access to any other secrets stored in the AWS account.

---

## 6. Network Access Control Lists (NACLs) vs. Security Groups

In AWS VPC networking, security groups and Network ACLs form two independent layers of packet inspection:

| Dimension | Security Groups | Network ACLs (NACLs) |
| :--- | :--- | :--- |
| **Operating Boundary** | Operates at the **Instance / ENI level**. | Operates at the **Subnet boundary**. |
| **Statefulness** | **Stateful**: If traffic is allowed inbound, response traffic is automatically allowed outbound regardless of egress rules. | **Stateless**: Inbound and outbound traffic must be explicitly and independently permitted. |
| **Rule Types** | **Allow rules only**; implicit deny of all other traffic. | **Allow AND Deny rules** processed in numerical rule order. |
| **Dynamic Membership** | Can reference other Security Groups as source/target. | Can ONLY evaluate static CIDR IP blocks. |

### When Are Custom NACL Rules Necessary?
While the default VPC NACL permits all traffic across subnet boundaries (delegating fine-grained filtering to stateful Security Groups), custom NACLs are required in the following scenarios:
1. **Explicit IP / CIDR Blacklisting**: When a malicious IP range or compromised subnet must be blocked immediately before packets reach instances, NACL `DENY` rules stop the traffic at the subnet threshold.
2. **Strict Compliance & Regulatory Segmentation**: In environments requiring hard network zoning (e.g., PCI-DSS, HIPAA), custom NACLs ensure that even if an engineer mistakenly opens a security group rule, traffic between public subnets and database subnets is blocked at the subnet boundary.
3. **Mitigation of Ephemeral Port Vulnerabilities**: Restricting outbound response traffic from private subnets strictly to established ephemeral port ranges (`1024-65535`).

---

## 7. Threat Modeling, Security Risks, and Mitigations

| Threat / Attack Vector | Vulnerability Description | Applied Mitigation in this Architecture |
| :--- | :--- | :--- |
| **SSH Brute-Force & Credential Theft** | Port 22 exposed to `0.0.0.0/0` invites continuous automated botnet SSH brute-forcing. | **Mitigated**: `enable_ssh_ingress` defaults to `false`. Terraform validation fails if `allowed_ssh_cidr = "0.0.0.0/0"`. Administrative access is routed through AWS SSM Session Manager. |
| **Database Exfiltration** | RDS database directly reachable from the public internet. | **Mitigated**: RDS deployed in private subnets, `publicly_accessible = false`, ingress restricted strictly to `aws_security_group.web.id`. |
| **C2 Malware Callbacks (Lateral Movement)** | Compromised EC2 instance initiates outbound connections to external command-and-control servers. | **Mitigated**: Unrestricted `0.0.0.0/0` egress is revoked. Outbound traffic is restricted to ports 80, 443, 53, 123, and internal VPC port 3306. |
| **Credential Hardcoding in Source Code** | Database passwords committed to Git or embedded in user-data scripts. | **Mitigated**: Credentials managed via AWS Secrets Manager with sensitive HCL variables and `.gitignore` masking. |
| **Cross-Tenant Network Probing** | Instances in the same VPC probing unauthorized database endpoints. | **Mitigated**: `db-sg` verifies the originating Security Group ID (`web-sg`), dropping traffic from any unauthorized instance in the VPC. |

