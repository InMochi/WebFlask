"""Application factory and startup wiring (analogous to ASP.NET Core Program.cs)."""

from pathlib import Path
from typing import Any
from flask import Flask

from config import Config, ProductionConfig, get_config, resolve_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def create_app(config_object: type[Config] | dict[str, Any] | None = None) -> Flask:
    """Create, configure, and wire the Flask application instance."""
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
    from backend.core.errors import register_error_handlers
    from backend.core.security import register_security_middleware
    from backend.data.db import register_db

    register_db(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_security_middleware(app)

    return app
