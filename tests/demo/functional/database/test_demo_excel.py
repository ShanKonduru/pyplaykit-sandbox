"""Example Excel-to-Excel comparison tests — demonstrates key features.

Prerequisites:
    pip install pandas openpyxl

These tests run out of the box: ``pyplaykit init`` ships the sample workbooks
they read (baseline.xlsx, current.xlsx, legacy_export.xlsx, etc.) into
``test_data/``. Swap in your own files at the same paths to compare real data.
They skip gracefully only if those workbooks are missing (e.g. pandas/openpyxl
were not installed when the project was scaffolded).

Run:
    pytest tests/demo/functional/database/test_demo_excel.py
"""
import pytest
from pathlib import Path
from utils.data_comparison_utils import compare_excel_files


@pytest.mark.smoke
@pytest.mark.data
def test_excel_files_match():
    """Compare a baseline Excel export against a current/generated one.

    Typical use cases:
      - Regression: ensure a new build produces identical report output.
      - Migration: validate ETL output matches expected reference data.
    """
    baseline = Path("test_data/baseline.xlsx")
    current = Path("test_data/current.xlsx")

    # Skip gracefully if sample files are not yet present
    if not baseline.exists() or not current.exists():
        pytest.skip(
            "Place baseline.xlsx and current.xlsx in test_data/ to run this test."
        )

    result = compare_excel_files(
        source_file=baseline,
        target_file=current,
        report_path="reports/data_validation/excel_comparison_report.html",
        sheet_name=0,           # compare the first sheet
        ignore_fields={"timestamp", "run_id"},  # fields that change each run
        float_tolerance=0.01,   # allow 1-cent rounding differences
    )

    assert result.passed, (
        f"Excel comparison failed: {result.failed_count} row(s) had discrepancies, "
        f"{result.source_only_count} source-only, {result.target_only_count} target-only.\n"
        f"Full HTML report: {result.report_path}"
    )


@pytest.mark.regression
@pytest.mark.data
def test_excel_with_column_mapping():
    """Compare Excel files with different column names (e.g., legacy vs new system).

    Use case: System migration where column names changed but data is identical.
    Example: "emp_id" in legacy system → "employee_id" in new system
    """
    legacy = Path("test_data/legacy_export.xlsx")
    new_system = Path("test_data/new_system_export.xlsx")

    if not legacy.exists() or not new_system.exists():
        pytest.skip(
            "Place legacy_export.xlsx and new_system_export.xlsx in test_data/ to run this test."
        )

    result = compare_excel_files(
        source_file=legacy,
        target_file=new_system,
        report_path="reports/data_validation/column_mapping_report.html",
        source_column_mapping={
            # Map legacy column names to new column names
            "emp_id": "employee_id",
            "emp_name": "name",
            "emp_dept": "department",
            "emp_sal": "salary"
        },
        key_columns=["employee_id"],  # Use target column name for matching
        ignore_fields={"created_at", "modified_at"},  # System timestamps
        float_tolerance=0.01
    )

    assert result.passed, (
        f"Migration validation failed: {result.failed_count} mismatches found.\n"
        f"Report: {result.report_path}"
    )


@pytest.mark.regression
@pytest.mark.data
def test_excel_unordered_data():
    """Compare Excel files where rows are in different order.

    Use case: Database exports without ORDER BY, or files sorted differently.
    Solution: Use key_columns for row matching instead of position.
    """
    baseline = Path("test_data/baseline_unordered.xlsx")
    current = Path("test_data/current_unordered.xlsx")

    if not baseline.exists() or not current.exists():
        pytest.skip(
            "Place baseline_unordered.xlsx and current_unordered.xlsx in test_data/"
        )

    result = compare_excel_files(
        source_file=baseline,
        target_file=current,
        report_path="reports/data_validation/unordered_comparison_report.html",
        key_columns=["order_id", "line_number"],  # Composite key for matching
        ignore_fields={"export_timestamp", "batch_id"},
        float_tolerance=0.01
    )

    assert result.passed, (
        f"Unordered data comparison failed: {result.failed_count} mismatches.\n"
        f"Report: {result.report_path}"
    )


@pytest.mark.regression
@pytest.mark.data
def test_excel_ignore_metadata_columns():
    """Compare Excel files while ignoring system-generated metadata.

    Use case: Validate business data while ignoring timestamps, IDs, versions.
    Common ignored fields: timestamp, created_at, updated_at, row_version, etl_batch_id
    """
    baseline = Path("test_data/export_v1.xlsx")
    current = Path("test_data/export_v2.xlsx")

    if not baseline.exists() or not current.exists():
        pytest.skip(
            "Place export_v1.xlsx and export_v2.xlsx in test_data/ to run this test."
        )

    result = compare_excel_files(
        source_file=baseline,
        target_file=current,
        report_path="reports/data_validation/ignore_metadata_report.html",
        ignore_fields={
            # System-generated fields that should not be compared
            "timestamp",
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
            "row_version",
            "etl_batch_id",
            "export_id"
        },
        key_columns=["product_id"],
        float_tolerance=0.01
    )

    assert result.passed, (
        f"Comparison failed after ignoring metadata: {result.failed_count} mismatches.\n"
        f"Report: {result.report_path}"
    )
