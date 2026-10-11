# UI Tests

## Purpose
UI tests validate the user interface and user workflows using Playwright.

## Organization
Tests are organized by **feature** or **page**:
- `login/` - Login and authentication flows
- `dashboard/` - Dashboard functionality
- `user_management/` - User CRUD operations

## Naming Convention
- `test_<feature>_<scenario>.py`
- Example: `test_login_success.py`, `test_login_failure.py`

## Example Structure
```python
# tests/functional/ui/login/test_login_success.py
import pytest
from pages.login_page import LoginPage

@pytest.mark.smoke
@pytest.mark.ui
def test_valid_user_can_login(page, runtime_options):
    login_page = LoginPage(page, runtime_options["resilience_policy"])
    login_page.navigate(runtime_options["base_url"])
    login_page.login("valid_user", "valid_pass")
    assert login_page.is_logged_in()
```

## Running UI Tests
```bash
# Run all UI tests
pytest tests/functional/ui/

# Run specific feature
pytest tests/functional/ui/login/

# Run with specific browser
pytest tests/functional/ui/ --pyplaykit-browser firefox
```

## Best Practices
1. Use Page Object Model (POM) - keep locators in `pages/` directory
2. One test = one user scenario
3. Use appropriate markers: `@pytest.mark.smoke`, `@pytest.mark.regression`
4. Keep tests independent - no test should depend on another
