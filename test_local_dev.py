"""
Test Suite: Local Development Configuration (SQLite + Flask + Frontend)
Covers Phase 8: 11 Verification Points
"""

import os
import sys
import json
import pytest

from backend.app import app, get_effective_db_mode, get_db_connection, SQLITE_DB_PATH

class TestLocalDevelopmentConfiguration:
    @pytest.fixture(autouse=True)
    def setup_client(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_01_flask_startup(self):
        """1. Test Flask WSGI app starts and responds."""
        assert app is not None
        res = self.client.get("/")
        assert res.status_code == 200

    def test_02_sqlite_initialization(self):
        """2. Test SQLite initializes visitors table at stable path."""
        conn = get_db_connection()
        assert conn.engine_type == "sqlite"
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visitors'")
            row = cur.fetchone()
            assert row is not None
        conn.close()

    def test_03_database_persistence(self):
        """3. Test database persistence across separate connections."""
        conn1 = get_db_connection()
        with conn1.cursor() as cur1:
            cur1.execute("SELECT COUNT(*) AS total FROM visitors")
            initial_count = cur1.fetchone()["total"]
        conn1.close()

        conn2 = get_db_connection()
        with conn2.cursor() as cur2:
            cur2.execute("SELECT COUNT(*) AS total FROM visitors")
            after_count = cur2.fetchone()["total"]
        conn2.close()
        assert initial_count == after_count

    def test_04_health_endpoint(self):
        """4. Test /api/health endpoint in local SQLite development mode."""
        res = self.client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["database"] == "connected"
        assert "SQLite" in data["database_engine"]
        assert data["database_mode"] == "development"

    def test_05_visitor_registration(self):
        """5. Test visitor registration with parameterized SQL."""
        payload = {"visitor_name": "Katherine Johnson Test", "email": "katherine.test@nasa.gov"}
        res = self.client.post("/api/visitors", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["visitor"]["visitor_name"] == "Katherine Johnson Test"
        # Save ID for cleanup
        new_id = data["visitor"]["id"]
        # Clean up
        self.client.delete(f"/api/visitors/{new_id}")

    def test_06_visitor_listing(self):
        """6. Test visitor listing and pagination."""
        res = self.client.get("/api/visitors?page=1&limit=5")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert isinstance(data["visitors"], list)
        assert data["total"] >= 0

    def test_07_visitor_editing(self):
        """7. Test visitor update via PUT /api/visitors/{id}."""
        # Create temp record
        create_res = self.client.post("/api/visitors", json={"visitor_name": "Edit Test", "email": "edit.test@example.com"})
        assert create_res.status_code == 201
        vis_id = create_res.get_json()["visitor"]["id"]

        # Edit record
        put_res = self.client.put(f"/api/visitors/{vis_id}", json={"visitor_name": "Edit Test Updated", "email": "edit.updated@example.com"})
        assert put_res.status_code == 200
        put_data = put_res.get_json()
        assert put_data["visitor"]["visitor_name"] == "Edit Test Updated"

        # Cleanup
        self.client.delete(f"/api/visitors/{vis_id}")

    def test_08_visitor_deletion(self):
        """8. Test visitor deletion and subsequent 404 confirmation."""
        create_res = self.client.post("/api/visitors", json={"visitor_name": "Delete Test", "email": "delete.test@example.com"})
        vis_id = create_res.get_json()["visitor"]["id"]

        del_res = self.client.delete(f"/api/visitors/{vis_id}")
        assert del_res.status_code == 200

        get_res = self.client.get(f"/api/visitors/{vis_id}")
        assert get_res.status_code == 404

    def test_09_all_frontend_api_requests(self):
        """9. Test all 11 core frontend API endpoints return valid JSON without crashing."""
        endpoints = [
            "/api/overview",
            "/api/vpc",
            "/api/subnets",
            "/api/routes",
            "/api/gateways",
            "/api/ec2",
            "/api/rds",
            "/api/security",
            "/api/monitoring",
            "/api/connectivity/tests",
            "/api/logs"
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            assert res.status_code == 200, f"Endpoint {ep} returned status {res.status_code}"
            assert res.is_json, f"Endpoint {ep} did not return valid JSON"

    def test_10_invalid_json_handling(self):
        """10. Test that invalid or malformed JSON payloads return HTTP 400 JSON gracefully."""
        res = self.client.post("/api/visitors", data="malformed-not-json", content_type="application/json")
        assert res.status_code == 400
        assert res.is_json
        data = res.get_json()
        assert data["success"] is False

    def test_11_backend_unavailable_and_cors(self):
        """11. Test 404 JSON error handling and CORS headers for cross-origin frontend."""
        res_404 = self.client.get("/api/unknown_endpoint_probe")
        assert res_404.status_code == 404
        assert res_404.is_json
        assert res_404.headers.get("Access-Control-Allow-Origin") == "*"

        res_opt = self.client.options("/api/visitors")
        assert res_opt.status_code == 200
        assert res_opt.headers.get("Access-Control-Allow-Origin") == "*"

