from __future__ import annotations

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "login/"
    auth_error_message = "Your login attempt has failed. Make sure the username and password are correct."

    @property
    def username_input(self) -> Locator:
        return self.page.get_by_placeholder("Username")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_placeholder("Password")

    @property
    def log_in_button(self) -> Locator:
        return self.page.get_by_role("button", name="Log in")

    @property
    def error_alert(self) -> Locator:
        return self.page.get_by_text(self.auth_error_message, exact=True)

    @property
    def welcome_heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Welcome to TDLR CORE")

    def assert_loaded(self) -> None:
        expect(self.welcome_heading).to_be_visible()
        expect(self.username_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.log_in_button).to_be_visible()

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.log_in_button.click()

    def assert_invalid_login_error_displayed(self) -> None:
        expect(self.error_alert).to_be_visible()
        expect(self.error_alert).to_have_text(self.auth_error_message)
        expect(self.username_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.log_in_button).to_be_visible()
        assert "/login" in self.page.url, f"Expected login page to remain displayed, got: {self.page.url}"
