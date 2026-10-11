"""File-to-file comparison demo -- CSV, XLS (legacy), XLSX, and multi-sheet.

Demonstrates the framework's ``compare_csv_files`` / ``compare_excel_files``
across every file format, and documents exactly how multi-sheet workbooks
behave. All test data is generated at runtime under ``test_data/file_comparison/``
so nothing binary is committed and the demo runs with zero manual setup.

Each format is exercised twice:
  * an identical pair  -> comparison PASSES
  * a pair with seeded, visible differences -> comparison reports mismatches

Multi-sheet behaviour (important!)
----------------------------------
``compare_excel_files`` compares ONE sheet per call (default: the first sheet,
``sheet_name=0``). Differences on *other* sheets are NOT seen unless you pass
``sheet_name`` explicitly. To validate a whole workbook, loop over its sheets.
``sheet_name=None`` compares every sheet in one call (multi-sheet result).

Prerequisites
-------------
    pip install pandas openpyxl          # CSV + XLSX
    pip install xlwt xlrd                # only needed for the legacy .xls test

Run
---
    pytest tests/demo/functional/database/file_comparison/test_file_comparison.py -v -s
"""
from __future__ import annotations

from pathlib import Path

import pytest

from utils.logger import get_logger

logger = get_logger("file_comparison_demo")

_DATA_DIR = Path("test_data/file_comparison")


_BASELINE = [
    {"employee_id": 1, "name": "Alice Johnson", "department": "Engineering", "salary": 95000.00},
    {"employee_id": 2, "name": "Bob Smith", "department": "Sales", "salary": 72000.00},
    {"employee_id": 3, "name": "Carla Diaz", "department": "Marketing", "salary": 68000.50},
    {"employee_id": 4, "name": "Devon Lee", "department": "Engineering", "salary": 88000.00},
    {"employee_id": 5, "name": "Erin Park", "department": "HR", "salary": 64000.00},
]

# Same keys, but employee 2 salary changed and employee 4 name changed.
_CHANGED = [
    {"employee_id": 1, "name": "Alice Johnson", "department": "Engineering", "salary": 95000.00},
    {"employee_id": 2, "name": "Bob Smith", "department": "Sales", "salary": 79999.00},
    {"employee_id": 3, "name": "Carla Diaz", "department": "Marketing", "salary": 68000.50},
    {"employee_id": 4, "name": "Devon L. Lee", "department": "Engineering", "salary": 88000.00},
    {"employee_id": 5, "name": "Erin Park", "department": "HR", "salary": 64000.00},
]


@pytest.fixture(scope="module")
def data_dir() -> Path:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    return _DATA_DIR


def _write_csv(path: Path, rows: list[dict]) -> None:
    import pandas as pd
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_xlsx(path: Path, rows: list[dict], sheet: str = "Sheet1") -> None:
    import pandas as pd
    pd.DataFrame(rows).to_excel(path, index=False, sheet_name=sheet)


def _write_xlsx_multi(path: Path, sheets: dict) -> None:
    import pandas as pd
    with pd.ExcelWriter(path) as writer:
        for sheet_name, rows in sheets.items():
            pd.DataFrame(rows).to_excel(writer, sheet_name=sheet_name, index=False)


def _write_xls(path: Path, rows: list[dict]) -> None:
    """Write a legacy .xls file via xlwt (pandas 3.x can't write .xls)."""
    xlwt = pytest.importorskip("xlwt", reason="pip install xlwt to run the legacy .xls demo")
    columns = list(rows[0].keys())
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Sheet1")
    for c, header in enumerate(columns):
        ws.write(0, c, header)
    for r, row in enumerate(rows, start=1):
        for c, header in enumerate(columns):
            ws.write(r, c, row[header])
    wb.save(str(path))


@pytest.mark.data
def test_csv_to_csv_identical(data_dir):
    """Two identical CSV files compare as PASSED."""
    from utils.data_comparison_utils import compare_csv_files
    src = data_dir / "employees_a.csv"
    tgt = data_dir / "employees_b.csv"
    _write_csv(src, _BASELINE)
    _write_csv(tgt, _BASELINE)
    result = compare_csv_files(
        source_file=src, target_file=tgt,
        key_columns=["employee_id"], float_tolerance=0.01,
        report_path=str(data_dir / "csv_identical_report.html"),
    )
    logger.info(f"CSV identical: passed={result.passed_count}, failed={result.failed_count}")
    logger.info(f"HTML report: {result.report_path}")
    assert result.passed, f"Identical CSVs should match. Report: {result.report_path}"


@pytest.mark.data
def test_csv_to_csv_with_differences(data_dir):
    """CSV files with seeded differences report exactly 2 mismatched rows."""
    from utils.data_comparison_utils import compare_csv_files
    src = data_dir / "employees_baseline.csv"
    tgt = data_dir / "employees_changed.csv"
    _write_csv(src, _BASELINE)
    _write_csv(tgt, _CHANGED)
    result = compare_csv_files(
        source_file=src, target_file=tgt,
        key_columns=["employee_id"], float_tolerance=0.01,
        report_path=str(data_dir / "csv_diff_report.html"),
    )
    logger.info(f"CSV diff: failed={result.failed_count} (report: {result.report_path})")
    assert result.failed_count == 2, (
        f"Expected 2 changed rows (emp 2 salary, emp 4 name), got {result.failed_count}. "
        f"Report: {result.report_path}"
    )


@pytest.mark.data
def test_xlsx_to_xlsx_identical(data_dir):
    """Two identical .xlsx files compare as PASSED."""
    from utils.data_comparison_utils import compare_excel_files
    src = data_dir / "employees_a.xlsx"
    tgt = data_dir / "employees_b.xlsx"
    _write_xlsx(src, _BASELINE)
    _write_xlsx(tgt, _BASELINE)
    result = compare_excel_files(
        source_file=src, target_file=tgt,
        key_columns=["employee_id"], float_tolerance=0.01,
        report_path=str(data_dir / "xlsx_identical_report.html"),
    )
    logger.info(f"XLSX identical: passed={result.passed_count}, failed={result.failed_count}")
    logger.info(f"HTML report: {result.report_path}")
    assert result.passed, f"Identical XLSX files should match. Report: {result.report_path}"


@pytest.mark.data
def test_xlsx_to_xlsx_with_differences(data_dir):
    """.xlsx files with seeded differences report exactly 2 mismatched rows."""
    from utils.data_comparison_utils import compare_excel_files
    src = data_dir / "employees_baseline.xlsx"
    tgt = data_dir / "employees_changed.xlsx"
    _write_xlsx(src, _BASELINE)
    _write_xlsx(tgt, _CHANGED)
    result = compare_excel_files(
        source_file=src, target_file=tgt,
        key_columns=["employee_id"], float_tolerance=0.01,
        report_path=str(data_dir / "xlsx_diff_report.html"),
    )
    logger.info(f"XLSX diff: failed={result.failed_count} (report: {result.report_path})")
    assert result.failed_count == 2, (
        f"Expected 2 changed rows, got {result.failed_count}. Report: {result.report_path}"
    )


@pytest.mark.data
def test_xls_to_xls_identical(data_dir):
    """Two identical legacy .xls files compare as PASSED.

    pandas 3.x can READ .xls (via xlrd) but can no longer WRITE it, so fixtures
    are written with xlwt directly. The comparison reads .xls transparently.
    """
    from utils.data_comparison_utils import compare_excel_files
    src = data_dir / "employees_a.xls"
    tgt = data_dir / "employees_b.xls"
    _write_xls(src, _BASELINE)
    _write_xls(tgt, _BASELINE)
    result = compare_excel_files(
        source_file=src, target_file=tgt,
        key_columns=["employee_id"], float_tolerance=0.01,
        report_path=str(data_dir / "xls_identical_report.html"),
    )
    logger.info(f"XLS identical: passed={result.passed_count}, failed={result.failed_count}")
    logger.info(f"HTML report: {result.report_path}")
    assert result.passed, f"Identical XLS files should match. Report: {result.report_path}"


@pytest.mark.data
def test_xls_to_xls_with_differences(data_dir):
    """Legacy .xls files with seeded differences report exactly 2 mismatched rows."""
    from utils.data_comparison_utils import compare_excel_files
    src = data_dir / "employees_baseline.xls"
    tgt = data_dir / "employees_changed.xls"
    _write_xls(src, _BASELINE)
    _write_xls(tgt, _CHANGED)
    result = compare_excel_files(
        source_file=src, target_file=tgt,
        key_columns=["employee_id"], float_tolerance=0.01,
        report_path=str(data_dir / "xls_diff_report.html"),
    )
    logger.info(f"XLS diff: failed={result.failed_count} (report: {result.report_path})")
    assert result.failed_count == 2, (
        f"Expected 2 changed rows, got {result.failed_count}. Report: {result.report_path}"
    )


@pytest.mark.data
def test_multi_sheet_requires_per_sheet_comparison(data_dir):
    """Multi-sheet workbooks: only ONE sheet is compared per call.

    Demonstrates:
      1. Default (sheet_name=0) compares only the FIRST sheet -- a difference on
         a later sheet is silently NOT detected.
      2. To validate the whole workbook, loop over sheets and compare each.
      3. sheet_name=None compares every sheet in one call.
    """
    from utils.data_comparison_utils import compare_excel_files

    src = data_dir / "workbook_src.xlsx"
    _write_xlsx_multi(src, {"Employees": _BASELINE, "Departments": [
        {"dept_id": 1, "name": "Engineering", "location": "NYC"},
        {"dept_id": 2, "name": "Sales", "location": "SF"},
    ]})
    tgt = data_dir / "workbook_tgt.xlsx"
    _write_xlsx_multi(tgt, {"Employees": _BASELINE, "Departments": [
        {"dept_id": 1, "name": "Engineering", "location": "Boston"},
        {"dept_id": 2, "name": "Sales", "location": "SF"},
    ]})

    # 1) Default: first sheet only -> Departments change NOT detected.
    first_only = compare_excel_files(
        source_file=src, target_file=tgt,
        key_columns=["employee_id"],
        report_path=str(data_dir / "workbook_first_sheet_report.html"),
    )
    logger.info(f"Default (first sheet only): passed={first_only.passed}")
    assert first_only.passed, "First sheet (Employees) is identical, so default compare passes"

    # 2) Correct pattern: compare every sheet explicitly.
    import pandas as pd
    sheet_names = pd.ExcelFile(src).sheet_names
    logger.info(f"Workbook sheets: {sheet_names}")
    per_sheet_failures = {}
    for sheet in sheet_names:
        keys = ["employee_id"] if sheet == "Employees" else ["dept_id"]
        result = compare_excel_files(
            source_file=src, target_file=tgt, sheet_name=sheet,
            key_columns=keys,
            report_path=str(data_dir / f"workbook_{sheet}_report.html"),
        )
        per_sheet_failures[sheet] = result.failed_count
        logger.info(f"  sheet '{sheet}': failed={result.failed_count} (report: {result.report_path})")

    assert per_sheet_failures["Employees"] == 0, "Employees sheet is identical"
    assert per_sheet_failures["Departments"] == 1, "Departments sheet has 1 changed row"

    # 3) sheet_name=None compares every sheet in one call (multi-sheet result).
    whole = compare_excel_files(
        source_file=src, target_file=tgt, sheet_name=None,
        report_path=str(data_dir / "workbook_all_sheets_report.html"),
    )
    logger.info(f"All sheets in one call: passed={whole.passed}")
    assert not whole.passed, "Comparing all sheets detects the Departments change"
