"""
Test Suite for Local VPC Simulation (No AWS)
Validates all 5 simulation scenarios, route tables, gateways, subnets, and security groups.
"""

import pytest
from backend.vpc_simulator import VPC_SIMULATOR

def test_01_vpc_and_subnet_configuration():
    assert VPC_SIMULATOR.vpc["cidr_block"] == "10.0.0.0/16"
    assert len(VPC_SIMULATOR.subnets) >= 2
    assert VPC_SIMULATOR.subnets[0]["cidr_block"] == "10.0.1.0/24"
    assert VPC_SIMULATOR.subnets[1]["cidr_block"] == "10.0.2.0/24"

def test_02_gateways_configuration():
    assert VPC_SIMULATOR.gateways["internet_gateway"]["state"] == "attached"
    assert VPC_SIMULATOR.gateways["nat_gateway"]["state"] == "available"
    assert VPC_SIMULATOR.gateways["nat_gateway"]["public_ip"] is not None

def test_03_route_tables():
    assert len(VPC_SIMULATOR.route_tables) == 2
    pub_rt = next(rt for rt in VPC_SIMULATOR.route_tables if rt["tier"] == "Public")
    priv_rt = next(rt for rt in VPC_SIMULATOR.route_tables if rt["tier"] == "Private")
    
    # Public RT has 0.0.0.0/0 -> IGW
    igw_route = next(r for r in pub_rt["routes"] if r["destination_cidr"] == "0.0.0.0/0")
    assert igw_route["target"] == "igw-sim-01"
    
    # Private RT has 0.0.0.0/0 -> NAT GW
    nat_route = next(r for r in priv_rt["routes"] if r["destination_cidr"] == "0.0.0.0/0")
    assert nat_route["target"] == "nat-sim-01"

def test_04_traffic_scenario_1_internet_to_public_web_allowed():
    res = VPC_SIMULATOR.simulate_packet("internet", "ec2", "TCP", 80)
    assert res["decision"] == "ALLOWED"
    assert "Web Security Group" in res["reason"]

def test_05_traffic_scenario_2_internet_to_private_rds_denied():
    res = VPC_SIMULATOR.simulate_packet("internet", "rds", "TCP", 3306)
    assert res["decision"] == "DENIED"
    assert "Private RDS has no public IP" in res["reason"]

def test_06_traffic_scenario_3_ec2_to_private_rds_allowed():
    res = VPC_SIMULATOR.simulate_packet("ec2", "rds", "TCP", 3306)
    assert res["decision"] == "ALLOWED"
    assert "Database Security Group" in res["reason"]

def test_07_traffic_scenario_4_private_to_internet_via_nat_allowed():
    res = VPC_SIMULATOR.simulate_packet("rds", "internet", "TCP", 443)
    assert res["decision"] == "ALLOWED"
    assert "NAT Gateway" in res["reason"]

def test_08_traffic_scenario_5_unauthorized_port_denied():
    res = VPC_SIMULATOR.simulate_packet("internet", "ec2", "TCP", 23)
    assert res["decision"] == "DENIED"
    assert "rejected incoming packet" in res["reason"]

def test_09_add_custom_security_rule():
    rule = VPC_SIMULATOR.add_security_rule("sg-sim-web", "TCP", 8080, 8080, "0.0.0.0/0", description="Dev web port")
    assert rule is not None
    res = VPC_SIMULATOR.simulate_packet("internet", "ec2", "TCP", 8080)
    assert res["decision"] == "ALLOWED"

def test_10_api_endpoints_simulation():
    from backend.app import app
    app.config["TESTING"] = True
    with app.test_client() as client:
        # GET /api/security-groups
        r = client.get("/api/security-groups")
        assert r.status_code == 200
        assert "security_groups" in r.get_json()

        # GET /api/resources
        r = client.get("/api/resources")
        assert r.status_code == 200
        assert "resources" in r.get_json()

        # GET /api/traffic/scenarios
        r = client.get("/api/traffic/scenarios")
        assert r.status_code == 200
        assert len(r.get_json()["scenarios"]) == 5

        # POST /api/traffic/simulate (Scenario 1)
        r = client.post("/api/traffic/simulate", json={
            "source": "internet", "destination": "ec2", "protocol": "TCP", "port": 80
        })
        assert r.status_code == 200
        assert r.get_json()["decision"] == "ALLOWED"

        # POST /api/traffic/simulate (Scenario 2)
        r = client.post("/api/traffic/simulate", json={
            "source": "internet", "destination": "rds", "protocol": "TCP", "port": 3306
        })
        assert r.status_code == 200
        assert r.get_json()["decision"] == "DENIED"

        # POST /api/security-groups/rules
        r = client.post("/api/security-groups/rules", json={
            "group_id": "sg-sim-web", "protocol": "TCP", "from_port": 9000, "to_port": 9000
        })
        assert r.status_code == 201
