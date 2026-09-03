"""Domain-specific exception hierarchy for Ultron Copilot."""


class UltronError(Exception):
    """Base exception for all domain errors within Ultron Copilot."""

    pass


class ConfigurationError(UltronError):
    """Raised when environment settings or required secrets fail validation."""

    pass


class SecurityBreachError(UltronError):
    """Raised when a tool attempts path traversal or unauthorized access outside the sandbox."""

    pass


class LLMServiceError(UltronError):
    """Raised when the LLM provider fails permanently after retry backoff."""

    pass


class AudioServiceError(UltronError):
    """Raised when audio synthesis or playback fails."""

    pass
