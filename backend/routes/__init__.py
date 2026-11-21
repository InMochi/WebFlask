"""Blueprint registration for backend routes."""

from flask import Flask

from backend.routes.api import api_bp
from backend.routes.web import web_bp


def register_blueprints(app: Flask) -> None:
    """Register web and API blueprints on the Flask app."""
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
