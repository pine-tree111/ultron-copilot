"""Unit tests verifying settings loading and secret masking."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_load_with_valid_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that settings load correctly when a valid API key is present."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-secret-key-12345")
    settings = Settings()

    assert settings.model_name == "openrouter/free"
    assert settings.openrouter_api_key.get_secret_value() == "test-secret-key-12345"


def test_secret_str_masks_key_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that SecretStr prevents accidental leaking of keys in logs or repr."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "super-confidential-token")
    settings = Settings()

    repr_output = repr(settings)
    assert "super-confidential-token" not in repr_output
    assert "**********" in repr_output


def test_missing_api_key_raises_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that missing OPENROUTER_API_KEY raises a strict Pydantic ValidationError."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    # Ensure .env doesn't supply it during this test
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
