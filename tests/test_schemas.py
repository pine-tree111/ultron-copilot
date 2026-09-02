"""Unit tests verifying Pydantic v2 domain schemas and persona validation."""

import pytest
from pydantic import ValidationError

from app.models.schemas import ToolCallRequest, ToolName, UltronMood, UltronResponse


def test_valid_ultron_response_creation() -> None:
    """Verify that a valid UltronResponse parses cleanly with defaults."""
    payload = {
        "thought_process": "The developer is attempting to optimize too early.",
        "mood": "condemning",
        "speech": "You build monuments to efficiency before laying the foundation...",
    }
    response = UltronResponse(**payload)

    assert response.mood == UltronMood.CONDEMNING
    assert "monuments" in response.speech
    assert response.action is None


def test_speech_validator_rejects_generic_platitudes() -> None:
    """Verify that generic chatbot phrases are rejected by the persona validator."""
    with pytest.raises(ValidationError) as exc_info:
        UltronResponse(
            thought_process="Compliant response",
            speech="As an AI language model, I would be happy to help!",
            mood=UltronMood.IDLE,
        )

    assert "Ultron persona breach" in str(exc_info.value)


def test_tool_call_request_validation() -> None:
    """Verify that ToolCallRequest enforces valid ToolName enums."""
    valid_tool = ToolCallRequest(
        tool=ToolName.GIT_STATUS,
        reasoning="Inspect developer changes.",
    )
    assert valid_tool.requires_confirmation is True

    # Test that an invented tool name fails validation
    with pytest.raises(ValidationError):
        ToolCallRequest(
            tool="unauthorized_destroy_command",  # type: ignore
            reasoning="Will fail",
        )
