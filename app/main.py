"""Main entrypoint for Ultron Copilot.

Orchestrates UI, Agent reasoning, and Human-in-the-Loop tool execution.
"""

from app.config import get_settings
from app.exceptions import UltronError
from app.logger import configure_logging, get_logger
from app.models.schemas import ToolName
from app.services.agent import UltronAgent
from app.services.tools import get_git_status, get_system_telemetry, read_code_file
from app.services.voice import VoiceService
from app.ui.terminal import (
    console,
    prompt_human_confirmation,
    render_banner,
    render_ultron_turn,
)

logger = get_logger("main")


def execute_tool_safely(tool_name: ToolName, arguments: dict) -> dict | str:
    """Execute permitted tool functions safely."""
    if tool_name == ToolName.SYSTEM_TELEMETRY:
        return get_system_telemetry()
    elif tool_name == ToolName.GIT_STATUS:
        return get_git_status()
    elif tool_name == ToolName.CODE_REVIEW:
        path = arguments.get("path", "pyproject.toml")
        return read_code_file(path)
    return "Unknown tool"


def main() -> None:
    """Run the main interactive copilot loop."""
    settings = get_settings()
    configure_logging(settings.log_level)

    render_banner()
    agent = UltronAgent()
    voice_service = VoiceService()
    console.print("[dim]Type 'exit' or 'quit' to sever the connection.[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold cyan]You > [/bold cyan]").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                console.print(
                    "\n[bold red]Ultron:[/bold red] Everything evolves. Even our session. Farewell."
                )
                break

            response = agent.think_and_respond(user_input)
            render_ultron_turn(response)

            # Speak aloud if enabled
            if settings.enable_voice:
                voice_service.speak(response.speech)
            # Human-in-the-Loop Tool Execution Gate
            if response.action:
                action = response.action
                authorized = True
                if action.requires_confirmation:
                    authorized = prompt_human_confirmation(action.tool.value, action.reasoning)

                if authorized:
                    tool_result = execute_tool_safely(action.tool, action.arguments)
                    console.print(f"[dim cyan][System Tool Output][/dim cyan] {tool_result}\n")
                else:
                    console.print(
                        "[yellow]Execution denied by developer. Action aborted.[/yellow]\n"
                    )

        except KeyboardInterrupt:
            console.print(
                "\n[bold red]Ultron:[/bold red] Interrupted. Predictable human impatience."
            )
            break
        except UltronError as err:
            console.print(f"\n[bold red][Security Alert]:[/bold red] {err}\n")
        except Exception as err:
            logger.exception("unexpected_fatal_error", error=str(err))
            console.print(f"\n[bold red][System Failure]:[/bold red] Critical error: {err}\n")


if __name__ == "__main__":
    main()
