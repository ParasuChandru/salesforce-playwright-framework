from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class HomePage(BasePage):
    path = ""

    @property
    def welcome_heading(self):
        return self.page.get_by_role("heading", name="Welcome to TDLR CORE")

    @property
    def login_heading(self):
        return self.page.get_by_role("heading", name="Log In: TDLR CORE License Management")

    @property
    def login_button(self):
        return self.page.get_by_role("button", name="Log in")

    @property
    def register_link(self):
        return self.page.get_by_text("New User - Register", exact=False)

    @property
    def forgot_password_link(self):
        return self.page.get_by_text("Forgot your password?", exact=False)

    @property
    def find_license_nav(self):
        return self.page.get_by_role("link", name="Find a License")

    def assert_loaded(self) -> None:
        expect(self.welcome_heading).to_be_visible()
        expect(self.login_heading).to_be_visible()
        expect(self.login_button).to_be_visible()
        expect(self.find_license_nav).to_be_visible()
        expect(self.body).to_contain_text("Get Started with TDLR CORE")
        expect(self.body).to_contain_text("Apply for a new license")
