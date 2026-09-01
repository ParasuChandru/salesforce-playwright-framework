from __future__ import annotations

import pytest

from pages.login_page import LoginPage
from utils.random_data import random_email, random_password
from utils.runtime_tracker import RuntimeTracker, chicago_now


@pytest.mark.auth
def test_portal_login_validate_error_message_is_displayed_when_invalid_credentials_are_entered(page, request):
    test_case_name = "Portal_Login_Validate_Error_Message_Is_Displayed_When_Invalid_Credentials_Are_Entered"
    tracker = RuntimeTracker(test_case_name)
    request.node.runtime_tracker = tracker

    login_page = LoginPage(page)
    end_time = None
    status = "PASSED"

    try:
        with tracker.step(page, 1, "navigate-to-portal-login-page"):
            login_page.open()
            login_page.assert_loaded()

        with tracker.step(page, 2, "prepare-invalid-login-credentials"):
            invalid_username = random_email()
            invalid_password = random_password()
            assert "@" in invalid_username
            assert len(invalid_password) >= 8

        with tracker.step(page, 3, "enter-invalid-username"):
            login_page.username_input.fill(invalid_username)

        with tracker.step(page, 4, "enter-invalid-password"):
            login_page.password_input.fill(invalid_password)

        with tracker.step(page, 5, "click-log-in-and-validate-error-message"):
            login_page.log_in_button.click()
            login_page.assert_invalid_login_error_displayed()

    except Exception:
        status = "FAILED"
        raise
    finally:
        end_time = chicago_now()
        report_path = tracker.write_report(status=status, ended_at=end_time)
        request.node.runtime_report_path = str(report_path)
        request.node.runtime_status = status
        request.node.runtime_start_time = tracker.started_at
        request.node.runtime_end_time = end_time
