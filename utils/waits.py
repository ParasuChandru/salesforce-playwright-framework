from __future__ import annotations

from playwright.sync_api import Page, expect


def wait_for_salesforce_ready(page: Page, timeout: int = 20_000) -> None:
    """Wait for common Experience Cloud/LWC shell elements to settle.

    Salesforce Experience Cloud pages often finish rendering after the initial
    DOM content event. This helper uses a few tolerant checks instead of relying
    purely on network idle.
    """
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1200)

    possible_main = page.locator("main, [role='main'], #main, .siteforceContentArea")
    if possible_main.count() > 0:
        expect(possible_main.first).to_be_visible(timeout=timeout)

    body = page.locator("body")
    expect(body).to_be_visible(timeout=timeout)
    page.wait_for_timeout(800)


def dismiss_generic_overlays(page: Page) -> None:
    """Dismiss generic toast/banner/refresh affordances when present."""
    close_candidates = [
        page.get_by_role("button", name="×"),
        page.get_by_role("button", name="Close"),
        page.get_by_role("link", name="×"),
    ]
    for locator in close_candidates:
        try:
            if locator.first.is_visible(timeout=1000):
                locator.first.click(timeout=1000)
                page.wait_for_timeout(300)
        except Exception:
            pass
