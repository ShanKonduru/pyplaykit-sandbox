"""Starter page object — copy this pattern for your own pages.

Locators live as class constants; methods expose intent (``login``,
``is_logged_in``) rather than raw selectors. Construct with the resilience
policy so self-healing locators work when enabled:

    from pages.login_page import LoginPage
    login_page = LoginPage(page, runtime_options["resilience_policy"])
    login_page.navigate(runtime_options["base_url"])
"""

from core.base_page import BasePage


class LoginPage(BasePage):
    """Page object for a generic login screen (SauceDemo selectors by default)."""

    # Locators as class constants — never put raw selectors in tests.
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_BANNER = "[data-test='error']"
    INVENTORY_CONTAINER = "[data-test='inventory-container']"

    def login(self, username: str, password: str) -> None:
        """Fill credentials and submit the login form."""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        """Return the login error banner text."""
        return self.text(self.ERROR_BANNER)

    def is_logged_in(self) -> bool:
        """Return True when the post-login landing element is visible."""
        return self.is_visible(self.INVENTORY_CONTAINER, timeout=5000)
