"""Smoke and security header tests for the Flask starter app."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from backend import create_app
from backend.security import rate_limiter
from config import DevelopmentConfig, ProductionConfig


class AppTestCase(unittest.TestCase):
    """Verify application factory, routes, error handlers, and headers."""

    def setUp(self) -> None:
        rate_limiter.reset()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test.db")
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        rate_limiter.reset()

    def test_factory_config(self) -> None:
        dev_app = create_app(DevelopmentConfig)
        self.assertTrue(dev_app.debug)
        self.assertFalse(dev_app.testing)
        self.assertTrue(self.app.testing)
        env_without_secret = {k: v for k, v in os.environ.items() if k != "SECRET_KEY"}
        with patch.dict(os.environ, env_without_secret, clear=True):
            with self.assertRaises(RuntimeError):
                create_app(ProductionConfig)

    def test_home_page_renders_with_security_headers(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Selamat datang di WebFlask", response.data)
        self.assertIn("Content-Security-Policy", response.headers)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(
            response.headers.get("Permissions-Policy"),
            "camera=(), microphone=(), geolocation=()",
        )

    def test_disallowed_method_rejected(self) -> None:
        response = self.client.post("/")
        self.assertEqual(response.status_code, 405)

    def test_custom_404_page(self) -> None:
        response = self.client.get("/halaman-tidak-ada")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Halaman tidak ditemukan", response.data)

    def test_static_css_served(self) -> None:
        with self.client.get("/static/css/style.css") as response:
            self.assertEqual(response.status_code, 200)

    def test_api_health_returns_json(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertEqual(response.get_json(), {"status": "ok", "app": "WebFlask"})
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_api_404_and_405_return_json(self) -> None:
        not_found = self.client.get("/api/tidak-ada")
        self.assertEqual(not_found.status_code, 404)
        self.assertTrue(not_found.is_json)
        self.assertEqual(not_found.get_json(), {"error": "Resource not found"})

        wrong_method = self.client.post("/api/health")
        self.assertEqual(wrong_method.status_code, 405)
        self.assertTrue(wrong_method.is_json)
        self.assertEqual(wrong_method.get_json(), {"error": "Method not allowed"})


if __name__ == "__main__":
    unittest.main()
