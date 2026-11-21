"""Shared SQLite query helpers for repositories."""

import logging
import sqlite3
from typing import Any

from backend.db import get_db
from backend.exceptions import DatabaseError, DuplicateRecordError


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    """Execute a SELECT query and return the first row as a dict, or None."""
    db = get_db()
    try:
        row = db.execute(query, params).fetchone()
    except sqlite3.Error as exc:
        logging.exception("Database read failure")
        raise DatabaseError() from exc
    return dict(row) if row is not None else None


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Execute a SELECT query and return all rows as a list of dicts."""
    db = get_db()
    try:
        rows = db.execute(query, params).fetchall()
    except sqlite3.Error as exc:
        logging.exception("Database read failure")
        raise DatabaseError() from exc
    return [dict(row) for row in rows]


def execute_write(
    query: str,
    params: tuple[Any, ...] = (),
    *,
    conflict_message: str = "Duplicate record",
) -> int:
    """Execute an INSERT/UPDATE/DELETE query, commit, and return lastrowid."""
    db = get_db()
    try:
        cursor = db.execute(query, params)
        db.commit()
    except sqlite3.IntegrityError as exc:
        raise DuplicateRecordError(conflict_message) from exc
    except sqlite3.Error as exc:
        logging.exception("Database write failure")
        raise DatabaseError() from exc
    return cursor.lastrowid
