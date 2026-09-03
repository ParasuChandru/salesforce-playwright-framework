from pathlib import Path
import re
import pytest
from playwright.sync_api import Page, expect

LOGIN_URL = "https://tdlrgov--qa2.sandbox.my.site.com/s/login/"
USERNAME = "z6d0b@web-library.net"
PASSWORD = "Password1234567!"
EXPECTED_EXTERNAL_URL = "https://www.tdlr.texas.gov/apply/"
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)


def safe_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_")


def save_page_artifacts(page: Page, name: str) -> None:
    stem = safe_name(name)
    page.screenshot(path=str(ARTIFACTS_DIR / f"{stem}.png"), full_page=True)
    (ARTIFACTS_DIR / f"{stem}.html").write_text(page.content(), encoding="utf-8")


@pytest.mark.smoke
def test_portal_apply_link_directory(page: Page) -> None:
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    expect(page).to_have_url(re.compile(r"/s/login/?$"))
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
    save_page_artifacts(page, "pytest_01_login_page")

    page.get_by_label("Username").fill(USERNAME)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Log In").click()

    expect(page).to_have_url(re.compile(r"/s/?(?:\?.*)?$"), timeout=30000)
    expect(page.get_by_role("link", name="Apply for a License", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_role("link", name="Home", exact=True)).to_be_visible()
    save_page_artifacts(page, "pytest_02_home_page_after_login")

    page.get_by_role("link", name="Apply for a License", exact=True).click()
    expect(page).to_have_url(re.compile(r"/s/apply(?:\?.*)?$"), timeout=30000)
    expect(page.get_by_role("link", name="Apply for a License", exact=True)).to_have_attribute("aria-current", "page")

    core_card_heading = page.get_by_text("Apply with TDLR CORE License Management", exact=False)
    expect(core_card_heading.first).to_be_visible(timeout=30000)

    external_link = page.locator("a[href='https://www.tdlr.texas.gov/apply']")
    expect(external_link.first).to_be_visible(timeout=30000)
    expect(external_link.first).to_have_text(re.compile(r"www\.tdlr\.texas\.gov/apply"))
    save_page_artifacts(page, "pytest_03_apply_for_license_page")

    with page.context.expect_page() as new_page_info:
        external_link.first.click()

    new_page = new_page_info.value
    new_page.wait_for_load_state("domcontentloaded")
    expect(new_page).to_have_url(EXPECTED_EXTERNAL_URL, timeout=30000)
    expect(new_page).to_have_title(re.compile(r"Apply for a New License", re.I), timeout=30000)
    expect(new_page.locator("body")).to_contain_text("Apply for a New License", timeout=30000)
    save_page_artifacts(new_page, "pytest_04_external_apply_page")
    new_page.close()
