from __future__ import annotations

import json
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
    Path("uploads").mkdir(exist_ok=True)
    Path("uploads/screenshots").mkdir(parents=True, exist_ok=True)


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

    if rep.when == "call":
        tracker = getattr(item, "runtime_tracker", None)
        report_path = getattr(item, "runtime_report_path", None)
        if tracker and report_path:
            payload = json.loads(Path(report_path).read_text(encoding="utf-8"))
            item.user_properties.extend(
                [
                    ("runtime_status", payload.get("status")),
                    ("runtime_start_time", payload.get("start_time")),
                    ("runtime_end_time", payload.get("end_time")),
                    ("runtime_total", payload.get("total_runtime")),
                    ("runtime_screenshot_folder", payload.get("screenshot_folder")),
                    ("runtime_report_path", report_path),
                ]
            )
