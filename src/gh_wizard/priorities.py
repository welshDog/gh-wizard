"""Eisenhower Matrix for task prioritization."""

from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()


class Priority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"  # Urgent + Important
    HIGH = "high"  # Important, not urgent
    NORMAL = "normal"  # Urgent, not important
    LOW = "low"  # Neither urgent nor important


class Quadrant(str, Enum):
    """Eisenhower Matrix quadrants."""
    Q1 = "q1"  # Urgent & Important - DO FIRST
    Q2 = "q2"  # Not Urgent & Important - SCHEDULE
    Q3 = "q3"  # Urgent & Not Important - DELEGATE
    Q4 = "q4"  # Not Urgent & Not Important - ELIMINATE


class Task(BaseModel):
    """Task with priority matrix information."""
    id: str
    title: str
    description: str = ""
    is_urgent: bool = False
    is_important: bool = False
    repo: str = ""
    issue_number: int = 0
    estimated_time: int = 0  # minutes
    completed: bool = False

    def get_quadrant(self) -> Quadrant:
        """Determine task quadrant.
        
        Returns:
            Quadrant enum value
        """
        if self.is_urgent and self.is_important:
            return Quadrant.Q1
        elif not self.is_urgent and self.is_important:
            return Quadrant.Q2
        elif self.is_urgent and not self.is_important:
            return Quadrant.Q3
        else:
            return Quadrant.Q4

    def get_priority(self) -> Priority:
        """Get priority level.
        
        Returns:
            Priority enum value
        """
        quadrant = self.get_quadrant()
        if quadrant == Quadrant.Q1:
            return Priority.CRITICAL
        elif quadrant == Quadrant.Q2:
            return Priority.HIGH
        elif quadrant == Quadrant.Q3:
            return Priority.NORMAL
        else:
            return Priority.LOW


class EisenhowerMatrix:
    """Manage tasks using Eisenhower Matrix prioritization."""

    def __init__(self):
        """Initialize Eisenhower Matrix."""
        self.tasks: Dict[str, Task] = {}
        self.quadrants: Dict[Quadrant, List[str]] = {
            Quadrant.Q1: [],
            Quadrant.Q2: [],
            Quadrant.Q3: [],
            Quadrant.Q4: [],
        }

    def add_task(self, task: Task) -> None:
        """Add task to matrix.
        
        Args:
            task: Task to add
        """
        self.tasks[task.id] = task
        quadrant = task.get_quadrant()
        self.quadrants[quadrant].append(task.id)
        logger.info(f"Task added to {quadrant.value}: {task.title}")

    def get_quadrant_tasks(self, quadrant: Quadrant) -> List[Task]:
        """Get all tasks in a quadrant.
        
        Args:
            quadrant: Quadrant enum value
            
        Returns:
            List of tasks in quadrant
        """
        task_ids = self.quadrants[quadrant]
        return [self.tasks[tid] for tid in task_ids if not self.tasks[tid].completed]

    def get_priority_tasks(self) -> List[Task]:
        """Get all tasks sorted by priority.
        
        Returns:
            Tasks sorted from critical to low priority
        """
        all_tasks = list(self.tasks.values())
        priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.NORMAL: 2, Priority.LOW: 3}
        all_tasks.sort(key=lambda t: priority_order[t.get_priority()])
        return [t for t in all_tasks if not t.completed]

    def mark_complete(self, task_id: str) -> None:
        """Mark task as complete.
        
        Args:
            task_id: Task identifier
        """
        if task_id in self.tasks:
            self.tasks[task_id].completed = True
            quadrant = self.tasks[task_id].get_quadrant()
            if task_id in self.quadrants[quadrant]:
                self.quadrants[quadrant].remove(task_id)
            logger.info(f"Task completed: {task_id}")

    def render_matrix(self) -> Panel:
        """Render Eisenhower Matrix visualization.
        
        Returns:
            Rich Panel with matrix
        """
        q1_tasks = self.get_quadrant_tasks(Quadrant.Q1)
        q2_tasks = self.get_quadrant_tasks(Quadrant.Q2)
        q3_tasks = self.get_quadrant_tasks(Quadrant.Q3)
        q4_tasks = self.get_quadrant_tasks(Quadrant.Q4)
        
        # Create matrix display
        content = f"""
[bold red]Q1: DO FIRST[/bold red]              [bold green]Q2: SCHEDULE[/bold green]
Urgent + Important         Not Urgent + Important
{self._format_quadrant(q1_tasks)}    {self._format_quadrant(q2_tasks)}

[bold yellow]Q3: DELEGATE[/bold yellow]          [bold dim]Q4: ELIMINATE[/bold dim]
Urgent + Not Important     Not Urgent + Not Important
{self._format_quadrant(q3_tasks)}    {self._format_quadrant(q4_tasks)}
"""
        
        return Panel(
            content,
            title="📊 Eisenhower Matrix",
            border_style="blue",
            expand=False,
        )

    def render_priority_list(self) -> Table:
        """Render priority-sorted task list.
        
        Returns:
            Rich Table with prioritized tasks
        """
        table = Table(title="🎯 Priority Task List")
        table.add_column("Priority", style="magenta", width=10)
        table.add_column("Title", style="cyan")
        table.add_column("Time (min)", justify="right")
        table.add_column("Quadrant")
        
        for task in self.get_priority_tasks():
            priority = task.get_priority()
            quadrant = task.get_quadrant()
            
            # Color code by priority
            priority_str = priority.value
            if priority == Priority.CRITICAL:
                priority_str = f"[red]{priority_str}[/red]"
            elif priority == Priority.HIGH:
                priority_str = f"[green]{priority_str}[/green]"
            elif priority == Priority.NORMAL:
                priority_str = f"[yellow]{priority_str}[/yellow]"
            
            table.add_row(
                priority_str,
                task.title,
                str(task.estimated_time),
                quadrant.value,
            )
        
        return table

    def _format_quadrant(self, tasks: List[Task]) -> str:
        """Format tasks for quadrant display.
        
        Args:
            tasks: List of tasks
            
        Returns:
            Formatted task list
        """
        if not tasks:
            return "(none)"
        
        lines = []
        for task in tasks[:3]:  # Show max 3 per quadrant
            lines.append(f"• {task.title}")
        
        if len(tasks) > 3:
            lines.append(f"+ {len(tasks) - 3} more")
        
        return "\n".join(lines)
