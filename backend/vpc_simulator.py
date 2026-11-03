"""
Local VPC with Public and Private Subnets Simulation Engine
Project: VPC WITH PUBLIC AND PRIVATE SUBNETS (Academic Lab)
Author: Academic Cloud Infrastructure Team

Zero Cloud Dependencies. Runs 100% locally on Windows without AWS, Boto3, or cloud credentials.
Faithfully implements the four academic PPT modules:
1. VPC & CIDR Configuration (10.0.0.0/16, 10.0.1.0/24, 10.0.2.0/24)
2. Subnet and Routing (IGW, NAT GW, Public RT, Private RT)
3. Security Controls (Web SG, DB SG Ingress Chaining, Least Privilege)
4. Deployment & Validation (EC2 App Server, SQLite Local RDS, Traffic Simulation)
"""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("vpc-simulator")

class LocalVpcSimulator:
    def __init__(self):
        # 1. VPC Definition (Module 1)
        self.vpc = {
            "vpc_id": "vpc-sim-10-0-0-0",
            "name": "academic-simulation-vpc",
            "cidr_block": "10.0.0.0/16",
            "enable_dns_support": True,
            "enable_dns_hostnames": True,
            "state": "available",
            "region": "local-sim-us-east-1",
            "owner": "Academic Lab (Local Simulation)",
            "mode": "LOCAL_SIMULATION_NO_AWS"
        }

        # 2. Subnet Definitions (Module 1)
        self.subnets = [
            {
                "subnet_id": "subnet-sim-public-01",
                "name": "public-subnet-1",
                "cidr_block": "10.0.1.0/24",
                "tier": "Public",
                "availability_zone": "us-east-1a",
                "map_public_ip_on_launch": True,
                "available_ips": 251,
                "gateway": "igw-sim-01",
                "route_table_id": "rtb-sim-public",
                "description": "Public Web Tier: Hosts EC2 Apache Web Server & NAT Gateway"
            },
            {
                "subnet_id": "subnet-sim-private-01",
                "name": "private-subnet-1",
                "cidr_block": "10.0.2.0/24",
                "tier": "Private-App",
                "availability_zone": "us-east-1a",
                "map_public_ip_on_launch": False,
                "available_ips": 251,
                "gateway": "nat-sim-01",
                "route_table_id": "rtb-sim-private",
                "description": "Private App Tier: Isolated from direct inbound internet traffic"
            },
            {
                "subnet_id": "subnet-sim-private-02",
                "name": "private-subnet-2",
                "cidr_block": "10.0.3.0/24",
                "tier": "Private-DB",
                "availability_zone": "us-east-1b",
                "map_public_ip_on_launch": False,
                "available_ips": 251,
                "gateway": "nat-sim-01",
                "route_table_id": "rtb-sim-private",
                "description": "Private DB Tier: Fulfills AWS RDS Multi-AZ DB Subnet Group standard"
            }
        ]

        # 3. Gateways (Module 2)
        self.gateways = {
            "internet_gateway": {
                "id": "igw-sim-01",
                "name": "vpc-sim-igw",
                "state": "attached",
                "vpc_id": "vpc-sim-10-0-0-0",
                "type": "Internet Gateway",
                "direction": "Bidirectional (Ingress / Egress)",
                "description": "Provides direct public internet connectivity for the public subnet (10.0.1.0/24)."
            },
            "nat_gateway": {
                "id": "nat-sim-01",
                "name": "vpc-sim-nat-gw",
                "state": "available",
                "subnet_id": "subnet-sim-public-01",
                "public_ip": "54.210.88.25",
                "private_ip": "10.0.1.99",
                "type": "NAT Gateway",
                "direction": "Outbound Egress Only (Unsolicited Inbound Blocked)",
                "description": "Enables instances in private subnets to originate outbound internet connections without public IP exposure."
            }
        }

        # 4. Route Tables (Module 2)
        self.route_tables = [
            {
                "route_table_id": "rtb-sim-public",
                "name": "public-route-table",
                "tier": "Public",
                "associated_subnets": ["subnet-sim-public-01 (10.0.1.0/24)"],
                "routes": [
                    {
                        "destination_cidr": "10.0.0.0/16",
                        "target": "local",
                        "status": "active",
                        "type": "implicit_local",
                        "description": "Enables internal communication across all subnets in the VPC."
                    },
                    {
                        "destination_cidr": "0.0.0.0/0",
                        "target": "igw-sim-01",
                        "status": "active",
                        "type": "internet_gateway",
                        "description": "Routes all external internet traffic to the Internet Gateway."
                    }
                ]
            },
            {
                "route_table_id": "rtb-sim-private",
                "name": "private-route-table",
                "tier": "Private",
                "associated_subnets": ["subnet-sim-private-01 (10.0.2.0/24)", "subnet-sim-private-02 (10.0.3.0/24)"],
                "routes": [
                    {
                        "destination_cidr": "10.0.0.0/16",
                        "target": "local",
                        "status": "active",
                        "type": "implicit_local",
                        "description": "Enables internal communication to other VPC resources (e.g., EC2 to RDS)."
                    },
                    {
                        "destination_cidr": "0.0.0.0/0",
                        "target": "nat-sim-01",
                        "status": "active",
                        "type": "nat_gateway",
                        "description": "Routes outbound non-VPC internet requests through NAT Gateway in public subnet."
                    }
                ]
            }
        ]

        # 5. Security Groups (Module 3)
        self.security_groups = [
            {
                "group_id": "sg-sim-web",
                "name": "web-tier-security-group",
                "description": "Controls inbound web traffic and restricted administrative access for EC2 Web Server",
                "vpc_id": "vpc-sim-10-0-0-0",
                "inbound_rules": [
                    {"rule_id": "r-web-in-80", "protocol": "TCP", "from_port": 80, "to_port": 80, "cidr_ip": "0.0.0.0/0", "description": "Allow HTTP web traffic from public internet", "action": "ALLOW"},
                    {"rule_id": "r-web-in-443", "protocol": "TCP", "from_port": 443, "to_port": 443, "cidr_ip": "0.0.0.0/0", "description": "Allow HTTPS secure web traffic from public internet", "action": "ALLOW"},
                    {"rule_id": "r-web-in-22", "protocol": "TCP", "from_port": 22, "to_port": 22, "cidr_ip": "203.0.113.50/32", "description": "Restricted administrative SSH (Locked to authorized admin IP)", "action": "ALLOW"}
                ],
                "outbound_rules": [
                    {"rule_id": "r-web-out-80", "protocol": "TCP", "from_port": 80, "to_port": 80, "cidr_ip": "0.0.0.0/0", "description": "Ubuntu package mirror updates", "action": "ALLOW"},
                    {"rule_id": "r-web-out-443", "protocol": "TCP", "from_port": 443, "to_port": 443, "cidr_ip": "0.0.0.0/0", "description": "AWS SSM Agent and secure APIs", "action": "ALLOW"},
                    {"rule_id": "r-web-out-3306", "protocol": "TCP", "from_port": 3306, "to_port": 3306, "cidr_ip": "10.0.0.0/16", "description": "Internal VPC MySQL Database connection", "action": "ALLOW"}
                ]
            },
            {
                "group_id": "sg-sim-db",
                "name": "database-tier-security-group",
                "description": "Controls database traffic strictly from Web Tier SG (sg-sim-web). Zero public exposure.",
                "vpc_id": "vpc-sim-10-0-0-0",
                "inbound_rules": [
                    {
                        "rule_id": "r-db-in-3306",
                        "protocol": "TCP",
                        "from_port": 3306,
                        "to_port": 3306,
                        "source_group_id": "sg-sim-web",
                        "source_name": "Web Tier Security Group (Chained)",
                        "cidr_ip": None,
                        "description": "Allow MySQL access strictly from EC2 Web Security Group ID",
                        "action": "ALLOW"
                    }
                ],
                "outbound_rules": [
                    {
                        "rule_id": "r-db-out-all",
                        "protocol": "ALL",
                        "from_port": 0,
                        "to_port": 0,
                        "cidr_ip": "10.0.0.0/16",
                        "description": "Internal VPC communication only (No direct internet egress)",
                        "action": "ALLOW"
                    }
                ]
            }
        ]

        # 6. Compute & Database Resources (Module 4)
        self.resources = {
            "ec2_server": {
                "instance_id": "i-sim-web-01",
                "name": "EC2 Web & Application Server",
                "os": "Ubuntu 22.04 LTS (Jammy Jellyfish)",
                "state": "running",
                "public_ip": "54.210.14.92",
                "private_ip": "10.0.1.50",
                "subnet_id": "subnet-sim-public-01",
                "subnet_name": "public-subnet-1 (10.0.1.0/24)",
                "security_group": "sg-sim-web",
                "web_server": "Apache 2.4 (Active / Reverse Proxy)",
                "app_server": "Python Flask (Active / Port 5000)",
                "architecture_tier": "Public Web/Application Tier"
            },
            "rds_database": {
                "db_instance_id": "db-sim-mysql-01",
                "name": "Amazon RDS MySQL Database (Simulated via SQLite)",
                "engine": "SQLite (Local Simulation of MySQL 8.0)",
                "status": "available",
                "private_ip": "10.0.2.20",
                "port": 3306,
                "publicly_accessible": False,
                "public_ip": None,
                "subnet_id": "subnet-sim-private-01",
                "subnet_name": "private-subnet-1 (10.0.2.0/24)",
                "db_subnet_group": "dbsng-sim-private (AZ-A & AZ-B)",
                "security_group": "sg-sim-db",
                "storage_encrypted": True,
                "encryption_type": "KMS AES-256 (Simulated)",
                "architecture_tier": "Isolated Private Database Tier"
            }
        }

    # --------------------------------------------------------------------------
    # Traffic Simulation Engine (Module 4 & Phase 9)
    # --------------------------------------------------------------------------
    def simulate_packet(self, source, destination, protocol="TCP", port=80, direction="inbound"):
        """
        Evaluates a simulated packet traversing the VPC network:
        1. Evaluates Source and Destination IP / Subnet
        2. Evaluates Route Table path (Local, IGW, or NAT GW)
        3. Evaluates Gateway Transit & Ingress/Egress permissions
        4. Evaluates Security Group rules on the target
        5. Returns ALLOWED or DENIED decision with step-by-step trace
        """
        src = str(source).lower().strip()
        dst = str(destination).lower().strip()
        proto = str(protocol).upper().strip()
        try:
            port_num = int(port)
        except (ValueError, TypeError):
            port_num = 80

        trace = []
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Normalize endpoints
        src_info = self._resolve_endpoint(src)
        dst_info = self._resolve_endpoint(dst)

        trace.append({
            "step": 1,
            "name": "Packet Origination",
            "detail": f"Source: {src_info['label']} ({src_info['ip']}) -> Destination: {dst_info['label']} ({dst_info['ip']}) on {proto}:{port_num}."
        })

        # Scenario 1: External Internet -> Private Database
        if src_info["zone"] == "internet" and dst_info["id"] == "rds":
            trace.append({
                "step": 2,
                "name": "Routing & Gateway Evaluation",
                "detail": "Target is in Private Subnet (10.0.2.0/24). Private subnet has no association with Internet Gateway.",
                "status": "BLOCKED"
            })
            trace.append({
                "step": 3,
                "name": "Database Isolation Check",
                "detail": "RDS instance attribute 'PubliclyAccessible' is FALSE. Zero public IPv4 assigned.",
                "status": "BLOCKED"
            })
            return {
                "decision": "DENIED",
                "result_badge": "DENIED (Network Isolated)",
                "scenario": "Internet -> Private RDS Database",
                "source": src_info,
                "destination": dst_info,
                "protocol": proto,
                "port": port_num,
                "trace": trace,
                "reason": "Direct inbound internet traffic to private subnet is rejected by AWS VPC routing. Private RDS has no public IP and no route to the Internet Gateway.",
                "timestamp": now_str
            }

        # Scenario 2: External Internet -> Public Web Server
        if src_info["zone"] == "internet" and dst_info["id"] == "ec2":
            trace.append({
                "step": 2,
                "name": "Internet Gateway Ingress",
                "detail": "Packet arrives through Internet Gateway (igw-sim-01). Destination IP 54.210.14.92 maps to EC2 in Public Subnet (10.0.1.0/24).",
                "status": "PASSED"
            })
            trace.append({
                "step": 3,
                "name": "Public Route Table Evaluation",
                "detail": "Public Route Table (rtb-sim-public) delivers traffic to public subnet interface.",
                "status": "PASSED"
            })

            # Check Web Security Group (sg-sim-web)
            sg_web = self.security_groups[0]
            matched_rule = None
            for r in sg_web["inbound_rules"]:
                if r["protocol"] == proto and r["from_port"] <= port_num <= r["to_port"]:
                    matched_rule = r
                    break

            if matched_rule:
                trace.append({
                    "step": 4,
                    "name": "Security Group Inspection (sg-sim-web)",
                    "detail": f"Matched inbound allow rule: {matched_rule['description']} (Port {port_num}/{proto}).",
                    "status": "PASSED"
                })
                return {
                    "decision": "ALLOWED",
                    "result_badge": "ALLOWED (Traffic Permitted)",
                    "scenario": "Internet -> Public Web Server",
                    "source": src_info,
                    "destination": dst_info,
                    "protocol": proto,
                    "port": port_num,
                    "matched_rule": matched_rule,
                    "trace": trace,
                    "reason": f"Traffic permitted by Web Security Group rule {matched_rule['rule_id']} allowing {proto} on port {port_num}.",
                    "timestamp": now_str
                }
            else:
                trace.append({
                    "step": 4,
                    "name": "Security Group Inspection (sg-sim-web)",
                    "detail": f"No inbound allow rule for port {port_num}/{proto}. State: Default Deny.",
                    "status": "BLOCKED"
                })
                return {
                    "decision": "DENIED",
                    "result_badge": "DENIED (Security Group Blocked)",
                    "scenario": "Internet -> Public Web Server",
                    "source": src_info,
                    "destination": dst_info,
                    "protocol": proto,
                    "port": port_num,
                    "trace": trace,
                    "reason": f"Web Security Group sg-sim-web rejected incoming packet on port {port_num}/{proto}. Only ports 80, 443, and authorized SSH are allowed.",
                    "timestamp": now_str
                }

        # Scenario 3: EC2 Web Server -> Private RDS Database
        if src_info["id"] == "ec2" and dst_info["id"] == "rds":
            trace.append({
                "step": 2,
                "name": "Internal VPC Routing Evaluation",
                "detail": "Source 10.0.1.50 -> Destination 10.0.2.20. Implicit VPC Route (10.0.0.0/16 -> local) routes packet internally without internet exposure.",
                "status": "PASSED"
            })

            # Check DB Security Group (sg-sim-db)
            sg_db = self.security_groups[1]
            if proto == "TCP" and port_num == 3306:
                trace.append({
                    "step": 3,
                    "name": "Security Group Chaining Evaluation (sg-sim-db)",
                    "detail": "Packet originates from EC2 instance possessing 'sg-sim-web'. Matched rule: Inbound MySQL 3306 from Web SG.",
                    "status": "PASSED"
                })
                return {
                    "decision": "ALLOWED",
                    "result_badge": "ALLOWED (Chained Security Group)",
                    "scenario": "EC2 Web Server -> Private RDS Database",
                    "source": src_info,
                    "destination": dst_info,
                    "protocol": proto,
                    "port": port_num,
                    "trace": trace,
                    "reason": "Internal VPC packet permitted by Database Security Group rule r-db-in-3306. Access is granted strictly via security group chaining.",
                    "timestamp": now_str
                }
            else:
                trace.append({
                    "step": 3,
                    "name": "Security Group Inspection (sg-sim-db)",
                    "detail": f"Inbound packet on {proto}:{port_num} rejected. Database Security Group only accepts TCP port 3306 from sg-sim-web.",
                    "status": "BLOCKED"
                })
                return {
                    "decision": "DENIED",
                    "result_badge": "DENIED (Port Not Allowed)",
                    "scenario": "EC2 Web Server -> Private RDS Database",
                    "source": src_info,
                    "destination": dst_info,
                    "protocol": proto,
                    "port": port_num,
                    "trace": trace,
                    "reason": f"Database Security Group sg-sim-db rejected packet on port {port_num}/{proto}. Only MySQL port 3306 is authorized.",
                    "timestamp": now_str
                }

        # Scenario 4: Private Subnet (RDS / Workloads) -> External Internet
        if src_info["zone"] == "private" and dst_info["zone"] == "internet":
            trace.append({
                "step": 2,
                "name": "Private Route Table Evaluation",
                "detail": "Packet destination is 0.0.0.0/0 (Internet). Private Route Table (rtb-sim-private) forwards traffic to NAT Gateway (nat-sim-01).",
                "status": "PASSED"
            })
            trace.append({
                "step": 3,
                "name": "NAT Gateway Translation",
                "detail": "NAT Gateway in Public Subnet translates private IP 10.0.2.20 to Elastic IP 54.210.88.25. Outbound-only state recorded.",
                "status": "PASSED"
            })
            trace.append({
                "step": 4,
                "name": "Internet Gateway Egress",
                "detail": "Packet leaves VPC via Internet Gateway (igw-sim-01) toward external destination.",
                "status": "PASSED"
            })
            return {
                "decision": "ALLOWED",
                "result_badge": "ALLOWED (NAT Gateway Egress)",
                "scenario": "Private Subnet -> External Internet",
                "source": src_info,
                "destination": dst_info,
                "protocol": proto,
                "port": port_num,
                "trace": trace,
                "reason": "Outbound internet connectivity permitted through NAT Gateway (nat-sim-01) with Elastic IP. Unsolicited inbound remains blocked.",
                "timestamp": now_str
            }

        # Scenario 5: Unauthorized / Unknown Traffic
        trace.append({
            "step": 2,
            "name": "Security Rule Evaluation",
            "detail": f"Unauthorized packet path or unrecognized port ({port_num}/{proto}). Default deny applied.",
            "status": "BLOCKED"
        })
        return {
            "decision": "DENIED",
            "result_badge": "DENIED (Unauthorized Route)",
            "scenario": f"{src_info['label']} -> {dst_info['label']}",
            "source": src_info,
            "destination": dst_info,
            "protocol": proto,
            "port": port_num,
            "trace": trace,
            "reason": f"Connection blocked by VPC network access controls. No authorized route or matching security group rule exists for {src_info['label']} to {dst_info['label']} on port {port_num}.",
            "timestamp": now_str
        }

    def _resolve_endpoint(self, key):
        if key in ("internet", "external", "public_user", "attacker"):
            return {"id": "internet", "label": "Public Internet User", "ip": "198.51.100.45", "zone": "internet", "subnet": "External Public Network"}
        elif key in ("ec2", "web", "web_server", "app"):
            return {"id": "ec2", "label": "EC2 Web Server (Ubuntu)", "ip": "10.0.1.50", "public_ip": "54.210.14.92", "zone": "public", "subnet": "10.0.1.0/24 (Public Subnet)"}
        elif key in ("rds", "db", "database", "mysql"):
            return {"id": "rds", "label": "Amazon RDS MySQL (SQLite Sim)", "ip": "10.0.2.20", "public_ip": None, "zone": "private", "subnet": "10.0.2.0/24 (Private Subnet)"}
        elif key in ("nat", "nat_gateway"):
            return {"id": "nat", "label": "NAT Gateway", "ip": "10.0.1.99", "public_ip": "54.210.88.25", "zone": "public", "subnet": "10.0.1.0/24 (Public Subnet)"}
        else:
            return {"id": "custom", "label": f"Custom Endpoint ({key})", "ip": "10.0.99.99", "zone": "unknown", "subnet": "Unassigned"}

    # --------------------------------------------------------------------------
    # Security Rule Management (Phase 7)
    # --------------------------------------------------------------------------
    def add_security_rule(self, group_id, protocol, from_port, to_port, cidr_ip=None, source_group_id=None, description=""):
        for sg in self.security_groups:
            if sg["group_id"] == group_id:
                new_rule = {
                    "rule_id": f"r-custom-{int(datetime.now().timestamp() * 1000) % 100000}",
                    "protocol": protocol.upper(),
                    "from_port": int(from_port),
                    "to_port": int(to_port),
                    "cidr_ip": cidr_ip,
                    "source_group_id": source_group_id,
                    "description": description or f"Custom rule for {protocol} {from_port}-{to_port}",
                    "action": "ALLOW"
                }
                sg["inbound_rules"].append(new_rule)
                return new_rule
        return None

    def get_predefined_scenarios(self):
        return [
            {
                "id": "scenario-1",
                "name": "1. Web User visits Web Server (HTTP Port 80)",
                "source": "internet",
                "destination": "ec2",
                "protocol": "TCP",
                "port": 80,
                "expected": "ALLOWED"
            },
            {
                "id": "scenario-2",
                "name": "2. External Attacker attempts direct connection to Private RDS Database (Port 3306)",
                "source": "internet",
                "destination": "rds",
                "protocol": "TCP",
                "port": 3306,
                "expected": "DENIED"
            },
            {
                "id": "scenario-3",
                "name": "3. EC2 Web Server connects to Private RDS Database (MySQL Port 3306)",
                "source": "ec2",
                "destination": "rds",
                "protocol": "TCP",
                "port": 3306,
                "expected": "ALLOWED"
            },
            {
                "id": "scenario-4",
                "name": "4. Private Subnet Workload downloads security patches via NAT Gateway (Port 443)",
                "source": "rds",
                "destination": "internet",
                "protocol": "TCP",
                "port": 443,
                "expected": "ALLOWED"
            },
            {
                "id": "scenario-5",
                "name": "5. Unauthorized Port Scan on EC2 Web Server (Telnet Port 23)",
                "source": "internet",
                "destination": "ec2",
                "protocol": "TCP",
                "port": 23,
                "expected": "DENIED"
            }
        ]

# Global singleton simulator instance
VPC_SIMULATOR = LocalVpcSimulator()

