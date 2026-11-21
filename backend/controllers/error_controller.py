"""HTTP error and domain exception controller for web views and JSON APIs."""

from flask import Flask, Response, jsonify, render_template, request

from backend.exceptions import AppError


def _is_api_request() -> bool:
    """Return True when the incoming request targets the /api namespace."""
    return request.path == "/api" or request.path.startswith("/api/")


def _error_response(
    status_code: int,
    api_message: str,
    template_name: str | None = None,
    page_title: str = "",
) -> tuple[Response | str, int]:
    """Return JSON for API paths or rendered HTML for web views."""
    if _is_api_request():
        return jsonify({"error": api_message}), status_code
    if template_name is not None:
        return render_template(template_name, page_title=page_title), status_code
    return api_message, status_code


def handle_app_error(error: AppError) -> tuple[Response | str, int]:
    """Serialize domain AppError exceptions into HTTP responses."""
    return _error_response(error.status_code, error.message)


def page_not_found(_error: Exception) -> tuple[Response | str, int]:
    """Handle 404 Not Found without exposing internal details."""
    return _error_response(
        404,
        "Resource not found",
        template_name="errors/404.html",
        page_title="Halaman Tidak Ditemukan",
    )


def method_not_allowed(_error: Exception) -> tuple[Response | str, int]:
    """Handle 405 Method Not Allowed consistently across web and API."""
    return _error_response(405, "Method not allowed")


def internal_server_error(_error: Exception) -> tuple[Response | str, int]:
    """Handle 500 Internal Server Error without exposing stack traces."""
    return _error_response(
        500,
        "Internal server error",
        template_name="errors/500.html",
        page_title="Kesalahan Server",
    )


def register_error_handlers(app: Flask) -> None:
    """Register domain and HTTP error handlers on the Flask app."""
    app.register_error_handler(AppError, handle_app_error)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(500, internal_server_error)
