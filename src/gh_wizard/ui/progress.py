"""Progress tracking UI components."""

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.console import Console

console = Console()


def create_task_progress():
    """Create a task progress indicator."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )
