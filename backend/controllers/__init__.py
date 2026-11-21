"""Automatic blueprint discovery and registration for controllers."""

import importlib
import pkgutil
from flask import Blueprint, Flask


def register_blueprints(app: Flask) -> None:
    """Auto-discover *_controller modules exporting `bp` and register them."""
    for module_info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        if not module_info.name.endswith("_controller"):
            continue
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        blueprint = getattr(module, "bp", None)
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint)
