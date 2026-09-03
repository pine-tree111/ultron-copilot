"""Unit tests verifying the VoiceService execution and fallback safety."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.voice import VoiceService


def test_voice_service_noop_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that VoiceService does not call API when voice is disabled."""
    monkeypatch.setenv("ENABLE_VOICE", "false")
    service = VoiceService()

    service.speak("Test speech")
    assert service._client is None


def test_voice_service_handles_synthesis_failure_gracefully(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that audio failure does not crash the application."""
    monkeypatch.setenv("ENABLE_VOICE", "true")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "dummy-key")

    with patch("app.services.voice.ElevenLabs") as mock_eleven:
        mock_instance = MagicMock()
        mock_instance.text_to_speech.convert.side_effect = Exception("Quota exceeded")
        mock_eleven.return_value = mock_instance

        service = VoiceService()
        # Must NOT raise an exception
        service.speak("This should fail safely.")
