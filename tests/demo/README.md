# Demo Tests

Runnable **reference tests** that demonstrate PyPlayKit features. They mirror
the same `functional/{ui,api,database}` layout as your project test tree, so
what you learn here maps directly onto where your real tests live.

## ⚠️ Important
**Don't add your project tests here** — use `demo/` as a learning resource,
then add your own tests under `tests/<project>/functional/...`.

## Layout
```
tests/demo/
└── functional/
    ├── ui/login/          test_demo_login.py    # Playwright UI (saucedemo.com)
    ├── api/               test_demo_api.py       # REST API (jsonplaceholder)
    └── database/          conftest.py            # local SQLite demo_db fixture
                           test_demo_db.py        # SQLite migration/row-count checks
                           test_demo_excel.py     # Excel comparison patterns
```

## Runs out of the box
- **UI** — targets https://www.saucedemo.com; credentials come from
  `PYPLAYKIT_TEST_USERNAME` / `PYPLAYKIT_TEST_PASSWORD` (defaults match the
  public demo account, so no setup is needed).
- **API** — targets the public https://jsonplaceholder.typicode.com service.
- **Database** — uses the bundled `test_data/demo.db` SQLite database created
  by `pyplaykit init`. No PostgreSQL/MySQL server required.
- **Excel** — runs against sample `.xlsx` workbooks that `pyplaykit init` ships
  in `test_data/` (requires `pandas`/`openpyxl`); swap in your own files at the
  same paths to compare real data.

## Running the demos
```bash
# All demo tests
pytest tests/demo/

# By category
pytest tests/demo/functional/ui/
pytest tests/demo/functional/api/
pytest tests/demo/functional/database/
```
