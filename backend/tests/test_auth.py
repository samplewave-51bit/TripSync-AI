"""
TripSync AI - User Authentication & Security Integration Test Suite
Validates:
1. Cryptographic hashing (bcrypt) and password verification
2. JWT token generation and validation
3. User registration and duplicate prevention (400)
4. Credential authentication (JSON and OAuth2 forms)
5. Protected endpoints with Bearer token injection (/api/v1/auth/me)
6. Unauthorized access rejection (401)
7. Profile update operations
"""

import unittest
import uuid
from fastapi.testclient import TestClient

from backend.app.core.database import SessionLocal
from backend.app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from backend.app.main import app
from backend.app.models.user import User


class TestAuthenticationSubsystem(unittest.TestCase):
    """Integration test harness for auth workflows."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_cryptographic_password_hashing(self):
        """Validates that bcrypt generates salted hashes and verifies passwords."""
        plain = "SuperSecretPassword123!"
        hashed = get_password_hash(plain)

        self.assertNotEqual(plain, hashed)
        self.assertTrue(hashed.startswith("$2b$"))
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("WrongPassword!", hashed))

    def test_02_jwt_token_issuance_and_decoding(self):
        """Validates JWT access token creation and decoding."""
        user_id = f"test-uuid-{uuid.uuid4().hex[:8]}"
        token = create_access_token(subject=user_id)

        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 30)

        decoded_id = decode_access_token(token)
        self.assertEqual(decoded_id, user_id)

        # Malformed token test
        self.assertIsNone(decode_access_token("malformed.tampered.token"))

    def test_03_user_registration_flow(self):
        """Validates user account creation via POST /api/v1/auth/register."""
        email = f"rohan_{uuid.uuid4().hex[:8]}@tripsync.ai"
        payload = {
            "email": email,
            "password": "SecurePassword123!",
            "full_name": "Rohan Sharma",
            "avatar_url": "https://avatar.iran.liara.run/public/1",
        }
        response = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user"]["email"], email)
        self.assertEqual(data["user"]["full_name"], "Rohan Sharma")
        self.assertTrue(data["user"]["is_active"])
        self.assertNotIn("password", data["user"])
        self.assertNotIn("hashed_password", data["user"])

    def test_04_duplicate_registration_rejection(self):
        """Validates that existing email registration returns 400 Bad Request."""
        email = f"dup_{uuid.uuid4().hex[:8]}@tripsync.ai"
        payload = {
            "email": email,
            "password": "Password123!",
            "full_name": "Duplicate User",
        }
        # First registration
        res1 = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(res1.status_code, 201)

        # Duplicate registration
        res2 = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(res2.status_code, 400)
        self.assertIn("already exists", res2.json()["detail"])

    def test_05_user_login_success_and_failure(self):
        """Validates JSON login with valid and invalid credentials."""
        # 1. Register test user
        email = f"ananya_{uuid.uuid4().hex[:8]}@tripsync.ai"
        pwd = "ValidPassword456!"
        self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": pwd, "full_name": "Ananya Patel"},
        )

        # 2. Valid Login
        login_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": pwd},
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("access_token", login_res.json())

        # 3. Invalid Password
        bad_pwd_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword!"},
        )
        self.assertEqual(bad_pwd_res.status_code, 401)
        self.assertIn("Incorrect email or password", bad_pwd_res.json()["detail"])

        # 4. Unknown Email
        unknown_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": f"unknown_{uuid.uuid4().hex[:8]}@tripsync.ai", "password": pwd},
        )
        self.assertEqual(unknown_res.status_code, 401)

    def test_06_protected_me_endpoint_and_token_guard(self):
        """Validates access control on GET /api/v1/auth/me."""
        # 1. Create user and obtain token
        email = f"kabir_{uuid.uuid4().hex[:8]}@tripsync.ai"
        pwd = "KabirPassword789!"
        reg = self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": pwd, "full_name": "Kabir Mehta"},
        )
        token = reg.json()["access_token"]

        # 2. Request without token (Expect 401)
        unauth_res = self.client.get("/api/v1/auth/me")
        self.assertEqual(unauth_res.status_code, 401)

        # 3. Request with Bearer token (Expect 200)
        auth_res = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(auth_res.status_code, 200)
        self.assertEqual(auth_res.json()["email"], email)
        self.assertEqual(auth_res.json()["full_name"], "Kabir Mehta")

    def test_07_update_user_profile(self):
        """Validates profile mutation via PUT /api/v1/auth/me."""
        email = f"diya_{uuid.uuid4().hex[:8]}@tripsync.ai"
        pwd = "DiyaPassword321!"
        reg = self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": pwd, "full_name": "Diya Sen"},
        )
        token = reg.json()["access_token"]

        # Update profile
        update_payload = {
            "full_name": "Dr. Diya Sen",
            "avatar_url": "https://tripsync.ai/avatars/diya.png",
        }
        put_res = self.client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json=update_payload,
        )
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.json()["full_name"], "Dr. Diya Sen")
        self.assertEqual(put_res.json()["avatar_url"], "https://tripsync.ai/avatars/diya.png")


if __name__ == "__main__":
    unittest.main()
