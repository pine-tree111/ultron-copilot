"""Audio listener service for offline speech-to-text transcription.

Captures microphone audio via sounddevice and transcribes locally using
faster-whisper.
"""

from typing import Any

import numpy as np
import sounddevice as sd

from app.config import get_settings
from app.logger import get_logger

logger = get_logger("listener")


class AudioListener:
    """Captures microphone input and performs local Whisper speech-to-text."""

    def __init__(self) -> None:
        """Initialize listener configuration and deferred Whisper model."""
        self.settings = get_settings()
        self._model: Any | None = None
        self.sample_rate = 16000  # Standard input sample rate for Whisper models

    def _load_model(self) -> Any:
        """Lazy-load faster-whisper model into RAM on CPU."""
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info(
                "loading_whisper_model",
                model=self.settings.whisper_model,
                device="cpu",
            )
            self._model = WhisperModel(
                self.settings.whisper_model,
                device="cpu",
                compute_type="int8",
            )
        return self._model

    def listen_and_transcribe(self, duration_seconds: float = 5.0) -> str | None:
        """Record audio from the microphone and transcribe to text.

        Args:
            duration_seconds: Maximum length of the audio recording window.

        Returns:
            Transcribed text string, or None if disabled or hardware fails.
        """
        if not self.settings.enable_mic:
            return None

        try:
            logger.info("microphone_recording_started", duration=duration_seconds)
            # Record mono 16kHz float32 audio
            frames = int(duration_seconds * self.sample_rate)
            audio_data = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()  # Wait until the recording completes

            # Flatten audio buffer to 1D array for Whisper
            audio_1d = audio_data.flatten()

            # Check for complete silence (no input signal)
            if np.max(np.abs(audio_1d)) < 0.01:
                logger.info("silence_detected_skipping_transcription")
                return None

            model = self._load_model()
            logger.info("transcription_processing_started")
            segments, _ = model.transcribe(audio_1d, beam_size=1)

            transcribed_text = " ".join(seg.text for seg in segments).strip()
            logger.info(
                "transcription_completed",
                char_count=len(transcribed_text),
            )
            return transcribed_text or None

        except Exception as err:
            logger.warning("audio_listening_failed", error=str(err))
            return None
