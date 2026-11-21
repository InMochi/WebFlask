"""SQLite repository for user records."""

from backend.models.user import User, UserCredentials
from backend.repositories.base import execute_write, fetch_one


def create_user(email: str, password_hash: str) -> User:
    """Insert a new user row and return the created User model."""
    user_id = execute_write(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash),
        conflict_message="Email is already registered",
    )
    return User(id=user_id, email=email)


def find_by_email(email: str) -> UserCredentials | None:
    """Fetch a UserCredentials model by normalized email."""
    row = fetch_one(
        "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
        (email,),
    )
    return UserCredentials(**row) if row is not None else None
