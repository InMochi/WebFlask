"""SQLite database connection and initialization helpers."""

from pathlib import Path
import sqlite3
import click
from flask import Flask, current_app, g


def get_db() -> sqlite3.Connection:
    """Return a per-request SQLite connection stored on flask.g."""
    db = g.get("db")
    if db is None:
        db_path = Path(current_app.config["DATABASE"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return db


def close_db(_exception: BaseException | None = None) -> None:
    """Close the per-request SQLite connection if one was opened."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Initialize SQLite tables from schema.sql."""
    db = get_db()
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    db.executescript(schema_path.read_text(encoding="utf-8"))
    db.commit()


@click.command("init-db")
def init_db_command() -> None:
    """CLI command to initialize the SQLite database schema."""
    init_db()
    click.echo("Database SQLite berhasil diinisialisasi.")


def register_db(app: Flask) -> None:
    """Attach database teardown hook, CLI command, and ensure schema exists."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    with app.app_context():
        init_db()
