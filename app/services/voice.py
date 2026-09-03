"""ElevenLabs neural audio synthesis and playback service.

Streams audio from ElevenLabs and plays directly on Linux with graceful error fallback.
"""

from elevenlabs import play
from elevenlabs.client import ElevenLabs

from app.config import get_settings
from app.logger import get_logger

logger = get_logger("voice")


class VoiceService:
  """Manages text-to-speech synthesis and speaker playback."""

  def __init__(self) -> None:
    """Initialize settings and ElevenLabs client if enabled."""
    self.settings = get_settings()
    self._client: ElevenLabs | None = None

    if self.settings.enable_voice and self.settings.elevenlabs_api_key:
      try:
        self._client = ElevenLabs(
            api_key=self.settings.elevenlabs_api_key.get_secret_value()
        )
      except Exception as err:
        logger.warning("voice_client_init_failed", error=str(err))

  def speak(self, text: str) -> None:
    """Convert text to speech and play aloud if voice is enabled.

    Args:
        text: Spoken content to synthesize.
    """
    if not self.settings.enable_voice:
      return

    if not self._client or not self.settings.elevenlabs_api_key:
      logger.warning(
          "voice_disabled_missing_credentials",
          hint="Set ELEVENLABS_API_KEY in .env or set ENABLE_VOICE=false",
      )
      return

    try:
      logger.info("voice_synthesis_started", char_count=len(text))
      audio_stream = self._client.text_to_speech.convert(
          voice_id=self.settings.elevenlabs_voice_id,
          text=text,
          model_id="eleven_turbo_v2_5",
      )

      # Native play without pygame
      play(audio_stream)
      logger.info("voice_playback_completed")

    except Exception as err:
      logger.error("voice_playback_failed", error=str(err))
      # Graceful fallback: never crash the assistant if audio fails
