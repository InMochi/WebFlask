"""Authentication HTTP controller (/api/auth/*)."""

import secrets
from flask import Blueprint, Response, current_app, g, jsonify, session

from backend.http import parse_json_object
from backend.security import get_or_create_csrf_token, login_required
from backend.services import auth_service

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _bind_session_cookie(session_id: str) -> None:
    """Store server session ID in a rotated permanent Flask cookie."""
    csrf_token = session.get("csrf_token") or secrets.token_urlsafe(32)
    session.clear()
    session["sid"] = session_id
    session["csrf_token"] = csrf_token
    session.permanent = True


@bp.route("/csrf", methods=["GET"])
def issue_csrf_token() -> tuple[Response, int]:
    """Issue a CSRF token bound to the client's session cookie."""
    return jsonify({"csrf_token": get_or_create_csrf_token()}), 200


@bp.route("/register", methods=["POST"])
def register() -> tuple[Response, int]:
    """Handle user registration requests."""
    payload = parse_json_object()
    user = auth_service.register_user(payload.get("email"), payload.get("password"))
    return jsonify({"user": user}), 201


@bp.route("/login", methods=["POST"])
def login() -> tuple[Response, int]:
    """Handle user login and issue an HttpOnly session cookie."""
    payload = parse_json_object(error_message="Invalid credentials", status_code=401)
    user = auth_service.authenticate_user(payload.get("email"), payload.get("password"))
    session_id = auth_service.create_user_session(
        user_id=user["id"],
        lifetime=current_app.config["PERMANENT_SESSION_LIFETIME"],
    )
    _bind_session_cookie(session_id)
    return jsonify({"user": user}), 200


@bp.route("/logout", methods=["POST"])
@login_required
def logout() -> tuple[Response, int]:
    """Handle user logout and invalidate active sessions."""
    auth_service.revoke_user_sessions(g.current_user["id"])
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@bp.route("/me", methods=["GET"])
@login_required
def current_profile() -> tuple[Response, int]:
    """Return the authenticated user's profile."""
    return jsonify({"user": g.current_user}), 200
