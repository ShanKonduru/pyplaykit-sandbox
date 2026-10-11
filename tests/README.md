# Multi-Project Test Organization

This repository supports **multiple projects** with separate test suites.

## Structure
```
tests/
├── <project>/           # One folder per project
│   ├── functional/
│   │   ├── ui/
│   │   ├── api/
│   │   └── database/
│   └── ...
│
└── demo/                # Runnable reference tests (functional/{ui,api,database})
```

## Adding a New Project

```bash
# Add one or more projects (comma-separated)
pyplaykit init . --multi --project-names=shop,admin,mobile
```

This generates the `tests/<project>/` tree **and** a matching
`config/projects/<project>.yaml` for each name, so config and tests are created
in lockstep.

## Per-Project Configuration

Each project has its own `config/projects/<project>.yaml` describing
environment URLs, API endpoints, test users, and feature flags:

```yaml
project:
  name: "shop"
  environments:
    qa:
      base_url: "https://qa.shop.example.com"
      api_base_url: "https://api.qa.shop.example.com"
      database_url: "postgresql://qa-db:5432/shop_qa"   # non-secret parts only
  test_users:
    standard_user:
      username: "${SHOP_USERNAME}"      # expanded from environment variables
      password: "${SHOP_PASSWORD}"
```

When a project is active, its `environments.<env>` node is **deep-merged over**
the global `config/environments.yaml` defaults (project wins; anything the
project omits — e.g. `tgt_db`, `auth` — is inherited). Database credentials are
never stored in config: only the non-secret host/port/database come from
`database_url`; the user and password come from the `SRC_DB_USER` /
`SRC_DB_PASSWORD` (and `TGT_*`) environment variables. `${VAR}` placeholders are
expanded from the environment at load time.

Legacy single-project repos with a flat `config/environments.yaml` and no
project keep resolving exactly as before.

## Selecting the Active Project

The active project is **auto-detected from the test path** (`tests/<project>/…`),
so engineers rarely pass a flag:

```bash
pytest tests/shop/ --pyplaykit-env qa      # resolves shop's QA URLs/DB
pytest tests/admin/ --pyplaykit-env qa     # resolves admin's QA URLs/DB
```

To pin a project explicitly (or when one run mixes projects), pass the flag or
env var — these override auto-detection:

```bash
pytest tests/ --pyplaykit-project shop
PYPLAYKIT_PROJECT=shop pytest tests/
```

When a single invocation collects tests from more than one project, no project
is pinned and resolution falls back to the flat global config — run one project
per invocation, or pass `--pyplaykit-project`.

Project-scoped values are exposed on `runtime_options`: `project`, `base_url`,
`api_base_url`, `api_endpoints`, `test_users`, and `features`.

## Running Tests by Project

```bash
# Run all tests for a single project
pytest tests/shop/

# Run UI tests for a project
pytest tests/shop/functional/ui/

# Run all tests across all projects
pytest tests/
```
