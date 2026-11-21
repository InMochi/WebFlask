"""Application factory for the Flask web app."""

from pathlib import Path
from typing import Any
from flask import Flask, Response, request

from config import Config, ProductionConfig, get_config, resolve_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


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
    if request.path == "/api" or request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def create_app(config_object: type[Config] | dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "templates"),
        static_folder=str(FRONTEND_DIR / "static"),
    )

    if isinstance(config_object, dict):
        app.config.from_object(Config)
        app.config.from_mapping(config_object)
        require_env_secret = False
    elif config_object is not None:
        app.config.from_object(config_object)
        require_env_secret = config_object is ProductionConfig
    else:
        resolved = get_config()
        app.config.from_object(resolved)
        require_env_secret = resolved is ProductionConfig

    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = resolve_secret_key(require_env=require_env_secret)

    from backend.controllers import register_blueprints
    from backend.controllers.error_controller import register_error_handlers
    from backend.db import register_db
    from backend.security import enforce_api_rate_limit, enforce_csrf

    register_db(app)
    register_blueprints(app)
    register_error_handlers(app)
    app.before_request(enforce_api_rate_limit)
    app.before_request(enforce_csrf)
    app.after_request(add_security_headers)

    return app
