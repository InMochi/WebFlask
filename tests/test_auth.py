"""Authentication, session, CSRF, and rate-limit tests."""

from pathlib import Path
import tempfile
import unittest

from backend import create_app
from backend.core.security import rate_limiter

HTTPS_BASE = "https://127.0.0.1"


class AuthTestCase(unittest.TestCase):
    """Verify SQLite-backed auth endpoints and security controls."""

    def setUp(self) -> None:
        rate_limiter.reset()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "auth_test.db")
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.db_path,
                "AUTH_RATE_LIMIT": 5,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        rate_limiter.reset()

    def _get_csrf(self) -> str:
        res = self.client.get("/api/auth/csrf", base_url=HTTPS_BASE)
        self.assertEqual(res.status_code, 200)
        return res.get_json()["csrf_token"]

    def test_csrf_cookie_flags_and_rejection_without_token(self) -> None:
        csrf_res = self.client.get("/api/auth/csrf", base_url=HTTPS_BASE)
        set_cookie = csrf_res.headers.get("Set-Cookie", "")
        self.assertIn("__Host-session=", set_cookie)
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("Secure", set_cookie)
        self.assertIn("SameSite=Lax", set_cookie)

        res = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "strongpassword123"},
            base_url=HTTPS_BASE,
        )
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json(), {"error": "Invalid or missing CSRF token"})

    def test_register_validation_and_duplicate_conflict(self) -> None:
        csrf = self._get_csrf()
        headers = {"X-CSRF-Token": csrf}

        weak = self.client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "short"},
            headers=headers,
            base_url=HTTPS_BASE,
        )
        self.assertEqual(weak.status_code, 400)

        created = self.client.post(
            "/api/auth/register",
            json={"email": "User@Example.com", "password": "correct horse battery"},
            headers=headers,
            base_url=HTTPS_BASE,
        )
        self.assertEqual(created.status_code, 201)
        user_payload = created.get_json()["user"]
        self.assertEqual(user_payload["email"], "user@example.com")
        self.assertNotIn("password_hash", user_payload)

        duplicate = self.client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "anotherlongpassword"},
            headers=headers,
            base_url=HTTPS_BASE,
        )
        self.assertEqual(duplicate.status_code, 409)

    def test_login_me_and_logout_lifecycle(self) -> None:
        csrf = self._get_csrf()
        headers = {"X-CSRF-Token": csrf}

        self.client.post(
            "/api/auth/register",
            json={"email": "dev@example.com", "password": "my-secure-password!"},
            headers=headers,
            base_url=HTTPS_BASE,
        )

        unauth_me = self.client.get("/api/auth/me", base_url=HTTPS_BASE)
        self.assertEqual(unauth_me.status_code, 401)

        bad_login = self.client.post(
            "/api/auth/login",
            json={"email": "dev@example.com", "password": "wrong-password"},
            headers=headers,
            base_url=HTTPS_BASE,
        )
        self.assertEqual(bad_login.status_code, 401)
        self.assertEqual(bad_login.get_json(), {"error": "Invalid credentials"})

        good_login = self.client.post(
            "/api/auth/login",
            json={"email": "dev@example.com", "password": "my-secure-password!"},
            headers=headers,
            base_url=HTTPS_BASE,
        )
        self.assertEqual(good_login.status_code, 200)
        self.assertEqual(good_login.get_json()["user"]["email"], "dev@example.com")

        me = self.client.get("/api/auth/me", base_url=HTTPS_BASE)
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.get_json()["user"]["email"], "dev@example.com")

        dashboard = self.client.get("/dashboard", base_url=HTTPS_BASE)
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.headers.get("Cache-Control"), "no-store")
        self.assertIn(b"d***@example.com", dashboard.data)
        self.assertNotIn(b"dev@example.com", dashboard.data)

        logout = self.client.post("/api/auth/logout", headers=headers, base_url=HTTPS_BASE)
        self.assertEqual(logout.status_code, 200)

        after_logout = self.client.get("/api/auth/me", base_url=HTTPS_BASE)
        self.assertEqual(after_logout.status_code, 401)

    def test_auth_rate_limiting(self) -> None:
        csrf = self._get_csrf()
        headers = {"X-CSRF-Token": csrf}

        for _ in range(5):
            res = self.client.post(
                "/api/auth/login",
                json={"email": "nobody@example.com", "password": "somepassword123"},
                headers=headers,
                base_url=HTTPS_BASE,
            )
            self.assertEqual(res.status_code, 401)

        blocked = self.client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "somepassword123"},
            headers=headers,
            base_url=HTTPS_BASE,
        )
        self.assertEqual(blocked.status_code, 429)
        self.assertIn("Retry-After", blocked.headers)


if __name__ == "__main__":
    unittest.main()
