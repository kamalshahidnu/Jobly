"""CLI display utilities."""

import click
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import time


console = Console()


def display_success(message: str):
    """Display success message.

    Args:
        message: Success message
    """
    console.print(f"[green]✓[/green] {message}")


def display_error(message: str):
    """Display error message.

    Args:
        message: Error message
    """
    console.print(f"[red]✗[/red] {message}")


def display_info(message: str):
    """Display info message.

    Args:
        message: Info message
    """
    console.print(f"[blue]ℹ[/blue] {message}")


def display_warning(message: str):
    """Display warning message.

    Args:
        message: Warning message
    """
    console.print(f"[yellow]⚠[/yellow] {message}")


def display_table(data: List[Dict[str, Any]], title: str = None):
    """Display data as table.

    Args:
        data: List of dictionaries with data
        title: Optional table title
    """
    if not data:
        display_info("No data to display")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")

    # Add columns from first row
    for key in data[0].keys():
        table.add_column(key, style="cyan")

    # Add rows
    for row in data:
        table.add_row(*[str(v) for v in row.values()])

    console.print(table)


def display_panel(content: str, title: str = None, style: str = "blue"):
    """Display content in a panel.

    Args:
        content: Panel content
        title: Optional panel title
        style: Panel style color
    """
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


def display_job(job: Dict[str, Any]):
    """Display job details.

    Args:
        job: Job data dictionary
    """
    content = f"""
[bold]{job.get('title', 'Unknown')}[/bold]
[cyan]Company:[/cyan] {job.get('company', 'Unknown')}
[cyan]Location:[/cyan] {job.get('location', 'Unknown')}
[cyan]Salary:[/cyan] {job.get('salary', 'Not specified')}
[cyan]Match Score:[/cyan] {job.get('match_score', 0)}/100
[cyan]Posted:[/cyan] {job.get('posted_date', 'Unknown')}
    """
    display_panel(content.strip(), title="Job Details", style="green")


def display_progress(message: str, steps: int = None):
    """Display progress indicator.

    Args:
        message: Progress message
        steps: Optional number of steps
    """
    if steps:
        with console.status(f"[bold green]{message}...") as status:
            # Simple progress animation; real progress hooks can replace this later.
            for idx in range(steps):
                status.update(f"[bold green]{message}... ({idx + 1}/{steps})")
                time.sleep(0.05)
    else:
        console.print(f"[bold green]⏳[/bold green] {message}...")


def confirm(message: str) -> bool:
    """Ask for user confirmation.

    Args:
        message: Confirmation message

    Returns:
        True if confirmed, False otherwise
    """
    return click.confirm(message)
