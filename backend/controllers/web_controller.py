"""Web UI controller."""

from flask import Blueprint, Response, g, make_response, redirect, render_template, url_for

from backend.controllers.authorize import authorize_page, load_authenticated_user

bp = Blueprint("web", __name__)


def _no_store_view(template_name: str, **context: object) -> Response:
    """Render an HTML template with Cache-Control: no-store."""
    response = make_response(render_template(template_name, **context))
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.app_context_processor
def inject_current_user() -> dict[str, object]:
    """Expose current_user to all Jinja2 templates."""
    return {"current_user": load_authenticated_user()}


@bp.route("/", methods=["GET"])
def home() -> str:
    """Render the public homepage."""
    return render_template("index.html", page_title="Beranda")


@bp.route("/login", methods=["GET"])
def login_page() -> Response | str:
    """Render the login page or redirect authenticated users to dashboard."""
    if load_authenticated_user() is not None:
        return redirect(url_for("web.dashboard"))
    return _no_store_view("auth/login.html", page_title="Masuk")


@bp.route("/register", methods=["GET"])
def register_page() -> Response | str:
    """Render the registration page or redirect authenticated users."""
    if load_authenticated_user() is not None:
        return redirect(url_for("web.dashboard"))
    return _no_store_view("auth/register.html", page_title="Daftar")


@bp.route("/dashboard", methods=["GET"])
@authorize_page
def dashboard() -> Response:
    """Render the protected user dashboard."""
    return _no_store_view("dashboard.html", page_title="Dashboard", user=g.current_user)
