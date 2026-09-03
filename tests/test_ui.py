"""Unit tests verifying ASCII HUD frames, UI rendering, and confirmation gates."""

import pytest

from app.main import execute_tool_safely
from app.models.schemas import ToolName, UltronMood
from app.ui.ascii_art import get_ascii_frame
from app.ui.terminal import prompt_human_confirmation


def test_ascii_frames_exist_for_all_moods() -> None:
    """Verify that every UltronMood has a defined, non-empty ASCII frame."""
    for mood in UltronMood:
        frame = get_ascii_frame(mood)
        assert frame is not None
        assert len(frame.strip()) > 0


def test_prompt_human_confirmation_accepts_yes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify confirmation gate returns True when user types 'y' or 'yes'."""
    monkeypatch.setattr("rich.console.Console.input", lambda self, prompt="": "y")
    assert prompt_human_confirmation("git_status", "Checking branch") is True

    monkeypatch.setattr("rich.console.Console.input", lambda self, prompt="": "yes")
    assert prompt_human_confirmation("git_status", "Checking branch") is True


def test_prompt_human_confirmation_rejects_no(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify confirmation gate returns False when user denies or presses Enter."""
    monkeypatch.setattr("rich.console.Console.input", lambda self, prompt="": "n")
    assert prompt_human_confirmation("git_status", "Checking branch") is False

    monkeypatch.setattr("rich.console.Console.input", lambda self, prompt="": "")
    assert prompt_human_confirmation("git_status", "Checking branch") is False


def test_execute_tool_safely_routes_telemetry() -> None:
    """Verify that execute_tool_safely routes to system_telemetry."""
    result = execute_tool_safely(ToolName.SYSTEM_TELEMETRY, {})
    assert isinstance(result, dict)
    assert "cpu_percent" in result
