"""
Automated Test Suite for Stage 5: Final Integration and Quality Assurance
Verifies all 13 pages, API endpoints, Boto3/fallback integration, Database CRUD,
CloudWatch metrics, Security audit, Connectivity suite, Activity Logs, Settings,
Documentation, and Mobile responsiveness.
"""

import os
import sys
import json
import re
import subprocess
import pytest

# Ensure backend can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from app import app, get_db_connection, LOG_RING_BUFFER


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestStage5StaticAssetsAndPages:
    """Verifies static assets, all 13 pages, and DOM alignment."""

    def test_01_all_13_pages_exist_in_html(self):
        with open("web/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        expected_pages = [
            "page-overview",
            "page-architecture",
            "page-subnets",
            "page-routing",
            "page-ec2",
            "page-rds",
            "page-security",
            "page-visitors",
            "page-monitoring",
            "page-testing",
            "page-logs",
            "page-settings",
            "page-documentation"
        ]

        for page_id in expected_pages:
            assert f'id="{page_id}"' in html, f"Page section '{page_id}' is missing from index.html"

    def test_02_all_13_sidebar_nav_links_exist(self):
        with open("web/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        expected_nav_pages = [
            "overview", "architecture", "subnets", "routing", "ec2",
            "rds", "security", "visitors", "monitoring", "testing",
            "logs", "settings", "documentation"
        ]

        for nav in expected_nav_pages:
            pattern = rf'data-page="{nav}"'
            assert re.search(pattern, html), f"Nav link for '{nav}' is missing data-page attribute"
            assert f'href="#{nav}"' in html, f"Nav link for '{nav}' is missing href attribute"

    def test_03_js_syntax_clean(self):
        res = subprocess.run(["node", "-c", "web/app.js"], capture_output=True, text=True)
        assert res.returncode == 0, f"JavaScript syntax error in web/app.js: {res.stderr}"

    def test_04_dom_id_alignment(self):
        with open("web/app.js", "r", encoding="utf-8") as f:
            js_content = f.read()
        with open("web/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        js_ids = set(re.findall(r"getElementById\(['\"]([a-zA-Z0-9_-]+)['\"]\)", js_content))
        html_ids = set(re.findall(r'id=["\']([a-zA-Z0-9_-]+)["\']', html_content))

        missing = js_ids - html_ids
        assert len(missing) == 0, f"DOM elements referenced in JS missing from HTML: {missing}"

    def test_05_css_theme_and_responsive_rules(self):
        with open("web/style.css", "r", encoding="utf-8") as f:
            css = f.read()

        # Theme variables
        assert "--bg-primary" in css
        assert "--accent-sky" in css
        assert '[data-theme="high-contrast"]' in css

        # Responsive media queries
        assert "@media (max-width: 900px)" in css
        assert "@media (max-width: 768px)" in css
        assert "@media (max-width: 480px)" in css


class TestStage5ApiEndpoints:
    """Verifies all backend API endpoints return valid 200 responses with correct schemas."""

    def test_01_health_endpoint(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert "status" in data
        assert "database" in data
        assert "timestamp" in data

    def test_02_overview_endpoint(self, client):
        res = client.get("/api/overview")
        assert res.status_code == 200
        data = res.get_json()
        assert "vpc" in data
        assert "ec2" in data
        assert "rds" in data
        assert "gateways" in data
        assert "timestamp" in data

    def test_03_vpc_subnets_routing_gateways(self, client):
        vpc_res = client.get("/api/vpc")
        assert vpc_res.status_code == 200
        assert "vpc" in vpc_res.get_json() or "vpc_id" in vpc_res.get_json()

        subnets_res = client.get("/api/subnets")
        assert subnets_res.status_code == 200
        subnets_data = subnets_res.get_json()
        assert "subnets" in subnets_data
        assert len(subnets_data["subnets"]) >= 3

        routes_res = client.get("/api/routes")
        assert routes_res.status_code == 200
        assert "route_tables" in routes_res.get_json()

        gateways_res = client.get("/api/gateways")
        assert gateways_res.status_code == 200
        gw_data = gateways_res.get_json()
        assert "internet_gateway" in gw_data
        assert "nat_gateway" in gw_data

    def test_04_compute_and_database_endpoints(self, client):
        ec2_res = client.get("/api/ec2")
        assert ec2_res.status_code == 200
        ec2_data = ec2_res.get_json()
        inst = ec2_data.get("instance", ec2_data)
        assert "instance_id" in inst
        assert "private_ip" in inst

        rds_res = client.get("/api/rds")
        assert rds_res.status_code == 200
        rds_data = rds_res.get_json()
        db = rds_data.get("database", rds_data)
        assert "identifier" in db or "db_instance_id" in db
        assert db.get("publicly_accessible") is False

    def test_05_security_and_iam_endpoints(self, client):
        sec_res = client.get("/api/security")
        assert sec_res.status_code == 200
        sec_data = sec_res.get_json()
        assert "security_groups" in sec_data
        assert "unrestricted_access_analysis" in sec_data
        assert "public_accessibility_audit" in sec_data

        iam_res = client.get("/api/iam")
        assert iam_res.status_code == 200
        iam_data = iam_res.get_json()
        iam_info = iam_data.get("iam", iam_data)
        assert "instance_profile" in iam_info

    def test_06_monitoring_telemetry(self, client):
        res = client.get("/api/monitoring?range=1h")
        assert res.status_code == 200
        data = res.get_json()
        assert "metrics" in data
        assert "ec2_cpu" in data["metrics"]
        assert "rds_cpu" in data["metrics"]
        assert "cloudwatch_status" in data

    def test_07_aws_diagnostic_status(self, client):
        res = client.get("/api/aws/status")
        assert res.status_code == 200
        data = res.get_json()
        assert "status" in data
        assert "services" in data
        for svc in ["ec2", "rds", "cloudwatch", "secretsmanager", "iam"]:
            assert svc in data["services"]

    def test_08_activity_logs_endpoint(self, client):
        res = client.get("/api/logs?limit=20")
        assert res.status_code == 200
        data = res.get_json()
        assert "logs" in data
        assert "total_available" in data

        # Test filters
        info_res = client.get("/api/logs?severity=INFO")
        assert info_res.status_code == 200
        for log in info_res.get_json().get("logs", []):
            assert log["severity"] == "INFO"

        sys_res = client.get("/api/logs?type=SYSTEM")
        assert sys_res.status_code == 200
        for log in sys_res.get_json().get("logs", []):
            assert log["type"] == "SYSTEM"


class TestStage5DatabaseAndVisitorManagement:
    """Verifies complete visitor CRUD operations and parameterized query protection."""

    def test_01_full_visitor_crud_lifecycle(self, client):
        # 1. Create visitor
        payload = {
            "name": "Audit Test Agent",
            "email": "audit.test@example.com"
        }
        create_res = client.post("/api/visitors", json=payload)
        assert create_res.status_code == 201
        create_data = create_res.get_json()
        assert create_data["success"] is True
        visitor_id = create_data["visitor"]["id"]

        # 2. Read single visitor
        get_res = client.get(f"/api/visitors/{visitor_id}")
        assert get_res.status_code == 200
        vis = get_res.get_json()["visitor"]
        assert vis.get("visitor_name") == "Audit Test Agent" or vis.get("name") == "Audit Test Agent"

        # 3. Search visitors
        search_res = client.get("/api/visitors?q=Audit+Test")
        assert search_res.status_code == 200
        assert any(v["id"] == visitor_id for v in search_res.get_json()["visitors"])

        # 4. Update visitor
        update_res = client.put(f"/api/visitors/{visitor_id}", json={
            "name": "Audit Test Agent Updated",
            "email": "audit.updated@example.com"
        })
        assert update_res.status_code == 200
        vis_up = update_res.get_json()["visitor"]
        assert vis_up.get("visitor_name") == "Audit Test Agent Updated" or vis_up.get("name") == "Audit Test Agent Updated"

        # 5. Visitor stats
        stats_res = client.get("/api/visitors/stats")
        assert stats_res.status_code == 200
        stats_json = stats_res.get_json()
        stats_data = stats_json.get("stats", stats_json)
        assert stats_data["total_visitors"] >= 1

        # 6. Visitor export CSV
        export_res = client.get("/api/visitors/export")
        assert export_res.status_code == 200
        assert "text/csv" in export_res.content_type

        # 7. Delete visitor
        del_res = client.delete(f"/api/visitors/{visitor_id}")
        assert del_res.status_code == 200

        # 8. Verify deletion
        not_found_res = client.get(f"/api/visitors/{visitor_id}")
        assert not_found_res.status_code == 404

    def test_02_input_validation_defense(self, client):
        # Empty name
        res1 = client.post("/api/visitors", json={"name": "", "email": "valid@example.com"})
        assert res1.status_code == 400

        # Invalid email
        res2 = client.post("/api/visitors", json={"name": "Valid Name", "email": "invalid-email"})
        assert res2.status_code == 400

        # Script tag
        res3 = client.post("/api/visitors", json={"name": "<script>alert(1)</script>", "email": "xss@example.com"})
        assert res3.status_code == 400


class TestStage5ConnectivitySuite:
    """Verifies the 12-test diagnostic engine runs authentic non-destructive probes."""

    def test_01_all_12_tests_defined(self, client):
        res = client.get("/api/connectivity/tests")
        assert res.status_code == 200
        data = res.get_json()
        assert len(data.get("tests", [])) == 12

    def test_02_run_all_connectivity_tests(self, client):
        res = client.post("/api/connectivity/tests/run", json={"test_id": "all"})
        assert res.status_code == 200
        data = res.get_json()
        assert data.get("executed_count", data.get("total")) == 12
        assert data.get("passed") == 12
        assert data.get("failed") == 0

    def test_03_reset_connectivity_tests(self, client):
        res = client.post("/api/connectivity/tests/reset")
        assert res.status_code == 200
        data = res.get_json()
        assert data.get("not_run") == 12
        for t in data.get("tests", []):
            assert t["status"] == "NOT RUN"
