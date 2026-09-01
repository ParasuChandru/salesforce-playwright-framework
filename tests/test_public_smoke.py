from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.search_license_page import SearchLicensePage


@pytest.mark.smoke
def test_home_page_redirects_to_login_and_displays_public_content(page):
    home = HomePage(page)
    home.open()

    assert "/login" in page.url, f"Expected Salesforce site to redirect unauthenticated users to login, got: {page.url}"
    home.assert_loaded()
    home.take_screenshot("home_public_smoke.png")


@pytest.mark.smoke
def test_public_navigation_to_find_a_license_works(page):
    home = HomePage(page)
    home.open()

    home.find_license_nav.click()

    search_page = SearchLicensePage(page)
    search_page.assert_loaded()
    assert "search-license-permit-holder" in page.url
    search_page.take_screenshot("find_license_navigation.png")


@pytest.mark.smoke
def test_find_license_search_form_fields_are_rendered(page):
    search_page = SearchLicensePage(page)
    search_page.open()
    search_page.assert_loaded()

    expect(search_page.license_type_input).to_be_visible()
    expect(search_page.license_number_input).to_be_visible()
    expect(search_page.original_issue_date_input).to_be_visible()
    expect(search_page.expiration_date_input).to_be_visible()
    expect(search_page.licensee_name_input).to_be_visible()
    expect(search_page.city_input).to_be_visible()
    expect(search_page.county_input).to_be_visible()
    expect(search_page.zip_code_input).to_be_visible()


@pytest.mark.smoke
def test_find_license_reset_button_is_available(page):
    search_page = SearchLicensePage(page)
    search_page.open()

    expect(search_page.reset_button).to_be_visible()
    expect(search_page.reset_button).to_be_enabled()


@pytest.mark.smoke
def test_footer_links_and_contact_text_are_visible_on_public_pages(page):
    search_page = SearchLicensePage(page)
    search_page.open()

    body = page.locator("body")
    expect(body).to_contain_text("About This Site")
    expect(body).to_contain_text("Texas Government")
    expect(body).to_contain_text("Contact")
    expect(page.get_by_role("link", name="Privacy Policy")).to_be_visible()
    expect(page.get_by_role("link", name="Accessibility Policy")).to_be_visible()
    expect(body).to_contain_text("(800) 803-9202")
