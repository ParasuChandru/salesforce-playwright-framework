from __future__ import annotations

from playwright.sync_api import Page, expect

from utils.config import settings
from utils.waits import dismiss_generic_overlays, wait_for_salesforce_ready


class BasePage:
    path = ""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, path: str | None = None) -> None:
        relative = self.path if path is None else path
        self.page.goto(f"{settings.base_url}{relative.lstrip('/')}", wait_until="domcontentloaded")
        wait_for_salesforce_ready(self.page)
        dismiss_generic_overlays(self.page)

    @property
    def body(self):
        return self.page.locator("body")

    def assert_text_visible(self, text: str) -> None:
        expect(self.page.get_by_text(text, exact=False)).to_be_visible()

    def take_screenshot(self, name: str) -> None:
        self.page.screenshot(path=f"artifacts/{name}", full_page=True)
