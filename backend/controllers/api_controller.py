"""General JSON API controller."""

from flask import Blueprint, Response, current_app, jsonify

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/health", methods=["GET"])
def health_check() -> tuple[Response, int]:
    """Public liveness endpoint for monitoring and smoke checks."""
    # TODO(security): /api/health is an intentionally public, read-only liveness
    # endpoint with no sensitive data. Any future business/data/write endpoints
    # under /api MUST enforce authentication, authorization/ownership checks,
    # strict schema validation, and rate limiting.
    return jsonify(
        {
            "status": "ok",
            "app": current_app.config["APP_NAME"],
        }
    ), 200
