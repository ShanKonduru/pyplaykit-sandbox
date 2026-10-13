<p align="center">
  <img src="https://raw.githubusercontent.com/ShanInnominds/innoHarmony-assets/main/readme/hero.png" alt="innoHarmony™ by Innominds — Unified Quality Engineering Framework" width="100%">
</p>

# innoHarmony™ — Project Overview

This project was created by `innoharmony init`. It is a ready-to-extend **innoHarmony** test suite:
UI, API, data and device tests on **pytest + Playwright**, sharing one configuration model and one
set of reports. innoHarmony is engineered by **Innominds**.

> Check the installed framework version with `innoharmony --version`, and read any guide offline
> with `innoharmony docs <topic>` — the guides ship with the package and always match your version.

---

## What `innoharmony init` created

| Path | Purpose |
|---|---|
| `conftest.py`, `pytest.ini` | pytest wiring and marker registration (the framework fixtures load automatically) |
| `config/config.yaml` | Framework defaults — browser, execution, reporting, resilience, quality gate, plugins … |
| `config/environments.yaml` | Base URLs and settings per environment (`dev`, `qa`, `uat`, `prod`, …) |
| `config/projects/<name>.yaml` | Per-project overrides for the multi-project layout |
| `config/org.example/` | Sample org → business-unit → project governance policy with locked keys; inactive until renamed to `config/org/` |
| `config/devices.yaml` | Devices under test, benches and simulated twins |
| `pages/` | Your page objects (`login_page.py` is a working example) |
| `test_data/` | Test data (`${ENV_VAR}` placeholders resolve at load time), JSON schemas, Pact files, a demo SQLite database |
| `tests/<project>/functional/{ui,api,database}/` | Where your tests go — one folder per project, feature and domain |
| `tests/demo/` | Runnable reference tests for UI, API, database, file comparison and devices |

## First run

```bash
# demo login for the public saucedemo.com app (PowerShell: $env:NAME = "value")
export INNOHARMONY_TEST_USERNAME=standard_user
export INNOHARMONY_TEST_PASSWORD=secret_sauce

pytest tests/demo/functional/api tests/demo/functional/ui
```

| Demo | Extra it needs |
|---|---|
| `tests/demo/functional/api`, `tests/demo/functional/ui` | none |
| `tests/demo/functional/database` (Excel, SQLite, file comparison) | `pip install "innoharmony[data-comparison]"` |
| `tests/demo/functional/database/postgres_src_tgt` | `[postgresql]` and Docker (see its README) |
| `tests/demo/functional/device` (simulated thermostat) | `pip install "innoharmony[devices-serial]"` |

## Capabilities and how to switch them on

Everything is opt-in: install the extra, then enable the feature in `config/config.yaml` or on the
command line.

| Capability | How to use it | Guide |
|---|---|---|
| **Web UI testing** | Page objects inherit `BasePage` (`from innoharmony import BasePage`); Chromium, Firefox, WebKit; `--innoharmony-device "iPhone 13"` for mobile emulation | `quickstart`, `qe-visual-guide` |
| **Accessibility (WCAG)** | `[accessibility]` extra, then enable the `accessibility:` section | comments in `config/config.yaml` |
| **API testing** | `ApiClient` (retries, OAuth2, multipart, cookies) + `ResponseValidator`; GraphQL and SOAP via `[graphql-client]` / `[soap-client]`; contracts via `[contracts]` / `[pact]` | `api-testing` |
| **Data validation** | `compare_excel_files`, `compare_csv_files`, DB-to-file comparisons with key columns, tolerances and column mappings; interactive HTML mismatch reports | `data-validation`, `database` |
| **Databases** | SQLite built in; PostgreSQL, MySQL, SQL Server, Oracle, DB2, Informix, Snowflake, MongoDB via extras (`[all-databases]`) | `database` |
| **Device & embedded** | `dut` fixture, `@pytest.mark.device` / `requires_dut`; serial, MQTT, SSH, CoAP, Modbus, CAN, BLE, ADB; twins (`--innoharmony-dut-mode sim`) or hardware (`hil`); fault injection, device pool | `innoharmony devices catalog` |
| **Self-healing locators** | `resilience: enabled: true` — fallback selector chains, DOM retries, recovery audit log | `resilience` |
| **Release quality gate** | `pytest --innoharmony-quality-gate` — PASS / WARN / BLOCK verdict and risk score; exits 1 on BLOCK | `cli` |
| **Observability** | Automatic failure classification, flaky-test detection, KPI and persona reports; `innoharmony observability-report` renders them to HTML | `observability` |
| **Orchestration & plugins** | `--innoharmony-orchestration` for dependency-ordered suites; plugins with lifecycle hooks | `plugins` |
| **Secrets & governance** | Environment variables, Vault, AWS or Azure secrets (`[vault]`, `[aws]`, `[azure]`); org policy with locked keys | `secrets-governance` |
| **AI assistants (MCP)** | `[mcp]` extra, then `innoharmony-mcp serve`; every tool is also a CLI command | `mcp` |
| **CI/CD** | GitHub Actions, Jenkins and Azure DevOps templates | `ci` |

## Everyday commands

| Goal | Command |
|---|---|
| Run one project | `pytest tests/<project>` |
| Run a suite | `pytest -m smoke` · `pytest -m regression` |
| Choose environment and browser | `pytest --innoharmony-env qa --innoharmony-browser firefox` |
| Watch the browser | `pytest --innoharmony-headed` |
| Run in parallel | `pytest -n auto` |
| Check the environment first | `pytest --innoharmony-readiness-check` |
| Add projects | `innoharmony init . --multi --project-names=shop,admin` |
| Inspect the device bench | `innoharmony devices list` · `innoharmony devices check` |

## Ground rules that keep suites maintainable

- **Locators live in page objects**, never in test files.
- **No hard-coded URLs, credentials or browser settings** — use `config/` and environment variables.
- **No `sleep()`** — rely on Playwright's auto-waiting and the framework's `wait_for_visible()`.
- **Log, don't print** — use the `logger` fixture.
- **Keep tests independent** — every test gets a fresh browser context.

## Where results go

| Output | Location |
|---|---|
| HTML test report | `reports/report.html` |
| Screenshots and videos of failures | `reports/screenshots/`, `reports/videos/` |
| Observability, KPI and persona reports | `reports/observability/` |
| Data-comparison reports | `reports/data_validation/` |
| Device transcripts and simulator state | `reports/devices/<test>/` |

## Documentation

```bash
innoharmony docs                 # every topic
innoharmony docs quickstart      # print one
```

Topics: `quickstart` · `install` · `cli` · `run-tests` · `multi-project` · `test-organization` ·
`qe-visual-guide` · `api-testing` · `database` · `data-validation` · `architecture` · `resilience` ·
`observability` · `secrets-governance` · `plugins` · `ci` · `mcp`

## Support

innoHarmony is developed and supported by **Innominds**. For onboarding, enterprise support or
custom integrations, contact [RKonduru@innominds.com](mailto:RKonduru@innominds.com) or visit
[innominds.com](https://www.innominds.com).

<sub>innoHarmony™ is a trademark of Innominds. © Innominds.</sub>
