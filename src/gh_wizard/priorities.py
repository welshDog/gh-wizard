"""Eisenhower Matrix for task prioritization."""

from typing import List, Dict
from enum import Enum
import json
from pathlib import Path
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
        logger.info("Task added to %s: %s", quadrant.value, task.title)

    def get_quadrant_tasks(self, quadrant: Quadrant) -> List[Task]:
        """Get all tasks in a specific quadrant."""
        task_ids = self.quadrants.get(quadrant, [])
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]

    def save(self, filepath: str = "eisenhower_matrix.json") -> None:
        """Save tasks to JSON file."""
        data = {
            "tasks": {tid: task.model_dump() for tid, task in self.tasks.items()}
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info("Matrix saved to %s", filepath)

    def load(self, filepath: str = "eisenhower_matrix.json") -> None:
        """Load tasks from JSON file."""
        path = Path(filepath)
        if not path.exists():
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.tasks = {}
            self.quadrants = {q: [] for q in Quadrant}
            
            for _, task_data in data.get("tasks", {}).items():
                task = Task(**task_data)
                self.add_task(task)
            
            logger.info("Matrix loaded from %s", filepath)
        except Exception as e:
            logger.error("Error loading matrix: %s", e)

    def get_priority_tasks(self) -> List[Task]:
        """Get all tasks sorted by priority."""
        all_tasks = list(self.tasks.values())
        priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.NORMAL: 2, Priority.LOW: 3}
        all_tasks.sort(key=lambda t: priority_order[t.get_priority()])
        return [t for t in all_tasks if not t.completed]

    def mark_complete(self, task_id: str) -> None:
        """Mark task as complete."""
        if task_id in self.tasks:
            self.tasks[task_id].completed = True
            # We don't remove from quadrants, just mark as complete
            logger.info("Task completed: %s", task_id)

    def render_matrix(self) -> None:
        """Render the Eisenhower Matrix to the console."""
        # Create a 2x2 grid using tables
        
        def create_quadrant_panel(quadrant: Quadrant, title: str, color: str) -> Panel:
            tasks = self.get_quadrant_tasks(quadrant)
            content = ""
            for task in tasks:
                status = "✅" if task.completed else "☐"
                content += f"{status} {task.title}\n"
            if not content:
                content = "[dim]No tasks[/dim]"
            
            return Panel(content, title=f"[{color}]{title}[/{color}]", border_style=color)

        q1 = create_quadrant_panel(Quadrant.Q1, "DO FIRST (Urgent & Important)", "red")
        q2 = create_quadrant_panel(Quadrant.Q2, "SCHEDULE (Not Urgent & Important)", "blue")
        q3 = create_quadrant_panel(Quadrant.Q3, "DELEGATE (Urgent & Not Important)", "yellow")
        q4 = create_quadrant_panel(Quadrant.Q4, "ELIMINATE (Not Urgent & Not Important)", "green")

        # Create a main table to hold the quadrants
        grid = Table.grid(expand=True, padding=1)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        
        grid.add_row(q1, q2)
        grid.add_row(q3, q4)
        
        console.print(Panel(grid, title="⚡ Eisenhower Matrix", border_style="bold white"))

    def render_priority_list(self) -> Table:
        """Render priority-sorted task list."""
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
