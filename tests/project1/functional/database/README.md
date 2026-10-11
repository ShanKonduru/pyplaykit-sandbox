# Database Tests

## Purpose
Database tests validate data integrity, migrations, and data comparisons.

## Organization
Tests are organized by **category**:
- `data_integrity/` - Foreign keys, constraints, referential integrity
- `data_comparison/` - Excel/DB comparisons, migration validation
- `migrations/` - Schema migration validation

## Naming Convention
- `test_<table>_<validation>.py`
- Example: `test_orders_data_integrity.py`, `test_users_migration.py`

## Example Structure
```python
# tests/functional/database/data_comparison/test_excel_to_db.py
import pytest
from pathlib import Path
from utils.data_comparison_utils import compare_excel_to_db

@pytest.mark.database
@pytest.mark.data
def test_excel_export_matches_database(db_client):
    result = compare_excel_to_db(
        excel_file=Path("test_data/users_export.xlsx"),
        db_client=db_client,
        db_query="SELECT * FROM users ORDER BY user_id",
        key_columns=["user_id"],
        ignore_fields={"created_at", "updated_at"},
        float_tolerance=0.01
    )
    assert result.passed, f"Validation failed: {result.summary}"
```

## Running Database Tests
```bash
# Run all database tests
pytest tests/functional/database/

# Run specific category
pytest tests/functional/database/data_comparison/

# Run with database configuration
pytest tests/functional/database/ --pyplaykit-env qa
```

## Best Practices
1. Use `db_client` fixture for database connections
2. Use data comparison utils for validation:
   - `compare_excel_to_db()` - Excel vs Database
   - `compare_db_to_db()` - Database vs Database
   - `compare_db_to_excel()` - Database export validation
3. Use `key_columns` for unordered data
4. Use `ignore_fields` for timestamps/metadata
5. Always clean up test data after tests
