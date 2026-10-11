"""Demo UI validation test — runs out of the box against saucedemo.com.

Credentials come from environment variables so no secrets live in the code.
The defaults below match the public SauceDemo demo account, so the test runs
immediately after `pyplaykit init`. Override them for your own app:

    # PowerShell
    $env:PYPLAYKIT_TEST_USERNAME="standard_user"
    $env:PYPLAYKIT_TEST_PASSWORD="secret_sauce"

Run:
    pytest tests/demo/functional/ui/login/test_demo_login.py
"""
import os
import pytest
from core.base_page import BasePage

# Public SauceDemo demo target. This demo is intentionally self-contained and
# always hits saucedemo.com (rather than the configured base_url) so it runs
# out of the box. Override with PYPLAYKIT_DEMO_URL if you mirror the site.
DEMO_BASE_URL = os.environ.get("PYPLAYKIT_DEMO_URL", "https://www.saucedemo.com")

# Credentials are sourced from env vars — never hardcode real secrets in tests.
DEMO_USERNAME = os.environ.get("PYPLAYKIT_TEST_USERNAME", "standard_user")
DEMO_PASSWORD = os.environ.get("PYPLAYKIT_TEST_PASSWORD", "secret_sauce")


class LoginPage(BasePage):
    """Minimal page object for the SauceDemo login screen."""
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = "[data-test='error']"
    INVENTORY_CONTAINER = "[data-test='inventory-container']"

    def login(self, username: str, password: str) -> None:
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def error_message(self) -> str:
        return self.text(self.ERROR_MESSAGE)


@pytest.mark.smoke
@pytest.mark.ui
def test_successful_login(page, runtime_options):
    """Validate that a valid user lands on the inventory page after login."""
    login = LoginPage(page, runtime_options["resilience_policy"])

    login.navigate(DEMO_BASE_URL)
    login.login(DEMO_USERNAME, DEMO_PASSWORD)

    # After login the inventory container must be visible
    assert login.is_visible(LoginPage.INVENTORY_CONTAINER, timeout=5000), (
        "Inventory page did not load after login"
    )


@pytest.mark.negative
@pytest.mark.ui
def test_invalid_credentials_show_error(page, runtime_options):
    """Validate that wrong credentials produce an error message."""
    login = LoginPage(page, runtime_options["resilience_policy"])

    login.navigate(DEMO_BASE_URL)
    login.login("wrong_user", "wrong_pass")

    error = login.error_message()
    assert "Username and password do not match" in error, (
        f"Unexpected error text: {error}"
    )
