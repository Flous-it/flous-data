"""
flous-data Python package.
Bundles the pre-built SQLite database and exposes SQLAlchemy models.
"""

from importlib.resources import files
from pathlib import Path


def get_db_path() -> Path:
    """Return path to the bundled SQLite database."""
    return Path(str(files("flous_data").joinpath("flous.sqlite")))
