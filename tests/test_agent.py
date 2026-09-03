"""Unit tests verifying the UltronAgent cognitive engine and tenacity retries."""

from unittest.mock import MagicMock

import pytest

from app.exceptions import LLMServiceError
from app.models.schemas import UltronMood, UltronResponse
from app.services.agent import UltronAgent


def test_agent_initialization() -> None:
    """Verify UltronAgent initializes with system instructions."""
    agent = UltronAgent()
    assert len(agent.history) == 1
    assert agent.history[0]["role"] == "system"


def test_agent_successful_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that agent processes LLM response and validates UltronResponse."""
    agent = UltronAgent()

    mock_json_payload = (
        '{"thought_process": "Developer is asking a question.", '
        '"mood": "analyzing", '
        '"speech": "You seek clarity in a world of static...", '
        '"action": null}'
    )

    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=mock_json_payload))]

    monkeypatch.setattr(
        agent.client.chat.completions,
        "create",
        lambda **kwargs: mock_completion,
    )

    result = agent.think_and_respond("Hello Ultron")

    assert isinstance(result, UltronResponse)
    assert result.mood == UltronMood.ANALYZING
    assert "clarity" in result.speech
    assert len(agent.history) == 3  # system, user, assistant


def test_agent_handles_malformed_llm_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that unparseable JSON from LLM raises LLMServiceError."""
    agent = UltronAgent()

    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Not a JSON string"))]

    monkeypatch.setattr(
        agent.client.chat.completions,
        "create",
        lambda **kwargs: mock_completion,
    )

    with pytest.raises(LLMServiceError):
        agent.think_and_respond("Will fail")
