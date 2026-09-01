from __future__ import annotations

import os

import pytest
from playwright.sync_api import expect

from pages.weather_modification_page import WeatherModificationPage
from utils.runtime_tracker import RuntimeTracker, chicago_now


@pytest.mark.auth
@pytest.mark.regression
def test_weather_modification_individual_details_validation(page, request):
    test_case_name = "Weather Modification Individual Details Validation"
    tracker = RuntimeTracker(test_case_name)
    request.node.runtime_tracker = tracker

    username = os.getenv("LOGIN_USERNAME", "s0n4g@web-library.net")
    password = os.getenv("LOGIN_PASSWORD", "Password1234567!")

    weather_page = WeatherModificationPage(page)

    status = "PASSED"
    try:
        with tracker.step(page, 1, "Navigate to login page and authenticate with valid credentials"):
            weather_page.login(username=username, password=password)
            expect(page.get_by_text("TDLR CORE Dashboard", exact=False)).to_be_visible(timeout=30000)

        with tracker.step(page, 2, "Navigate to Apply for a License and open Weather Modification License"):
            weather_page.navigate_to_weather_modification_individual()
            expect(page.get_by_text("New License Application", exact=False)).to_be_visible(timeout=30000)

        with tracker.step(page, 3, "Attempt to progress to Individual Details page"):
            result = weather_page.attempt_reach_individual_details()
            request.node.weather_modification_result = result
            assert result["individual_details_heading_visible"], "Individual Details heading was not displayed"

        with tracker.step(page, 4, "Validate actual page state and identify blocker for field-level validation"):
            result = request.node.weather_modification_result
            if result["business_question_visible"]:
                weather_page.assert_business_question_blocker_visible()
                assert result["blocker"] == "Business Information Question step requires selection before proceeding"
            else:
                visible_labels = weather_page.visible_individual_detail_labels()
                assert visible_labels, "No expected individual detail labels were visible for validation"

    except Exception:
        status = "FAILED"
        raise
    finally:
        report_path = tracker.write_report(status=status, ended_at=chicago_now())
        request.node.runtime_report_path = str(report_path)
