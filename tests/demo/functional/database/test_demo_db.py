"""Demo database validation tests — runnable out of the box with SQLite.

These tests use the bundled ``test_data/demo.db`` (created by ``pyplaykit
init``) via the local ``demo_db`` fixture, so they run with zero setup — no
database server required. They demonstrate row-count checks, source/target
migration validation, column mapping, and ignore-fields.

For your real project, replace the ``demo_db`` fixture with the framework's
``db_client`` fixture and configure ``src_db`` in config/environments.yaml.

Run:
    pytest tests/demo/functional/database/
"""
import pytest
from utils.db_validation_helper import DbValidationHelper


@pytest.mark.smoke
@pytest.mark.database
def test_employees_table_row_count(demo_db, logger):
    """Validate that the employees_source table is not empty after a data load."""
    if demo_db is None:
        pytest.skip("Demo database not found — re-run 'pyplaykit init' to create it.")

    count = demo_db.fetch_scalar("SELECT COUNT(*) FROM employees_source")

    assert int(count) > 0, "employees_source is empty — data load may have failed"
    logger.info(f"employees_source contains {count} row(s)")


@pytest.mark.regression
@pytest.mark.database
def test_source_and_target_row_counts_match(demo_db, logger):
    """Validate that source and target tables have the same number of rows.

    Useful after a migration or ETL run to catch missing records.
    """
    if demo_db is None:
        pytest.skip("Demo database not found — re-run 'pyplaykit init' to create it.")

    src_count = int(demo_db.fetch_scalar("SELECT COUNT(*) FROM employees_source"))
    tgt_count = int(demo_db.fetch_scalar("SELECT COUNT(*) FROM employees_target"))

    DbValidationHelper.assert_row_counts_match(
        src_count=src_count,
        tgt_count=tgt_count,
        label="employees_source vs employees_target",
    )
    logger.info(f"Row counts match: {src_count} rows in both tables")


@pytest.mark.regression
@pytest.mark.database
def test_migration_validation_with_column_mapping(demo_db, logger):
    """Compare a legacy-schema table to a new-schema table in the same database.

    Use case: Validate a data migration where table/column names changed but the
    underlying data should be identical. The demo database ships both a legacy
    table (abbreviated columns) and a new table (full column names) that hold the
    same data, so this comparison passes.
    """
    if demo_db is None:
        pytest.skip("Demo database not found — re-run 'pyplaykit init' to create it.")

    # Imported lazily: pulls in pandas, which the row-count tests above don't need.
    try:
        from utils.data_comparison_utils import compare_db_to_db
    except ImportError:
        pytest.skip("Install pandas + openpyxl to run data-comparison demos: pip install pandas openpyxl")

    result = compare_db_to_db(
        db_client_source=demo_db,
        query_source="SELECT emp_id, emp_nm, emp_dept, emp_sal FROM employees_source ORDER BY emp_id",
        db_client_target=demo_db,
        query_target="SELECT employee_id, name, department, salary FROM employees_target ORDER BY employee_id",
        source_column_mapping={
            # Map legacy column names to new column names
            "emp_id": "employee_id",
            "emp_nm": "name",
            "emp_dept": "department",
            "emp_sal": "salary",
        },
        key_columns=["employee_id"],
        float_tolerance=0.01,
        report_path="reports/data_validation/demo_migration_report.html",
    )

    # Always surface where the HTML/CSS report was written — on pass and fail
    # alike — so users can open it in a browser.
    logger.info(f"HTML comparison report generated: {result.report_path}")

    assert result.passed, (
        f"Database migration validation failed: {result.failed_count} mismatches.\n"
        f"Source-only: {result.source_only_count}, Target-only: {result.target_only_count}\n"
        f"Report: {result.report_path}"
    )
    logger.info(f"✓ Migration validation passed: {result.passed_count} rows matched")
