"""SQLite repository for user records."""

from typing import Any

from backend.repositories.base import execute_write, fetch_one


def create_user(email: str, password_hash: str) -> dict[str, Any]:
    """Insert a new user row and return the created user dictionary."""
    user_id = execute_write(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash),
        conflict_message="Email is already registered",
    )
    return {"id": user_id, "email": email}


def find_by_email(email: str) -> dict[str, Any] | None:
    """Fetch a user record (including password_hash) by normalized email."""
    return fetch_one(
        "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
        (email,),
    )
