"""Smoke and security header tests for the Flask starter app."""

import unittest

from app import create_app


class AppTestCase(unittest.TestCase):
    """Verify application factory, routes, error handlers, and headers."""

    def setUp(self) -> None:
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_factory_config(self) -> None:
        self.assertFalse(create_app().testing)
        self.assertTrue(self.app.testing)

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
        response = self.client.get("/static/css/style.css")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
