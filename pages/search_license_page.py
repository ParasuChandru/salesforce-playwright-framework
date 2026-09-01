from __future__ import annotations

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class SearchLicensePage(BasePage):
    path = "search-license-permit-holder"

    @property
    def page_heading(self) -> Locator:
        return self.page.get_by_text("Find A License", exact=True)

    @property
    def search_button(self) -> Locator:
        return self.page.get_by_role("button", name="Search")

    @property
    def reset_button(self) -> Locator:
        return self.page.get_by_role("button", name="Reset")

    @property
    def license_type_input(self) -> Locator:
        return self.page.locator("input[aria-label='License Type']")

    @property
    def original_issue_date_input(self) -> Locator:
        return self.page.locator("input[aria-label='Original Issue Date']")

    @property
    def expiration_date_input(self) -> Locator:
        return self.page.locator("input[aria-label='Expiration Date']")

    @property
    def text_inputs(self) -> Locator:
        return self.page.locator("input[type='text']")

    def input_by_id_prefix(self, prefix: str) -> Locator:
        return self.page.locator(f"input[id^='{prefix}']")

    @property
    def license_number_input(self) -> Locator:
        return self.input_by_id_prefix("input12-")

    @property
    def licensee_name_input(self) -> Locator:
        return self.input_by_id_prefix("input15-")

    @property
    def city_input(self) -> Locator:
        return self.input_by_id_prefix("input16-")

    @property
    def county_input(self) -> Locator:
        return self.page.locator("input[aria-label='County']")

    @property
    def zip_code_input(self) -> Locator:
        return self.input_by_id_prefix("input17-")

    def assert_loaded(self) -> None:
        expect(self.page_heading).to_be_visible()
        expect(self.search_button).to_be_visible()
        expect(self.reset_button).to_be_visible()
        expect(self.body).to_contain_text("To view additional license details")
        expect(self.body).to_contain_text("If license not found, please contact Customer Service")

    def fill_basic_filters(self, licensee_name: str = "Test", city: str = "Austin", zip_code: str = "78701") -> None:
        self.licensee_name_input.fill(licensee_name)
        self.city_input.fill(city)
        self.zip_code_input.fill(zip_code)

    def reset_form(self) -> None:
        self.reset_button.click()
