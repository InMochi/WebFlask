"""User domain models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class User:
    """Public user entity without credential fields."""

    id: int
    email: str
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize safe user fields for JSON responses."""
        data: dict[str, Any] = {"id": self.id, "email": self.email}
        if self.created_at is not None:
            data["created_at"] = self.created_at
        return data


@dataclass(frozen=True, slots=True)
class UserCredentials:
    """Internal user record including password hash for verification."""

    id: int
    email: str
    password_hash: str
    created_at: str | None = None

    def to_user(self) -> User:
        """Convert to a safe public User model."""
        return User(id=self.id, email=self.email, created_at=self.created_at)
