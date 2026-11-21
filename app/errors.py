"""Custom HTTP error handlers."""

from flask import render_template


def page_not_found(_error: Exception) -> tuple[str, int]:
    """Render a generic 404 page without exposing internal details."""
    return render_template("errors/404.html", page_title="Halaman Tidak Ditemukan"), 404


def internal_server_error(_error: Exception) -> tuple[str, int]:
    """Render a generic 500 page without exposing stack traces."""
    return render_template("errors/500.html", page_title="Kesalahan Server"), 500
