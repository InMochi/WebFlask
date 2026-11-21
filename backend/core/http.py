"""HTTP request parsing helpers for controllers."""

from typing import Any
from flask import request

from backend.core.exceptions import AppError


def parse_json_object(
    error_message: str = "Invalid request payload",
    status_code: int = 400,
) -> dict[str, Any]:
    """Parse request body as a JSON object or raise AppError."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise AppError(error_message, status_code=status_code)
    return payload
