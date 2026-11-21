"""Main application routes."""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def home() -> str:
    """Render the public homepage."""
    return render_template("index.html", page_title="Beranda")
