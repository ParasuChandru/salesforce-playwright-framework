from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from utils.config import settings

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def ensure_artifacts_dir() -> None:
    Path("artifacts").mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    browser_launcher = getattr(playwright_instance, settings.browser_name)
    browser = browser_launcher.launch(headless=settings.headless)
    yield browser
    browser.close()


@pytest.fixture()
def context(browser: Browser) -> BrowserContext:
    context = browser.new_context(viewport={"width": 1440, "height": 1200}, ignore_https_errors=True)
    yield context
    context.close()


@pytest.fixture()
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Page:
    page = context.new_page()
    yield page

    outcome = getattr(request.node, "rep_call", None)
    failed = bool(outcome and outcome.failed)
    if failed:
        safe_name = request.node.name.replace("/", "_").replace(" ", "_")
        page.screenshot(path=os.path.join("artifacts", f"{safe_name}_failed.png"), full_page=True)
    page.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
