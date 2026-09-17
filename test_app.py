import os
import sys
import io
import datetime
import unittest
from fastapi.testclient import TestClient

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import db
from app import app, DEADLINE

client = TestClient(app)

class TestConfirmationSystem(unittest.TestCase):

    def setUp(self):
        # Reset DB before tests
        db.init_db(force_reseed=True)

    def test_01_candidate_seeding(self):
        candidates = db.get_all_candidates()
        self.assertEqual(len(candidates), 11, "Should have exactly 11 candidates")
        names = [c["name"] for c in candidates]
        self.assertIn("김병희", names)
        self.assertIn("김수철", names)
        self.assertIn("강선우", names)

    def test_02_privacy_department_hidden(self):
        """CRITICAL: Ensure division and department are NOT returned to candidate view"""
        candidates = db.get_all_candidates()
        first_token = candidates[0]["token"]
        
        view_data = db.get_candidate_for_candidate_view(first_token)
        self.assertNotIn("division", view_data, "Division MUST NOT be in candidate view")
        self.assertNotIn("department", view_data, "Department MUST NOT be in candidate view")
        self.assertEqual(view_data["name"], candidates[0]["name"])

    def test_03_dormitory_conditional_logic(self):
        """Verify dormitory eligibility default values and toggle"""
        candidates = db.get_all_candidates()
        
        # Check initial eligible candidates: 박기혁, 전세민, 김수철, 강동진
        eligible_names = [c["name"] for c in candidates if c["dormitory_eligible"]]
        self.assertIn("박기혁", eligible_names)
        self.assertIn("전세민", eligible_names)
        self.assertIn("김수철", eligible_names)
        self.assertIn("강동진", eligible_names)
        self.assertEqual(len(eligible_names), 4)

        # Toggle Kim Byeonghee (id 1) to eligible
        resp = client.post("/api/admin/toggle_dormitory/1", json={"eligible": True})
        self.assertEqual(resp.status_code, 200)
        c1 = db.get_candidate_by_token(candidates[0]["token"])
        self.assertEqual(c1["dormitory_eligible"], 1)

    def test_04_submit_acceptance(self):
        """Test candidate submitting acceptance response"""
        candidates = db.get_all_candidates()
        c = candidates[0]
        token = c["token"]

        payload = {
            "status": "accepted",
            "response_english_name": "KIM, BYEONGHEE",
            "response_uniform_size": "2XL(110)",
            "response_dormitory": ""
        }

        resp = client.post(f"/api/submit/{token}", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])

        updated = db.get_candidate_by_token(token)
        self.assertEqual(updated["status"], "accepted")
        self.assertEqual(updated["response_english_name"], "KIM, BYEONGHEE")
        self.assertEqual(updated["response_uniform_size"], "2XL(110)")
        self.assertIsNotNone(updated["responded_at"])

    def test_05_submit_decline(self):
        """Test candidate submitting decline response"""
        candidates = db.get_all_candidates()
        c = candidates[1] # 권석율
        token = c["token"]

        payload = {
            "status": "declined",
            "decline_reason": "타사 취업",
            "decline_detail": "타 공기업에 최종 합격하여 부득이하게 입사를 포기합니다."
        }

        resp = client.post(f"/api/submit/{token}", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])

        updated = db.get_candidate_by_token(token)
        self.assertEqual(updated["status"], "declined")
        self.assertEqual(updated["decline_reason"], "타사 취업")
        self.assertIn("타 공기업", updated["decline_detail"])

    def test_06_admin_dashboard_kpi_and_excel(self):
        """Test Admin KPI calculation and Excel export"""
        # Accept 1, Decline 1, Pending 9
        candidates = db.get_all_candidates()
        client.post(f"/api/submit/{candidates[0]['token']}", json={"status": "accepted", "response_english_name": "KIM"})
        client.post(f"/api/submit/{candidates[1]['token']}", json={"status": "declined", "decline_reason": "학업 및 진학"})

        resp = client.get("/api/admin/candidates")
        self.assertEqual(resp.status_code, 200)
        summary = resp.json()["summary"]
        self.assertEqual(summary["total"], 11)
        self.assertEqual(summary["responded"], 2)
        self.assertEqual(summary["pending"], 9)
        self.assertEqual(summary["accepted"], 1)
        self.assertEqual(summary["declined"], 1)

        # Test Excel export
        excel_resp = client.get("/api/admin/export_excel")
        self.assertEqual(excel_resp.status_code, 200)
        self.assertIn("application/vnd.openxmlformats", excel_resp.headers["content-type"])

    def test_07_login_api(self):
        """Test login with candidate name and phone digits"""
        resp = client.post("/api/login", json={"name": "김병희", "phone": "8259"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])
        self.assertIsNotNone(resp.json()["token"])

        # Invalid login
        resp_invalid = client.post("/api/login", json={"name": "없는사람", "phone": "0000"})
        self.assertEqual(resp_invalid.status_code, 200)
        self.assertFalse(resp_invalid.json()["success"])

if __name__ == "__main__":
    unittest.main()
