# SRC -> TGT PostgreSQL Comparison Demo

Spins up **two PostgreSQL containers** -- a *source* (legacy) database and a
*target* (migrated) database -- each holding `employee` (5000 rows) and
`department` (50 rows). The two schemas use **different column names** and carry
**metadata columns that are ignored**, and the target has a few **deliberate,
visible data differences**. A pytest demo validates SRC against TGT using the
framework's `compare_db_to_db` and produces a filterable HTML/CSS report.

## Seeded differences (what the report should catch)

| Table | Key | Difference | Report type |
|---|---|---|---|
| employee | 100 | salary changed | VALUE_MISMATCH |
| employee | 250 | name changed | VALUE_MISMATCH |
| employee | 375 | email changed | VALUE_MISMATCH |
| employee | 500 | salary + name changed | VALUE_MISMATCH (1 row) |
| employee | 4999 | deleted in target | SOURCE_ONLY |
| employee | 5001 | extra in target | TARGET_ONLY |
| department | 7 | location changed | VALUE_MISMATCH |

`row_version` (department) and `created_ts` (employee) differ on **every** row
but are ignored, proving the ignore-fields feature.

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2)
- `pip install psycopg2-binary pandas openpyxl`

## Steps

```bash
# 1. Start + seed both databases (from this folder)
cd tests/demo/functional/database/postgres_src_tgt
docker compose up -d

# 2. Wait until both report healthy
docker compose ps

# 3. Run the comparison demo (from the project root)
cd ../../../../..
pytest tests/demo/functional/database/postgres_src_tgt/test_src_tgt_comparison.py -v -s

# 4. Tear down (removes all data; next `up` re-seeds)
cd tests/demo/functional/database/postgres_src_tgt
docker compose down -v
```

## Connection details

| | SRC (source) | TGT (target) |
|---|---|---|
| Host | localhost | localhost |
| Port | **55432** | **55433** |
| Database | `srcdb` | `tgtdb` |
| User / Password | `demo` / `demo` | `demo` / `demo` |

Override via env vars if the ports clash: `PYPLAYKIT_SRC_DB_HOST/PORT`,
`PYPLAYKIT_TGT_DB_HOST/PORT`, `PYPLAYKIT_DEMO_DB_USER`,
`PYPLAYKIT_DEMO_DB_PASSWORD`.

## Adapting to your real databases

1. Point the `_SRC` / `_TGT` dicts (or env vars) at your real hosts.
2. Replace the `query_source` / `query_target` SELECTs with your tables.
3. Update `source_column_mapping` to your legacy->new column names.
4. List your metadata/audit columns in `ignore_fields`.
5. Change assertions to `assert result.passed` when you expect a clean match.
