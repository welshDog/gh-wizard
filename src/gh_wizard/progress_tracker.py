"""Visual progress tracking with Rich UI components."""

from typing import Optional, List, Dict, Any
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from gh_wizard.pomodoro import PomodoroSession
from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()


class ProgressDisplay:
    """Display progress with Rich components."""

    def __init__(self):
        """Initialize progress display."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TimeRemainingColumn(),
        )

    def render_pomodoro_display(self, session: PomodoroSession) -> Panel:
        """Render Pomodoro session display.
        
        Returns:
            Rich Panel with session info
        """
        remaining = session.format_time()
        progress = session.get_progress_percentage()
        
        # Create progress bar manually
        bar_width = 40
        filled = int((progress / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Determine color based on phase
        color = "green" if session.current_phase == "work" else "blue"
        phase_emoji = "💼" if session.current_phase == "work" else "☕"
        
        content = f"""
{phase_emoji} {session.current_phase.upper()}

[bold {color}]{remaining}[/bold {color}]
{bar}
{progress:.1f}%

[dim]Sessions completed: {session.completed_sessions}[/dim]
"""
        
        return Panel(
            content,
            title="⏱️ Pomodoro Session",
            border_style=color,
            expand=False,
        )

    def render_task_progress(self, task_name: str, steps_completed: int, total_steps: int) -> Panel:
        """Render task progress display.
        
        Args:
            task_name: Name of the task
            steps_completed: Number of completed steps
            total_steps: Total number of steps
            
        Returns:
            Rich Panel with task progress
        """
        progress_pct = (steps_completed / total_steps * 100) if total_steps > 0 else 0
        bar_width = 40
        filled = int((progress_pct / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        content = f"""
[bold cyan]{task_name}[/bold cyan]

{bar}
{steps_completed}/{total_steps} steps
{progress_pct:.1f}% complete
"""
        
        return Panel(
            content,
            title="📋 Task Progress",
            border_style="cyan",
            expand=False,
        )

    def render_session_stats(self, session: PomodoroSession) -> Table:
        """Render session statistics table.
        
        Args:
            session: Pomodoro session instance
            
        Returns:
            Rich Table with stats
        """
        table = Table(title="📊 Session Stats")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Sessions Completed", str(session.completed_sessions))
        table.add_row("Total Work Time", f"{(session.completed_sessions * session.work_minutes)} min")
        table.add_row("Elapsed", session.format_time(session.get_elapsed_seconds()))
        table.add_row("Remaining", session.format_time())
        table.add_row(
            "Status",
            "🟢 Running" if session.is_running else "🔴 Stopped",
        )
        
        return table


class MultiTaskProgress:
    """Track progress of multiple tasks simultaneously."""

    def __init__(self):
        """Initialize multi-task progress tracker."""
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def add_task(
        self,
        task_id: str,
        name: str,
        total_steps: int,
        description: str = "",
    ) -> None:
        """Add a task to track.
        
        Args:
            task_id: Unique task identifier
            name: Display name
            total_steps: Total number of steps
            description: Optional description
        """
        self.tasks[task_id] = {
            "name": name,
            "description": description,
            "total_steps": total_steps,
            "completed_steps": 0,
            "status": "in_progress",
        }
        logger.info(f"Task added: {task_id}")

    def update_task(self, task_id: str, steps_completed: int) -> None:
        """Update task progress.
        
        Args:
            task_id: Task identifier
            steps_completed: Number of steps completed
        """
        if task_id in self.tasks:
            self.tasks[task_id]["completed_steps"] = min(
                steps_completed,
                self.tasks[task_id]["total_steps"],
            )
            
            # Check if complete
            if (
                self.tasks[task_id]["completed_steps"]
                >= self.tasks[task_id]["total_steps"]
            ):
                self.tasks[task_id]["status"] = "complete"
                logger.info(f"Task completed: {task_id}")

    def get_overall_progress(self) -> float:
        """Get overall progress across all tasks.
        
        Returns:
            Overall completion percentage (0-100)
        """
        if not self.tasks:
            return 0
        
        total_steps = sum(t["total_steps"] for t in self.tasks.values())
        completed_steps = sum(t["completed_steps"] for t in self.tasks.values())
        
        if total_steps == 0:
            return 0
        
        return (completed_steps / total_steps) * 100

    def render_overview(self) -> Table:
        """Render overview of all tasks.
        
        Returns:
            Rich Table showing all tasks
        """
        table = Table(title="📈 Tasks Overview")
        table.add_column("Task", style="cyan")
        table.add_column("Progress", justify="right")
        table.add_column("Status", justify="center")
        
        for task_id, task in self.tasks.items():
            completed = task["completed_steps"]
            total = task["total_steps"]
            progress = f"{completed}/{total}"
            status = "✅" if task["status"] == "complete" else "⏳"
            
            table.add_row(task["name"], progress, status)
        
        overall = self.get_overall_progress()
        table.add_row(
            "[bold]Overall[/bold]",
            f"[bold]{overall:.1f}%[/bold]",
            "[bold]→[/bold]",
        )
        
        return table
