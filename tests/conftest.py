"""Global pytest fixtures and test environment configuration."""

import pytest


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Automatically provide mock environment variables for all tests."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-mock-api-key-12345")
    monkeypatch.setenv("ENABLE_VOICE", "false")
