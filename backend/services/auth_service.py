"""Authentication business logic service."""

from datetime import datetime, timedelta, timezone
import re
import secrets
from werkzeug.security import check_password_hash, generate_password_hash

from backend.core.exceptions import BadRequestError, UnauthorizedError
from backend.models.user import User
from backend.repositories import session_repository, user_repository

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


def _validate_email(raw_email: object) -> str | None:
    """Normalize and validate an email address."""
    if not isinstance(raw_email, str):
        return None
    normalized = raw_email.strip().lower()
    if not normalized or len(normalized) > 254:
        return None
    if not EMAIL_PATTERN.match(normalized):
        return None
    return normalized


def _validate_password(raw_password: object) -> str | None:
    """Validate password length without restricting character classes."""
    if not isinstance(raw_password, str):
        return None
    if len(raw_password) < MIN_PASSWORD_LENGTH or len(raw_password) > MAX_PASSWORD_LENGTH:
        return None
    return raw_password


def register_user(raw_email: object, raw_password: object) -> User:
    """Validate registration input, hash password with scrypt, and persist user."""
    # TODO(security): Add leaked-password checking (e.g., HIBP k-anonymity)
    # and email verification before opening public registration in production.
    email = _validate_email(raw_email)
    password = _validate_password(raw_password)
    if email is None or password is None:
        raise BadRequestError(
            f"Valid email and password ({MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters) are required"
        )

    password_hash = generate_password_hash(password, method="scrypt")
    return user_repository.create_user(email=email, password_hash=password_hash)


def authenticate_user(raw_email: object, raw_password: object) -> User:
    """Verify user credentials and return a public User model."""
    # TODO(security): Consider OAuth 2.0 / OIDC and MFA for stronger user auth.
    email = _validate_email(raw_email)
    if email is None or not isinstance(raw_password, str) or not raw_password:
        raise UnauthorizedError("Invalid credentials")

    credentials = user_repository.find_by_email(email)
    if credentials is None or not check_password_hash(credentials.password_hash, raw_password):
        raise UnauthorizedError("Invalid credentials")

    return credentials.to_user()


def create_user_session(user_id: int, lifetime: timedelta) -> str:
    """Generate a cryptographic session ID and persist its expiration."""
    session_id = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + lifetime).strftime("%Y-%m-%d %H:%M:%S")
    session_repository.create_session(
        session_id=session_id,
        user_id=user_id,
        expires_at=expires_at,
    )
    return session_id


def get_authenticated_user(session_id: str) -> User | None:
    """Resolve an active session ID to its User model."""
    return session_repository.find_active_user_by_session_id(session_id)


def revoke_user_sessions(user_id: int) -> None:
    """Invalidate all active sessions for a user on logout."""
    session_repository.delete_sessions_by_user_id(user_id)
