"""Endpoint authorization decorators (similar to ASP.NET Core [Authorize])."""

from functools import wraps
from typing import Any, Callable
from flask import g, redirect, session, url_for

from backend.core.exceptions import UnauthorizedError
from backend.models.user import User
from backend.services import auth_service


def load_authenticated_user() -> User | None:
    """Load the active User model from the current session cookie."""
    sid = session.get("sid")
    if not sid:
        return None

    user = auth_service.get_authenticated_user(sid)
    if user is None:
        session.pop("sid", None)
        return None
    return user


def authorize(view: Callable[..., Any]) -> Callable[..., Any]:
    """Require an authenticated user session for API endpoints (HTTP 401)."""

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        user = load_authenticated_user()
        if user is None:
            raise UnauthorizedError("Authentication required")
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def authorize_page(view: Callable[..., Any]) -> Callable[..., Any]:
    """Require an authenticated user session for web views (redirect to /login)."""

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        user = load_authenticated_user()
        if user is None:
            return redirect(url_for("web.login_page"))
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped
