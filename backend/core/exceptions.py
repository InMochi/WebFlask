"""Domain and HTTP-mappable application exceptions."""


class AppError(Exception):
    """Base application error automatically serialized by error handlers."""

    status_code = 500

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class BadRequestError(AppError):
    """Raised when request input fails validation (HTTP 400)."""

    status_code = 400


class UnauthorizedError(AppError):
    """Raised when authentication fails or is missing (HTTP 401)."""

    status_code = 401


class ForbiddenError(AppError):
    """Raised when access or CSRF verification fails (HTTP 403)."""

    status_code = 403


class NotFoundError(AppError):
    """Raised when a requested resource does not exist (HTTP 404)."""

    status_code = 404


class ConflictError(AppError):
    """Raised when a resource conflicts with existing state (HTTP 409)."""

    status_code = 409


class DuplicateRecordError(ConflictError):
    """Raised by repositories on unique constraint violations (HTTP 409)."""


class DatabaseError(AppError):
    """Raised when an unexpected database failure occurs (HTTP 500)."""

    status_code = 500

    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(message, 500)
