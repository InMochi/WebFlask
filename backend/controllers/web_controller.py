"""Web UI controller."""

from flask import Blueprint, render_template

bp = Blueprint("web", __name__)


@bp.route("/", methods=["GET"])
def home() -> str:
    """Render the public homepage."""
    return render_template("index.html", page_title="Beranda")
