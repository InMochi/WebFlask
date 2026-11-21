"""SQLite repository for server-side session records."""

from backend.models.user import User
from backend.repositories.base import execute_write, fetch_one


def create_session(session_id: str, user_id: int, expires_at: str) -> None:
    """Persist a new active session identifier for a user."""
    execute_write(
        "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)",
        (session_id, user_id, expires_at),
    )


def find_active_user_by_session_id(session_id: str) -> User | None:
    """Return the User owning an unexpired session, or None if invalid/expired."""
    row = fetch_one(
        """
        SELECT u.id, u.email, u.created_at
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.id = ? AND s.expires_at > datetime('now')
        """,
        (session_id,),
    )
    return User(**row) if row is not None else None


def delete_sessions_by_user_id(user_id: int) -> None:
    """Invalidate all active sessions belonging to the given user."""
    execute_write("DELETE FROM sessions WHERE user_id = ?", (user_id,))
