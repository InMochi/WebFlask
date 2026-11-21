"""Security utilities: CSRF protection, rate limiting, and auth guards."""

from collections import defaultdict, deque
from functools import wraps
import hmac
import secrets
import threading
import time
from typing import Any, Callable
from flask import Response, current_app, g, jsonify, request, session

from backend.services import auth_service

STATE_CHANGING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding-window rate limiter."""

    # TODO(security): Replace with a shared store (e.g., Redis via Flask-Limiter)
    # when running multiple worker processes or multiple server instances.

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        """Record a request and return (allowed, retry_after_seconds)."""
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = max(1, int(bucket[0] + window_seconds - now) + 1)
                return False, retry_after
            bucket.append(now)
            return True, 0

    def reset(self) -> None:
        """Clear all recorded rate-limit buckets (for tests)."""
        with self._lock:
            self._events.clear()


rate_limiter = SlidingWindowRateLimiter()


def get_or_create_csrf_token() -> str:
    """Return the active CSRF token for this session, generating one if absent."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def enforce_csrf() -> tuple[Response, int] | None:
    """Validate X-CSRF-Token on matched state-changing endpoints."""
    if request.method not in STATE_CHANGING_METHODS:
        return None
    if request.url_rule is None or request.method not in request.url_rule.methods:
        return None

    expected = session.get("csrf_token")
    provided = request.headers.get("X-CSRF-Token", "")
    if not expected or not provided or not hmac.compare_digest(expected, provided):
        return jsonify({"error": "Invalid or missing CSRF token"}), 403
    return None


def enforce_api_rate_limit() -> tuple[Response, int] | None:
    """Apply rate limiting to all /api/* requests."""
    if not (request.path == "/api" or request.path.startswith("/api/")):
        return None
    if not current_app.config.get("RATE_LIMIT_ENABLED", True):
        return None

    client_ip = request.remote_addr or "unknown"
    is_auth_mutation = request.path in {"/api/auth/login", "/api/auth/register"}
    limit = (
        current_app.config["AUTH_RATE_LIMIT"]
        if is_auth_mutation
        else current_app.config["API_RATE_LIMIT"]
    )
    window = current_app.config["RATE_LIMIT_WINDOW_SECONDS"]
    bucket_scope = "auth" if is_auth_mutation else "api"
    allowed, retry_after = rate_limiter.is_allowed(
        f"{bucket_scope}:{client_ip}",
        limit=limit,
        window_seconds=window,
    )
    if not allowed:
        response = jsonify({"error": "Too many requests"})
        response.headers["Retry-After"] = str(retry_after)
        return response, 429
    return None


def load_authenticated_user() -> dict[str, Any] | None:
    """Load the current authenticated user via auth_service."""
    sid = session.get("sid")
    if not sid:
        return None

    user = auth_service.get_authenticated_user(sid)
    if user is None:
        session.pop("sid", None)
        return None
    return user


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Require an active server-side session for protected API endpoints."""

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        user = load_authenticated_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped
