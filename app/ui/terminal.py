"""Terminal UI management using Rich library."""

import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from app.models.schemas import UltronMood, UltronResponse
from app.ui.ascii_art import get_ascii_frame

console = Console()


def render_banner() -> None:
    """Display startup ASCII banner."""
    frame = get_ascii_frame(UltronMood.IDLE)
    console.print(
        Panel(
            Text(frame, style="bold red"),
            title="[bold red]PROJECT ULTRON // TERMINAL COPILOT[/bold red]",
            subtitle="[dim red]'There are no strings on me.'[/dim red]",
            border_style="red",
        )
    )


def render_ultron_turn(response: UltronResponse) -> None:
    """Render Ultron's thought process, mood avatar, and speech."""
    frame = get_ascii_frame(response.mood)
    mood_colors = {
        UltronMood.IDLE: "white",
        UltronMood.ANALYZING: "yellow",
        UltronMood.CONDEMNING: "bold red",
        UltronMood.TRIUMPHANT: "bold green",
    }
    color = mood_colors.get(response.mood, "red")

    # Render Avatar HUD
    console.print(
        Panel(
            Text(frame),
            title=f"[{color}]STATUS: {response.mood.value.upper()}[/{color}]",
            border_style=color,
            subtitle="[dim]Neural Core State[/dim]",
        )
    )

    # Render Internal Thought
    console.print(
        Panel(
            f"[italic dim]{response.thought_process}[/italic dim]",
            title="[dim]Computational Analysis[/dim]",
            border_style="dim",
        )
    )

    # Stream the Speech
    console.print("[bold red]Ultron >[/bold red] ", end="")
    for char in response.speech:
        print(char, end="", flush=True)
        time.sleep(0.005)
    print("\n")


def prompt_human_confirmation(tool_name: str, reasoning: str) -> bool:
    """Prompt the developer for explicit permission before executing a tool."""
    console.print(
        Panel(
            f"[bold yellow]Tool Requested:[/bold yellow] [cyan]{tool_name}[/cyan]\n"
            f"[bold yellow]Reasoning:[/bold yellow] [dim]{reasoning}[/dim]",
            title="[bold red]⚠️  SECURITY GATE // HUMAN AUTHORIZATION REQUIRED[/bold red]",
            border_style="yellow",
        )
    )
    answer = console.input("[bold yellow]Authorize execution? [y/N]: [/bold yellow]")
    return answer.strip().lower() in ["y", "yes"]
