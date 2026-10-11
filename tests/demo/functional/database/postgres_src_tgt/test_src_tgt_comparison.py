"""Real-world SRC -> TGT PostgreSQL comparison demo.

Validates two PostgreSQL databases (a "source"/legacy system and a
"target"/migrated system), each holding ``employee`` and ``department`` tables
with thousands of rows. The two schemas use *different column names* and carry
*metadata columns that should be ignored*, and the target has a handful of
deliberate data differences seeded in.

This demonstrates the framework's ``compare_db_to_db`` handling of column-name
mapping, ignore-fields, key-based row matching, float tolerance, and automatic
HTML/CSS report generation.

Prerequisites
-------------
    pip install psycopg2-binary pandas openpyxl
    cd tests/demo/functional/database/postgres_src_tgt
    docker compose up -d          # starts + seeds both databases

Run
---
    pytest tests/demo/functional/database/postgres_src_tgt/test_src_tgt_comparison.py -v -s

Reports are written to ``reports/data_validation/`` and the exact path is
logged for each comparison.

Connection overrides (defaults match docker-compose.yml)
--------------------------------------------------------
    PYPLAYKIT_SRC_DB_HOST / PYPLAYKIT_SRC_DB_PORT
    PYPLAYKIT_TGT_DB_HOST / PYPLAYKIT_TGT_DB_PORT
    PYPLAYKIT_DEMO_DB_USER / PYPLAYKIT_DEMO_DB_PASSWORD
"""
from __future__ import annotations

import os

import pytest

from utils.db_factory import DbClientFactory
from utils.logger import get_logger

logger = get_logger("src_tgt_demo")


# Connection settings (defaults match docker-compose.yml)
_USER = os.environ.get("PYPLAYKIT_DEMO_DB_USER", "demo")
_PASSWORD = os.environ.get("PYPLAYKIT_DEMO_DB_PASSWORD", "demo")

_SRC = {
    "host": os.environ.get("PYPLAYKIT_SRC_DB_HOST", "localhost"),
    "port": int(os.environ.get("PYPLAYKIT_SRC_DB_PORT", "55432")),
    "database": "srcdb",
    "user": _USER,
    "password": _PASSWORD,
}
_TGT = {
    "host": os.environ.get("PYPLAYKIT_TGT_DB_HOST", "localhost"),
    "port": int(os.environ.get("PYPLAYKIT_TGT_DB_PORT", "55433")),
    "database": "tgtdb",
    "user": _USER,
    "password": _PASSWORD,
}


def _connect(cfg: dict):
    """Create + connect a PostgreSQL client, or skip if unreachable."""
    try:
        client = DbClientFactory.create("postgresql", logger=logger, **cfg)
        client.connect()
        return client
    except Exception as exc:  # noqa: BLE001 - skip on any connection issue
        pytest.skip(
            f"Cannot reach PostgreSQL at {cfg['host']}:{cfg['port']}/{cfg['database']} "
            f"({exc}). Start the demo databases with: "
            f"cd tests/demo/functional/database/postgres_src_tgt && docker compose up -d"
        )


@pytest.fixture(scope="module")
def src_db():
    client = _connect(_SRC)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="module")
def tgt_db():
    client = _connect(_TGT)
    try:
        yield client
    finally:
        client.close()


@pytest.mark.smoke
@pytest.mark.database
def test_tables_are_seeded(src_db, tgt_db, logger):
    """Confirm both databases seeded thousands of rows before comparing."""
    for label, db in (("SRC", src_db), ("TGT", tgt_db)):
        emp = int(db.fetch_scalar("SELECT COUNT(*) FROM employee"))
        dept = int(db.fetch_scalar("SELECT COUNT(*) FROM department"))
        logger.info(f"{label}: employee={emp} rows, department={dept} rows")
        assert emp > 1000, f"{label}.employee looks unseeded ({emp} rows)"
        assert dept > 0, f"{label}.department looks unseeded ({dept} rows)"


@pytest.mark.regression
@pytest.mark.database
def test_employee_src_vs_tgt(src_db, tgt_db, logger):
    """Compare SRC.employee (legacy names) against TGT.employee (new names)."""
    from utils.data_comparison_utils import compare_db_to_db

    result = compare_db_to_db(
        db_client_source=src_db,
        query_source=(
            "SELECT emp_id, emp_nm, emp_dept_id, emp_sal, emp_email, created_ts "
            "FROM employee ORDER BY emp_id"
        ),
        db_client_target=tgt_db,
        query_target=(
            "SELECT employee_id, name, department_id, salary, email, created_ts "
            "FROM employee ORDER BY employee_id"
        ),
        source_column_mapping={
            "emp_id": "employee_id",
            "emp_nm": "name",
            "emp_dept_id": "department_id",
            "emp_sal": "salary",
            "emp_email": "email",
        },
        key_columns=["employee_id"],
        ignore_fields={"created_ts"},
        float_tolerance=0.01,
        report_path="reports/data_validation/employee_src_vs_tgt_report.html",
    )

    logger.info(
        f"employee comparison: passed={result.passed_count}, failed={result.failed_count}, "
        f"source_only={result.source_only_count}, target_only={result.target_only_count}"
    )
    logger.info(f"HTML report: {result.report_path}")

    # This demo intentionally seeds differences, so we assert on the *known*
    # discrepancy shape. Swap this for `assert result.passed` when validating a
    # real migration you expect to match.
    assert result.failed_count == 4, (
        f"Expected 4 value-mismatched employees, got {result.failed_count}. "
        f"Report: {result.report_path}"
    )
    assert result.source_only_count == 1, "Expected employee 4999 to be source-only"
    assert result.target_only_count == 1, "Expected employee 5001 to be target-only"


@pytest.mark.regression
@pytest.mark.database
def test_department_src_vs_tgt(src_db, tgt_db, logger):
    """Compare SRC.department against TGT.department (dept 7 location changed)."""
    from utils.data_comparison_utils import compare_db_to_db

    result = compare_db_to_db(
        db_client_source=src_db,
        query_source="SELECT dept_id, dept_nm, dept_loc, row_version FROM department ORDER BY dept_id",
        db_client_target=tgt_db,
        query_target="SELECT department_id, name, location, row_version FROM department ORDER BY department_id",
        source_column_mapping={
            "dept_id": "department_id",
            "dept_nm": "name",
            "dept_loc": "location",
        },
        key_columns=["department_id"],
        ignore_fields={"row_version"},
        report_path="reports/data_validation/department_src_vs_tgt_report.html",
    )

    logger.info(
        f"department comparison: passed={result.passed_count}, failed={result.failed_count}"
    )
    logger.info(f"HTML report: {result.report_path}")

    assert result.failed_count == 1, (
        f"Expected 1 changed department (location), got {result.failed_count}. "
        f"Report: {result.report_path}"
    )
    assert result.source_only_count == 0
    assert result.target_only_count == 0
