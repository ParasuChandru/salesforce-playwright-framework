from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = "https://tdlrgov--qa2.sandbox.my.site.com/s/"


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/") + "/"
    browser_name: str = os.getenv("BROWSER", "chromium")
    headless: bool = os.getenv("HEADLESS", "true").lower() in {"1", "true", "yes", "on"}
    login_username: str = os.getenv("LOGIN_USERNAME", "")
    login_password: str = os.getenv("LOGIN_PASSWORD", "")


settings = Settings()
