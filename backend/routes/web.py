"""Web UI routes."""

from flask import Blueprint, render_template

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
def home() -> str:
    """Render the public homepage."""
    return render_template("index.html", page_title="Beranda")
