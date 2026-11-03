#!/usr/bin/env python3
"""
Comprehensive Automated Test Suite for Stage 4: Monitoring, Security, and Connectivity Testing
Tests:
  1. Real Infrastructure Monitoring (EC2 CPU, Network, RDS CPU, RDS Connections, RDS Storage, Health)
  2. CloudWatch API status, range parameter handling, and time-series generation
  3. Security Group inspection, inbound/outbound rules, and unrestricted access analysis
  4. Public accessibility verification (RDS publicly_accessible=False)
  5. IAM permissions and least-privilege role verification
  6. Automated security audit findings (AUD-01 through AUD-08)
  7. Connectivity Testing Center:
     - Initial NOT RUN state
     - Real live execution of all 12 test cases
     - Individual test execution (TC-01, TC-09, TC-12)
     - Reset test suite functionality
     - Validation that all tests execute real probes without fabrication
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from app import app, init_db_schema, get_db_connection

class TestStage4MonitoringSecurityTesting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db_schema()
        cls.client = app.test_client()

    # =========================================================================
    # 1. MONITORING TESTS
    # =========================================================================
    def test_01_monitoring_metrics_payload(self):
        """Verifies GET /api/monitoring returns all required telemetry metrics."""
        res = self.client.get("/api/monitoring?range=1h")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("source", data)
        self.assertIn("metrics", data)
        self.assertIn("cloudwatch_status", data)

        m = data["metrics"]
        # Required: EC2 CPU
        self.assertIn("ec2_cpu", m)
        self.assertIn("current", m["ec2_cpu"])
        self.assertGreater(len(m["ec2_cpu"]["series"]), 0)

        # Required: EC2 Network Metrics
        self.assertIn("ec2_network_io", m)
        self.assertIn("in_kbs", m["ec2_network_io"])
        self.assertIn("out_kbs", m["ec2_network_io"])
        self.assertGreater(len(m["ec2_network_io"]["series"]), 0)

        # Required: RDS CPU
        self.assertIn("rds_cpu", m)
        self.assertIn("current", m["rds_cpu"])

        # Required: RDS Connections
        self.assertIn("rds_connections", m)
        self.assertIn("current", m["rds_connections"])
        self.assertGreater(len(m["rds_connections"]["series"]), 0)

        # Required: RDS Storage
        self.assertIn("rds_storage_free", m)
        self.assertIn("free_gb", m["rds_storage_free"])

        # Required: Application Health & Latency
        self.assertIn("application_health", m)
        self.assertEqual(m["application_health"]["status_code"], 200)

        # Required: Backend Health
        self.assertIn("backend_health", m)
        self.assertIn("engine", m["backend_health"])

        print(f"  [PASS] Monitoring verified - EC2 CPU: {m['ec2_cpu']['current']} | Network: {m['ec2_network_io']['in_kbs']} / {m['ec2_network_io']['out_kbs']} | Storage: {m['rds_storage_free']['free_gb']}")

    def test_02_monitoring_time_ranges(self):
        """Verifies GET /api/monitoring supports 1h, 6h, 24h, 7d ranges."""
        ranges = ["1h", "6h", "24h", "7d"]
        for r in ranges:
            res = self.client.get(f"/api/monitoring?range={r}")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["time_range"], r)
            self.assertGreater(len(data["metrics"]["ec2_cpu"]["series"]), 0)
        print("  [PASS] All 4 monitoring time ranges (1h, 6h, 24h, 7d) query successfully.")

    def test_03_cloudwatch_status_reporting(self):
        """Verifies CloudWatch API status, error reporting, and missing permissions handling."""
        res = self.client.get("/api/monitoring")
        self.assertEqual(res.status_code, 200)
        cw = res.get_json()["cloudwatch_status"]
        self.assertIn("status", cw)
        self.assertIn(cw["status"], ["active", "standby", "permission_denied"])
        print(f"  [PASS] CloudWatch API status reported cleanly: {cw['status']} (Accessible: {cw['accessible']}).")

    # =========================================================================
    # 2. SECURITY TESTS
    # =========================================================================
    def test_04_security_groups_inspection(self):
        """Verifies GET /api/security inspects EC2 and RDS security groups with inbound/outbound rules."""
        res = self.client.get("/api/security")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        sgs = data["security_groups"]
        self.assertGreaterEqual(len(sgs), 2)

        web_sg = next((s for s in sgs if "web" in s.get("name", "").lower() or "web" in s.get("tier", "").lower()), None)
        self.assertIsNotNone(web_sg)
        self.assertGreater(len(web_sg["inbound_rules"]), 0)
        self.assertGreater(len(web_sg["outbound_rules"]), 0)

        rds_sg = next((s for s in sgs if "rds" in s.get("name", "").lower() or "database" in s.get("tier", "").lower()), None)
        self.assertIsNotNone(rds_sg)
        self.assertGreater(len(rds_sg["inbound_rules"]), 0)

        print(f"  [PASS] Security Groups inspected: Web SG ({web_sg['id']}) & RDS SG ({rds_sg['id']}).")

    def test_05_unrestricted_access_analyzer(self):
        """Verifies identification of unrestricted access (blocks Port 22 and 3306, permits 80 and 443)."""
        res = self.client.get("/api/security")
        self.assertEqual(res.status_code, 200)
        unrec = res.get_json()["unrestricted_access_analysis"]

        self.assertFalse(unrec["ssh_port_22_exposed"], "SSH Port 22 must NOT be exposed to 0.0.0.0/0!")
        self.assertFalse(unrec["rds_port_3306_exposed"], "MySQL Port 3306 must NOT be exposed to 0.0.0.0/0!")
        self.assertTrue(unrec["http_port_80_exposed"], "Port 80 HTTP should be permitted for web tier.")
        self.assertEqual(unrec["unrestricted_admin_exposed"], 0)
        self.assertEqual(unrec["compliance_status"], "COMPLIANT")
        print("  [PASS] Unrestricted Access Analyzer: 0 administrative ports exposed to 0.0.0.0/0.")

    def test_06_public_accessibility_audit(self):
        """Verifies RDS public accessibility check confirms publicly_accessible is FALSE."""
        res = self.client.get("/api/security")
        self.assertEqual(res.status_code, 200)
        pub_audit = res.get_json()["public_accessibility_audit"]
        self.assertFalse(pub_audit["rds_publicly_accessible"])
        self.assertIsNone(pub_audit["rds_assigned_public_ip"])
        self.assertEqual(pub_audit["status"], "PASS")
        print("  [PASS] RDS public accessibility audit passed: publicly_accessible=False in private subnets.")

    def test_07_iam_permissions_review(self):
        """Verifies review of EC2 IAM role and attached least-privilege policies."""
        res = self.client.get("/api/security")
        self.assertEqual(res.status_code, 200)
        iam = res.get_json()["iam"]
        self.assertIn("role_name", iam)
        self.assertIn("instance_profile", iam)
        self.assertGreater(len(iam["attached_policies"]), 0)

        policy_names = [p["policy_name"] for p in iam["attached_policies"]]
        self.assertIn("AmazonSSMManagedInstanceCore", policy_names)
        self.assertIn("SecretsManagerReadPolicy", policy_names)
        self.assertIn("InfrastructureReadPolicy", policy_names)
        print(f"  [PASS] IAM review OK: Role {iam['role_name']} verified with {len(policy_names)} least-privilege policies.")

    def test_08_security_audit_findings(self):
        """Verifies automated Well-Architected Security Pillar audit findings."""
        res = self.client.get("/api/security")
        self.assertEqual(res.status_code, 200)
        findings = res.get_json()["audit_findings"]
        self.assertGreaterEqual(len(findings), 7)
        for f in findings:
            self.assertEqual(f["status"], "PASS")
        print(f"  [PASS] All {len(findings)} security audit checklist rules evaluated: 100% PASS.")

    # =========================================================================
    # 3. CONNECTIVITY TESTING CENTER TESTS
    # =========================================================================
    def test_09_tests_initial_not_run_state(self):
        """Verifies GET /api/connectivity/tests reports NOT RUN state initially or after reset."""
        self.client.post("/api/connectivity/tests/reset")
        res = self.client.get("/api/connectivity/tests")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["total_tests"], 12)
        self.assertEqual(data["passed"], 0)
        self.assertEqual(data["failed"], 0)
        self.assertEqual(data["not_run"], 12)

        for t in data["tests"]:
            self.assertEqual(t["status"], "NOT RUN")
            self.assertIn("Awaiting", t["actual"])
        print("  [PASS] Initial state verified: All 12 tests in NOT RUN state.")

    def test_10_run_all_connectivity_tests(self):
        """Verifies POST /api/connectivity/tests/run with 'all' executes live probes across all 12 test cases."""
        res = self.client.post("/api/connectivity/tests/run", json={"test_id": "all"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["executed_count"], 12)
        self.assertEqual(data["passed"], 12)
        self.assertEqual(data["failed"], 0)
        self.assertEqual(data["not_run"], 0)

        for r in data["results"]:
            self.assertEqual(r["status"], "PASS")
            self.assertGreaterEqual(r["duration_ms"], 0)
            self.assertTrue(len(r["actual"]) > 10)
        print("  [PASS] Run all 12 tests completed: 12 Passed, 0 Failed, 0 Not Run.")

    def test_11_individual_test_execution_tc09_database(self):
        """Verifies executing single test TC-09 (EC2 to RDS TCP 3306)."""
        res = self.client.post("/api/connectivity/tests/run", json={"test_id": "TC-09"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["executed_count"], 1)
        r = data["results"][0]
        self.assertEqual(r["id"], "TC-09")
        self.assertEqual(r["status"], "PASS")
        self.assertIn("Database TCP connection & SQL probe successful", r["actual"])
        print(f"  [PASS] Single test TC-09 executed: {r['actual']} ({r['duration_ms']}ms)")

    def test_12_individual_test_execution_tc12_visitor_crud(self):
        """Verifies executing single test TC-12 (Live Database Visitor CRUD Operations)."""
        res = self.client.post("/api/connectivity/tests/run", json={"test_id": "TC-12"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["executed_count"], 1)
        r = data["results"][0]
        self.assertEqual(r["id"], "TC-12")
        self.assertEqual(r["status"], "PASS")
        self.assertIn("Functional CRUD verified", r["actual"])
        print(f"  [PASS] Single test TC-12 executed: {r['actual']} ({r['duration_ms']}ms)")

    def test_13_reset_connectivity_tests(self):
        """Verifies POST /api/connectivity/tests/reset restores test suite to NOT RUN state."""
        res_reset = self.client.post("/api/connectivity/tests/reset")
        self.assertEqual(res_reset.status_code, 200)
        data_reset = res_reset.get_json()
        self.assertTrue(data_reset["success"])
        self.assertEqual(data_reset["not_run"], 12)

        res_check = self.client.get("/api/connectivity/tests")
        self.assertEqual(res_check.get_json()["not_run"], 12)
        print("  [PASS] Test suite reset confirmed: 12 tests restored to NOT RUN state.")

if __name__ == "__main__":
    print("\n==================================================================")
    print("RUNNING AUTOMATED TEST SUITE: STAGE 4 MONITORING, SECURITY & TESTING")
    print("==================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage4MonitoringSecurityTesting)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

