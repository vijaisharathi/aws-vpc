#!/usr/bin/env python3
"""
Comprehensive Automated Test Suite for Stage 3: Visitor Management and Database Functionality
Tests:
  1. Input Validation (Name length, regex, RFC email, bad formats)
  2. SQL Injection Resistance (Parameterized query verification)
  3. Visitor Registration (POST /api/visitors)
  4. Visitor Listing & Pagination (GET /api/visitors?page=1&limit=3)
  5. Visitor Search (GET /api/visitors?q=...)
  6. Visitor Time Filtering (GET /api/visitors?time_filter=all|today|7d|30d)
  7. Visitor Sorting (GET /api/visitors?sort_by=...&order=...)
  8. Single Record Fetch (GET /api/visitors/<id>)
  9. Visitor Update (PUT /api/visitors/<id>)
  10. Visitor Deletion (DELETE /api/visitors/<id>)
  11. 404 Error Handling for non-existent IDs
  12. Aggregated Statistics (GET /api/visitors/stats)
  13. CSV Export (GET /api/visitors/export)
  14. Health Check Database Probe (GET /api/health)
"""

import os
import sys
import json
import unittest

# Ensure backend module is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from app import app, init_db_schema, get_db_connection

class TestVisitorManagementCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initializes database schema and provides Flask test client."""
        init_db_schema()
        cls.client = app.test_client()

    def test_01_health_check_db_probe(self):
        """Verifies GET /api/health probes the database and reports connected status."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertIn("database_engine", data)
        self.assertGreaterEqual(data["latency_ms"], 0)
        print(f"  [PASS] Health check OK - Database: {data['database_engine']} (Latency: {data['latency_ms']}ms)")

    def test_02_validation_rejects_empty_payload(self):
        """Verifies POST /api/visitors returns 400 Bad Request on empty or non-JSON."""
        res = self.client.post("/api/visitors", data="Not json", content_type="text/plain")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Request body must be valid JSON", data["error"])
        print("  [PASS] Non-JSON payload rejected with HTTP 400.")

    def test_03_validation_rejects_invalid_inputs(self):
        """Verifies POST /api/visitors enforces name length, characters, and RFC email rules."""
        test_cases = [
            ({"visitor_name": "", "email": "test@domain.com"}, "Visitor name is required"),
            ({"visitor_name": "A", "email": "test@domain.com"}, "Visitor name must be between 2 and 100 characters"),
            ({"visitor_name": "Katherine", "email": "not-an-email"}, "Invalid email address format"),
            ({"visitor_name": "Katherine", "email": ""}, "Email address is required"),
            ({"visitor_name": "Katherine <script>alert(1)</script>", "email": "test@domain.com"}, "Visitor name contains invalid characters"),
        ]

        for payload, expected_err in test_cases:
            res = self.client.post("/api/visitors", json=payload)
            self.assertEqual(res.status_code, 400)
            data = res.get_json()
            self.assertFalse(data["success"])
            all_details = " ".join(data.get("details", []))
            self.assertIn(expected_err, all_details)

        print(f"  [PASS] All {len(test_cases)} validation test cases strictly rejected with HTTP 400.")

    def test_04_create_visitor_success(self):
        """Verifies POST /api/visitors successfully inserts a record and returns 201 Created."""
        payload = {
            "visitor_name": "Dr. Chien-Shiung Wu",
            "email": "wu.cs@columbia.edu"
        }
        res = self.client.post("/api/visitors", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("visitor", data)
        self.assertGreater(data["visitor"]["id"], 0)
        self.assertEqual(data["visitor"]["visitor_name"], "Dr. Chien-Shiung Wu")
        self.assertEqual(data["visitor"]["email"], "wu.cs@columbia.edu")
        self.__class__.created_id = data["visitor"]["id"]
        print(f"  [PASS] Registration successful - ID #{self.created_id} created.")

    def test_05_sql_injection_defense(self):
        """
        Verifies dual-layer defense against SQL injection:
        1. Input validation strictly blocks semicolons and shell metacharacters with HTTP 400.
        2. Parameterized queries safely store names containing single quotes (e.g. O'Connor).
        3. Parameterized search queries safely neutralize boolean tautologies like ' OR '1'='1.
        """
        # 1. Semicolon injection blocked at validation gate
        malicious_semicolon = {
            "visitor_name": "Bobby Tables; DROP TABLE visitors;",
            "email": "bobby.tables@injection-test.org"
        }
        res_semi = self.client.post("/api/visitors", json=malicious_semicolon)
        self.assertEqual(res_semi.status_code, 400)
        self.assertIn("contains invalid characters", " ".join(res_semi.get_json().get("details", [])))

        # 2. Legitimate name with single quote stored safely via parameterized query
        quote_payload = {
            "visitor_name": "Dr. Ronald O'Reilly",
            "email": "ronald.oreilly@cern.ch"
        }
        res_quote = self.client.post("/api/visitors", json=quote_payload)
        self.assertEqual(res_quote.status_code, 201)
        injected_id = res_quote.get_json()["visitor"]["id"]

        fetch_res = self.client.get(f"/api/visitors/{injected_id}")
        self.assertEqual(fetch_res.status_code, 200)
        self.assertEqual(fetch_res.get_json()["visitor"]["visitor_name"], "Dr. Ronald O'Reilly")
        self.client.delete(f"/api/visitors/{injected_id}")

        # 3. Search query injection tautology returns empty / matching only, table unharmed
        search_res = self.client.get("/api/visitors?q=' OR '1'='1")
        self.assertEqual(search_res.status_code, 200)
        search_data = search_res.get_json()
        self.assertTrue(search_data["success"])
        self.assertEqual(search_data["total"], 0) # Tautology treated as literal string, no records leaked

        print("  [PASS] Dual-layer SQL Injection defense verified (Validation gate + Parameterized query).")

    def test_06_get_single_visitor(self):
        """Verifies GET /api/visitors/<id> retrieves the expected record."""
        target_id = self.__class__.created_id
        res = self.client.get(f"/api/visitors/{target_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["visitor"]["id"], target_id)
        self.assertEqual(data["visitor"]["visitor_name"], "Dr. Chien-Shiung Wu")
        print(f"  [PASS] Single record retrieval verified for ID #{target_id}.")

    def test_07_list_visitors_pagination(self):
        """Verifies GET /api/visitors supports pagination parameters (page, limit)."""
        res = self.client.get("/api/visitors?page=1&limit=2")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 2)
        self.assertEqual(len(data["visitors"]), 2)
        self.assertGreaterEqual(data["total"], 2)
        self.assertGreaterEqual(data["pages"], 1)
        self.assertIn("database_engine", data)
        self.assertIn("stats", data)
        print(f"  [PASS] Pagination verified: Showing 2 of {data['total']} records across {data['pages']} pages.")

    def test_08_search_visitors(self):
        """Verifies GET /api/visitors?q=... filters by visitor_name or email."""
        res = self.client.get("/api/visitors?q=Chien-Shiung")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["visitors"][0]["email"], "wu.cs@columbia.edu")
        print("  [PASS] Search by query 'Chien-Shiung' returned exactly 1 matching record.")

    def test_09_time_filtering(self):
        """Verifies GET /api/visitors?time_filter=... operates properly on UTC dates."""
        res_today = self.client.get("/api/visitors?time_filter=today")
        self.assertEqual(res_today.status_code, 200)
        data_today = res_today.get_json()
        self.assertTrue(data_today["success"])
        self.assertGreaterEqual(data_today["total"], 1)

        res_week = self.client.get("/api/visitors?time_filter=7d")
        self.assertEqual(res_week.status_code, 200)
        data_week = res_week.get_json()
        self.assertTrue(data_week["success"])
        self.assertGreaterEqual(data_week["total"], data_today["total"])
        print(f"  [PASS] Time filtering verified - Today: {data_today['total']} records, Past 7 Days: {data_week['total']} records.")

    def test_10_sorting_visitors(self):
        """Verifies GET /api/visitors?sort_by=...&order=... sorts properly."""
        res_asc = self.client.get("/api/visitors?sort_by=visitor_name&order=ASC&limit=100")
        self.assertEqual(res_asc.status_code, 200)
        names_asc = [v["visitor_name"] for v in res_asc.get_json()["visitors"]]

        res_desc = self.client.get("/api/visitors?sort_by=visitor_name&order=DESC&limit=100")
        self.assertEqual(res_desc.status_code, 200)
        names_desc = [v["visitor_name"] for v in res_desc.get_json()["visitors"]]

        self.assertEqual(names_asc, list(reversed(names_desc)))
        print("  [PASS] Sorting verified: ASC and DESC names lists are perfect inverses.")

    def test_11_update_visitor(self):
        """Verifies PUT /api/visitors/<id> updates existing record."""
        target_id = self.__class__.created_id
        update_payload = {
            "visitor_name": "Professor C.S. Wu",
            "email": "cs.wu@columbia.edu"
        }
        res = self.client.put(f"/api/visitors/{target_id}", json=update_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["visitor"]["visitor_name"], "Professor C.S. Wu")
        self.assertEqual(data["visitor"]["email"], "cs.wu@columbia.edu")

        # Confirm change in database
        verify_res = self.client.get(f"/api/visitors/{target_id}")
        self.assertEqual(verify_res.get_json()["visitor"]["visitor_name"], "Professor C.S. Wu")
        print(f"  [PASS] Record #{target_id} updated and verified in database.")

    def test_12_delete_visitor(self):
        """Verifies DELETE /api/visitors/<id> deletes the record from database."""
        target_id = self.__class__.created_id
        res = self.client.delete(f"/api/visitors/{target_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

        # Confirm 404 on subsequent get
        verify_res = self.client.get(f"/api/visitors/{target_id}")
        self.assertEqual(verify_res.status_code, 404)
        print(f"  [PASS] Record #{target_id} deleted and confirmed 404.")

    def test_13_not_found_error_handling(self):
        """Verifies 404 Not Found handling for missing IDs across GET, PUT, and DELETE."""
        missing_id = 999999
        res_get = self.client.get(f"/api/visitors/{missing_id}")
        self.assertEqual(res_get.status_code, 404)

        res_put = self.client.put(f"/api/visitors/{missing_id}", json={"visitor_name": "Ghost", "email": "ghost@haunt.com"})
        self.assertEqual(res_put.status_code, 404)

        res_del = self.client.delete(f"/api/visitors/{missing_id}")
        self.assertEqual(res_del.status_code, 404)
        print("  [PASS] 404 Not Found properly returned for non-existent ID #999999 across GET, PUT, DELETE.")

    def test_14_stats_endpoint(self):
        """Verifies GET /api/visitors/stats returns registration analytics."""
        res = self.client.get("/api/visitors/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        stats = data["stats"]
        self.assertIn("total_visitors", stats)
        self.assertIn("today_visitors", stats)
        self.assertIn("weekly_visitors", stats)
        self.assertIn("monthly_visitors", stats)
        self.assertIn("recent_visitor", stats)
        self.assertIn("recent_time", stats)
        self.assertGreaterEqual(stats["total_visitors"], 5)
        print(f"  [PASS] Stats endpoint OK - Total: {stats['total_visitors']}, Recent: {stats['recent_visitor']}")

    def test_15_export_csv_endpoint(self):
        """Verifies GET /api/visitors/export streams a valid CSV document."""
        res = self.client.get("/api/visitors/export")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.content_type)
        self.assertIn("attachment; filename=aws_vpc_visitors_", res.headers.get("Content-Disposition", ""))
        csv_text = res.get_data(as_text=True)
        lines = csv_text.strip().split("\r\n") if "\r\n" in csv_text else csv_text.strip().split("\n")
        self.assertGreaterEqual(len(lines), 6) # Header + at least 5 pioneer records
        self.assertEqual(lines[0], "ID,Visitor Name,Email Address,Registered At (UTC)")
        print(f"  [PASS] CSV Export OK - Streamed {len(lines)} CSV rows with valid header.")

if __name__ == "__main__":
    print("\n==================================================================")
    print("RUNNING AUTOMATED TEST SUITE: STAGE 3 VISITOR CRUD & DATABASE")
    print("==================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVisitorManagementCRUD)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
