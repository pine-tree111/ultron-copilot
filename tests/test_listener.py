"""Unit tests verifying AudioListener offline transcription and error resilience."""

from unittest.mock import MagicMock, patch

import numpy as np

from app.config import Settings
from app.services.listener import AudioListener


def test_listener_disabled_by_default() -> None:
    """Verify that listener returns None immediately when enable_mic is false."""
    listener = AudioListener()
    listener.settings = Settings(enable_mic=False)

    # Must return None without touching audio hardware
    result = listener.listen_and_transcribe()
    assert result is None


def test_listener_transcription_successful() -> None:
    """Verify successful audio capture and Whisper transcription parsing."""
    listener = AudioListener()
    listener.settings = Settings(enable_mic=True)

    # Generate 1 second of mock non-silent audio data (shape: [16000, 1])
    mock_audio = np.full((16000, 1), 0.5, dtype=np.float32)

    with (
        patch("sounddevice.rec") as mock_rec,
        patch("sounddevice.wait"),
        patch.object(AudioListener, "_load_model") as mock_load_model,
    ):
        mock_rec.return_value = mock_audio

        # Mock Whisper model transcription output
        mock_model = MagicMock()
        mock_segment = MagicMock(text="Ultron, inspect git status")
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_load_model.return_value = mock_model

        result = listener.listen_and_transcribe(duration_seconds=1.0)
        assert result == "Ultron, inspect git status"


def test_listener_silence_detection_skips_model() -> None:
    """Verify that silence skips Whisper inference to save CPU cycles."""
    listener = AudioListener()
    listener.settings = Settings(enable_mic=True)

    # Pure silence (all zeros)
    mock_silence = np.zeros((16000, 1), dtype=np.float32)

    with (
        patch("sounddevice.rec") as mock_rec,
        patch("sounddevice.wait"),
        patch.object(AudioListener, "_load_model") as mock_load_model,
    ):
        mock_rec.return_value = mock_silence

        result = listener.listen_and_transcribe(duration_seconds=1.0)

        assert result is None
        # Model should NEVER be loaded into memory for silence
        mock_load_model.assert_not_called()


def test_listener_handles_hardware_failure_gracefully() -> None:
    """Verify that audio hardware failure logs a warning and returns None without crashing."""
    listener = AudioListener()
    listener.settings = Settings(enable_mic=True)

    with patch("sounddevice.rec", side_effect=Exception("PortAudio device error")):
        result = listener.listen_and_transcribe()
        assert result is None
