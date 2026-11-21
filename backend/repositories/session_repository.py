"""SQLite repository for server-side session records."""

from typing import Any

from backend.repositories.base import execute_write, fetch_one


def create_session(session_id: str, user_id: int, expires_at: str) -> None:
    """Persist a new active session identifier for a user."""
    execute_write(
        "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)",
        (session_id, user_id, expires_at),
    )


def find_active_user_by_session_id(session_id: str) -> dict[str, Any] | None:
    """Return the user owning an unexpired session, or None if invalid/expired."""
    return fetch_one(
        """
        SELECT u.id, u.email, u.created_at
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.id = ? AND s.expires_at > datetime('now')
        """,
        (session_id,),
    )


def delete_sessions_by_user_id(user_id: int) -> None:
    """Invalidate all active sessions belonging to the given user."""
    execute_write("DELETE FROM sessions WHERE user_id = ?", (user_id,))
