from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from pages.login_page import LoginPage
from utils.waits import dismiss_generic_overlays, wait_for_salesforce_ready


class WeatherModificationPage(BasePage):
    path = ""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.login_page = LoginPage(page)

    @property
    def apply_for_license_link(self) -> Locator:
        return self.page.get_by_role("link", name="Apply for a License")

    @property
    def weather_modification_card(self) -> Locator:
        return self.page.get_by_text("Weather Modification License", exact=False)

    @property
    def dashboard_heading(self) -> Locator:
        return self.page.get_by_text("TDLR CORE Dashboard", exact=False)

    @property
    def individual_radio(self) -> Locator:
        return self.page.get_by_role("radio", name="Individual")

    @property
    def next_button(self) -> Locator:
        return self.page.get_by_role("button", name="Next")

    @property
    def continue_button(self) -> Locator:
        return self.page.get_by_role("button", name="Continue")

    @property
    def business_question_heading(self) -> Locator:
        return self.page.get_by_text("What Business is this license application for", exact=False)

    @property
    def new_business_radio(self) -> Locator:
        return self.page.get_by_role("radio", name="New Business")

    @property
    def existing_business_radio(self) -> Locator:
        return self.page.get_by_role("radio", name="New Location for existing business")

    @property
    def business_combobox(self) -> Locator:
        return self.page.locator('input[role="combobox"][aria-label*="Select the applicable Business"]')

    @property
    def individual_details_heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Individual Details")

    def draft_card(self, draft_number: str) -> Locator:
        card = self.page.locator("runtime_omnistudio_flexcards-block").filter(
            has_text="Weather Modification License"
        ).filter(has_text=draft_number)
        if card.count() > 0:
            return card.first
        return self.page.locator("article, section, div, li, tr, [role='row']").filter(
            has_text=f"Weather Modification License {draft_number}"
        ).first

    def login(self, username: str, password: str) -> None:
        self.login_page.open()
        self.login_page.assert_loaded()
        self.login_page.login(username=username, password=password)
        wait_for_salesforce_ready(self.page)
        dismiss_generic_overlays(self.page)

    def navigate_to_weather_modification_individual(self) -> None:
        expect(self.apply_for_license_link).to_be_visible(timeout=20000)
        self.apply_for_license_link.click()
        wait_for_salesforce_ready(self.page)
        dismiss_generic_overlays(self.page)

        expect(self.weather_modification_card).to_be_visible(timeout=20000)
        card_container = self.weather_modification_card.locator(
            "xpath=ancestor::*[self::article or self::section or self::div][contains(., 'Weather Modification License')][1]"
        )
        apply_now = card_container.get_by_role("link", name="Apply Now")
        if apply_now.count() == 0:
            apply_now = self.page.locator("a,button").filter(has_text="Apply Now").first
        expect(apply_now).to_be_visible(timeout=20000)
        apply_now.scroll_into_view_if_needed()
        apply_now.click(force=True)
        wait_for_salesforce_ready(self.page)
        dismiss_generic_overlays(self.page)

        if self.individual_radio.count() > 0:
            expect(self.individual_radio).to_be_visible(timeout=15000)
            self.individual_radio.check()
            wait_for_salesforce_ready(self.page)
            dismiss_generic_overlays(self.page)

    def open_weather_modification_draft(self, draft_number: str) -> None:
        wait_for_salesforce_ready(self.page)
        dismiss_generic_overlays(self.page)
        expect(self.dashboard_heading).to_be_visible(timeout=30000)

        draft_card = self.draft_card(draft_number)
        expect(draft_card).to_be_visible(timeout=30000)
        expect(draft_card).to_contain_text("Weather Modification License")

        edit_application = draft_card.get_by_role("link", name="Edit Application")
        if edit_application.count() == 0:
            edit_application = draft_card.get_by_role("button", name="Edit Application").first
        if edit_application.count() == 0:
            edit_application = draft_card.locator("a,button").filter(has_text="Edit Application").first

        expect(edit_application).to_be_visible(timeout=20000)
        edit_application.scroll_into_view_if_needed()
        edit_application.click(force=True)
        wait_for_salesforce_ready(self.page)
        dismiss_generic_overlays(self.page)

    def attempt_reach_individual_details(self) -> dict:
        result = {
            "individual_details_heading_visible": False,
            "business_question_visible": False,
            "new_license_application_visible": False,
            "draft_number_visible": False,
            "current_url": self.page.url,
            "product_text": "",
            "blocker": "",
        }

        for _ in range(3):
            wait_for_salesforce_ready(self.page)
            dismiss_generic_overlays(self.page)
            if self.individual_details_heading.count() > 0 and self.individual_details_heading.first.is_visible():
                result["individual_details_heading_visible"] = True
            if self.business_question_heading.count() > 0 and self.business_question_heading.first.is_visible():
                result["business_question_visible"] = True
                result["blocker"] = "Business Information Question step requires selection before proceeding"
                break
            if self.page.get_by_text("New License Application", exact=False).count() > 0:
                try:
                    if self.page.get_by_text("New License Application", exact=False).first.is_visible():
                        result["new_license_application_visible"] = True
                except Exception:
                    pass
            if self.page.get_by_text("DRAFT-0000006127", exact=False).count() > 0:
                try:
                    if self.page.get_by_text("DRAFT-0000006127", exact=False).first.is_visible():
                        result["draft_number_visible"] = True
                except Exception:
                    pass
            if (
                result["individual_details_heading_visible"]
                or result["business_question_visible"]
                or result["new_license_application_visible"]
                or result["draft_number_visible"]
            ):
                break
            if self.next_button.count() > 0 and self.next_button.first.is_visible():
                try:
                    self.next_button.first.click(timeout=10000)
                    wait_for_salesforce_ready(self.page)
                    dismiss_generic_overlays(self.page)
                except Exception:
                    break
            else:
                break

        text_snapshot = self.page.locator("body").inner_text(timeout=10000)
        if "Apprentice Pump Installer" in text_snapshot:
            result["product_text"] = "Apprentice Pump Installer"
        elif "Weather Modification License" in text_snapshot:
            result["product_text"] = "Weather Modification License"
        result["current_url"] = self.page.url
        return result

    def assert_business_question_blocker_visible(self) -> None:
        expect(self.business_question_heading).to_be_visible(timeout=20000)
        expect(self.business_combobox).to_be_visible(timeout=20000)

    def visible_individual_detail_labels(self) -> list[str]:
        labels = [
            "Legal First Name",
            "Legal Middle Name",
            "Legal Last Name",
            "Suffix",
            "Date of Birth",
            "Gender",
            "Military Status",
            "Do you have a Social Security Number?",
            "Social Security Number",
            "Email Address",
            "Email Type",
            "Phone Number",
            "Phone Type",
            "Is physical address the same as mailing address?",
            "Mailing Address",
            "Physical Address",
            "Have you ever been convicted of, or placed on deferred adjudication for, any misdemeanor or felony, other than a minor traffic violation?",
            "Have you ever had an occupational license, certification, or registration suspended, revoked, or denied in any state?",
        ]
        visible = []
        for label in labels:
            locator = self.page.get_by_text(label, exact=False)
            if locator.count() > 0:
                try:
                    if locator.first.is_visible():
                        visible.append(label)
                except Exception:
                    pass
        return visible
