"""Application factory for the Flask web app."""

from flask import Flask, Response


def add_security_headers(response: Response) -> Response:
    """Attach baseline security headers to every HTTP response."""
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self'; "
        "script-src 'self'; "
        "img-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


def create_app() -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)

    # TODO(security): Add SECRET_KEY (via env/secret manager), session cookie
    # hardening (__Host-, HttpOnly, Secure, SameSite), CSRF protection,
    # authentication, and rate limiting before introducing forms, APIs, or
    # user accounts. Omitted here because only a public GET homepage is served.

    from app.routes import main_bp

    app.register_blueprint(main_bp)
    app.after_request(add_security_headers)

    return app
