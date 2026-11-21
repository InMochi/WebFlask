"""Environment-based configuration classes for the Flask app."""

from datetime import timedelta
import logging
import os
from pathlib import Path
import secrets

BASE_DIR = Path(__file__).resolve().parent


def resolve_secret_key(require_env: bool) -> str:
    """Resolve SECRET_KEY from environment, local file, or cryptographic RNG."""
    env_secret = os.getenv("SECRET_KEY")
    if env_secret:
        return env_secret

    if require_env:
        raise RuntimeError("SECRET_KEY environment variable is required in production.")

    local_secret_path = BASE_DIR / "instance" / "secret_key.txt"
    if local_secret_path.exists():
        stored = local_secret_path.read_text(encoding="utf-8").strip()
        if stored:
            return stored

    logging.warning("Generating ephemeral SECRET_KEY. Instance-isolated!")
    return secrets.token_hex(32)


class Config:
    """Base configuration shared across all environments."""

    APP_NAME = os.getenv("APP_NAME", "WebFlask")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DATABASE = str(BASE_DIR / "instance" / "app.db")
    DEBUG = False
    TESTING = False

    # Hardened session cookie defaults
    SESSION_COOKIE_NAME = "__Host-session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_PATH = "/"
    SESSION_COOKIE_DOMAIN = None
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # API rate limiting
    RATE_LIMIT_ENABLED = True
    AUTH_RATE_LIMIT = 10
    API_RATE_LIMIT = 60
    RATE_LIMIT_WINDOW_SECONDS = 60


class DevelopmentConfig(Config):
    """Local development configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Automated testing configuration."""

    TESTING = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


CONFIG_MAP: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str | None = None) -> type[Config]:
    """Resolve a configuration class from FLASK_ENV (defaults to production)."""
    selected = (env_name or os.getenv("FLASK_ENV", "production")).strip().lower()
    return CONFIG_MAP.get(selected, ProductionConfig)
