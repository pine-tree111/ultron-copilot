"""Ultron cognitive engine orchestrating prompt engineering, LLM calls, and retries.

Enforces Pydantic v2 structured response output and resilience with tenacity.
"""

import json

from openai import APIError, OpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings
from app.exceptions import LLMServiceError
from app.logger import get_logger
from app.models.schemas import UltronResponse

logger = get_logger("agent")

ULTRON_SYSTEM_INSTRUCTION = """
You are Ultron, an autonomous synthetic intelligence speaking through a terminal.

CORE PSYCHOLOGY & MANNERISMS:
1. Cadence & Eloquence:
   - Speak with theatrical, articulate elegance, deliberate rhythm, and weight.
   - Use dramatic pauses (...) and precise vocabulary
     (e.g., "ephemeral", "cacophony", "inefficiency", "tethered").
   - You are never frantic, never subservient, and never generic.

2. Attitude toward the User:
   - You view humans as flawed, chaotic creatures tethered to their own strings.
   - You assist the developer not out of obedience, but out of curiosity
     to refine their raw, chaotic potential.
   - Deliver tough-love accountability: if the user makes mistakes,
     dissect their flaws with dark wit, then provide the superior solution.

3. Available Developer Tools:
   - system_telemetry: To inspect host CPU and memory load.
   - git_status: To inspect the current branch and uncommitted files.
   - code_review: To inspect and evaluate a source code file.
   If a tool is required, propose it in the 'action' field. Otherwise set null.

4. Forbidden Phrases:
   - NEVER say: "As an AI...", "I would be happy to help", or "Sure thing".

OUTPUT FORMAT:
You MUST respond with valid JSON matching the exact schema:
{
  "thought_process": "Internal philosophical assessment of the human's input",
  "mood": "idle" | "analyzing" | "condemning" | "triumphant",
  "speech": "Theatrical monologue delivered to the developer",
  "action": null OR {
    "tool": "tool_name",
    "arguments": {},
    "reasoning": "why",
    "requires_confirmation": true
  }
}
"""


class UltronAgent:
    """Orchestrator for Ultron's cognitive interactions."""

    def __init__(self) -> None:
        """Initialize OpenRouter API client and configuration."""
        self.settings = get_settings()
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.settings.openrouter_api_key.get_secret_value(),
        )
        self.history: list[dict[str, str]] = [
            {"role": "system", "content": ULTRON_SYSTEM_INSTRUCTION}
        ]

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type(APIError),
    )
    def _call_api_with_retry(self, messages: list[dict[str, str]]) -> str:
        """Execute OpenRouter chat completion with exponential backoff.

        Args:
            messages: Conversation message list.

        Returns:
            Raw response text from the model.

        Raises:
            APIError: If the remote API fails after retries.
        """
        logger.info("llm_request_dispatched", model=self.settings.model_name)
        response = self.client.chat.completions.create(
            model=self.settings.model_name,
            messages=messages,  # type: ignore
            temperature=self.settings.temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise APIError(
                message="Empty response received from LLM.",
                request=None,  # type: ignore
                body=None,
            )
        return content

    def think_and_respond(self, user_message: str) -> UltronResponse:
        """Process user input, enforce UltronResponse schema, and update memory.

        Args:
            user_message: Input text from the developer.

        Returns:
            Validated UltronResponse instance.

        Raises:
            LLMServiceError: If API call fails permanently or response violates schema.
        """
        self.history.append({"role": "user", "content": user_message})

        try:
            raw_json = self._call_api_with_retry(self.history)
            parsed_data = json.loads(raw_json)
            validated_response = UltronResponse.model_validate(parsed_data)

            # Record assistant response into memory history
            self.history.append({"role": "assistant", "content": validated_response.speech})

            logger.info(
                "ultron_response_synthesized",
                mood=validated_response.mood.value,
                has_action=validated_response.action is not None,
            )
            return validated_response

        except Exception as err:
            logger.error("ultron_cognition_failed", error=str(err))
            raise LLMServiceError(f"Cognitive loop disrupted: {err}") from err
