"""Environment-based configuration classes for the Flask app."""

import os


class Config:
    """Base configuration shared across all environments."""

    APP_NAME = os.getenv("APP_NAME", "WebFlask")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = False
    TESTING = False


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
