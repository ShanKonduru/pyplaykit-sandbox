"""Local fixtures for the demo database tests.

These tests are fully self-contained: they run against a bundled SQLite
database (``test_data/demo.db``) created by ``pyplaykit init``, so they pass
out of the box with no PostgreSQL/MySQL server required.

For your real project, delete this conftest and use the framework's
``db_client`` fixture instead — point ``src_db`` in config/environments.yaml
at your database and the fixture is wired automatically.
"""
from pathlib import Path

import pytest

from utils.db_factory import DbClientFactory


# Resolve the bundled demo database relative to the project root. This file
# lives at tests/demo/functional/database/conftest.py, so the project root is
# four levels up.
_DEMO_DB_PATH = Path(__file__).resolve().parents[4] / "test_data" / "demo.db"


@pytest.fixture(scope="module")
def demo_db(logger):
    """A SQLite client backed by the bundled demo database.

    Yields ``None`` (so tests skip gracefully) if the demo database is missing,
    e.g. when this folder is copied into a project that was scaffolded before
    the demo database was generated. Re-run ``pyplaykit init`` to create it.
    """
    if not _DEMO_DB_PATH.exists():
        yield None
        return

    client = DbClientFactory.create(
        "sqlite", database=str(_DEMO_DB_PATH), logger=logger
    )
    client.connect()
    try:
        yield client
    finally:
        client.close()
