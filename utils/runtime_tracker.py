from __future__ import annotations

import re
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator
from zoneinfo import ZoneInfo

from playwright.sync_api import Page

CENTRAL_TZ = ZoneInfo("America/Chicago")


def chicago_now() -> datetime:
    return datetime.now(CENTRAL_TZ)


def format_chicago_timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S America/Chicago")


def format_duration(seconds: float) -> str:
    return f"{seconds:.2f}s"


def sanitize_name(value: str, max_length: int = 50) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized[:max_length].rstrip("-") or "item"


@dataclass
class StepResult:
    step_number: int
    description: str
    status: str
    start_time: str
    end_time: str
    runtime_seconds: float
    runtime_display: str
    failure_reason: str
    possible_solution: str
    screenshot_path: str


@dataclass
class RuntimeTracker:
    test_case_name: str
    started_at: datetime = field(default_factory=chicago_now)
    steps: list[StepResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        folder_stamp = self.started_at.strftime("%Y%m%d-%H%M%S")
        self.test_case_slug = sanitize_name(self.test_case_name)
        self.run_stamp = folder_stamp
        self.screenshot_dir = Path("uploads") / "screenshots" / f"{self.test_case_slug}-{folder_stamp}"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_path = Path("artifacts") / f"{self.test_case_slug}-{folder_stamp}-runtime.json"

    @contextmanager
    def step(self, page: Page, step_number: int, description: str) -> Iterator[None]:
        start_dt = chicago_now()
        start_perf = time.perf_counter()
        failure_reason = "N/A"
        possible_solution = "N/A"
        status = "PASSED"
        try:
            yield
        except Exception as exc:
            status = "FAILED"
            failure_reason = str(exc)
            possible_solution = "Review locator, page state, and application response for this step."
            raise
        finally:
            screenshot_name = f"step-{step_number:02d}-{sanitize_name(description)}.png"
            screenshot_rel = self.screenshot_dir / screenshot_name
            try:
                page.screenshot(path=str(screenshot_rel), full_page=True)
            except Exception:
                screenshot_rel = Path("N/A")
            end_dt = chicago_now()
            runtime_seconds = time.perf_counter() - start_perf
            self.steps.append(
                StepResult(
                    step_number=step_number,
                    description=description,
                    status=status,
                    start_time=format_chicago_timestamp(start_dt),
                    end_time=format_chicago_timestamp(end_dt),
                    runtime_seconds=runtime_seconds,
                    runtime_display=format_duration(runtime_seconds),
                    failure_reason=failure_reason,
                    possible_solution=possible_solution,
                    screenshot_path="/" + screenshot_rel.as_posix() if str(screenshot_rel) != "N/A" else "N/A",
                )
            )

    def to_dict(self, status: str, ended_at: datetime | None = None) -> dict:
        end_dt = ended_at or chicago_now()
        total_seconds = (end_dt - self.started_at).total_seconds()
        return {
            "test_case_name": self.test_case_name,
            "status": status,
            "start_time": format_chicago_timestamp(self.started_at),
            "end_time": format_chicago_timestamp(end_dt),
            "total_runtime": format_duration(total_seconds),
            "screenshot_folder": "/" + self.screenshot_dir.as_posix(),
            "steps": [step.__dict__ for step in self.steps],
        }

    def write_report(self, status: str, ended_at: datetime | None = None) -> Path:
        import json

        payload = self.to_dict(status=status, ended_at=ended_at)
        self.artifact_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifact_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return self.artifact_path
