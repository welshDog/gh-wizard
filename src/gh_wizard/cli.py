"""Main CLI entry point for GitHub Wizard."""

import click
import time
import msvcrt
import sys
from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt, Confirm

from gh_wizard.utils.logger import setup_logger
from gh_wizard.ui.dashboard import show_dashboard
from gh_wizard.session import SessionManager
from gh_wizard.pomodoro import PomodoroSession, notify_phase_complete, BreakReminder
from gh_wizard.progress_tracker import ProgressDisplay
from gh_wizard.priorities import EisenhowerMatrix, Task
from gh_wizard.stats import StatsManager

console = Console()
logger = setup_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def app():
    """🧙 GitHub Wizard - Terminal UI for managing GitHub projects."""
    pass


@app.group()
def session():
    """Manage your hyperfocus sessions."""
    pass


@session.command(name="start")
@click.argument("name", required=True)
def start_session(name: str):
    """Start a new hyperfocus session.
    
    Example:
        gh wizard session start "HyperCode feature work"
    """
    try:
        manager = SessionManager()
        session_id = manager.start(name)
        console.print(f"[green]✨ Session started: {name}[/green]")
        console.print(f"[dim]Session ID: {session_id}[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Error starting session: {e}[/red]")
        sys.exit(1)


@session.command()
def resume():
    """Resume your last hyperfocus session."""
    try:
        manager = SessionManager()
        session = manager.get_last_session()
        if session:
            manager.resume(session["session_id"])
            console.print(f"[green]✨ Resumed: {session['name']}[/green]")
            console.print(f"[dim]Last worked: {session['last_active']}[/dim]")
        else:
            console.print("[yellow]No previous sessions found[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error resuming session: {e}[/red]")
        raise click.exceptions.Exit(1)


@session.command()
def pause():
    """Pause current session and save context."""
    try:
        manager = SessionManager()
        manager.pause()
        console.print("[yellow]⏸️  Session paused[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error pausing session: {e}[/red]")
        raise click.exceptions.Exit(1)


@session.command(name="list")
def list_sessions_command():
    """List all saved sessions."""
    try:
        manager = SessionManager()
        sessions = manager.list_sessions()
        if sessions:
            console.print("[bold]📝 Your Sessions[/bold]")
            for i, s in enumerate(sessions, 1):
                console.print(f"  {i}. {s['name']} (ID: {s['session_id']})")
        else:
            console.print("[yellow]No sessions found[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error listing sessions: {e}[/red]")
        sys.exit(1)


@app.command()
def dashboard():
    """Show dashboard with all repo status."""
    try:
        show_dashboard()
    except Exception as e:
        console.print(f"[red]❌ Error loading dashboard: {e}[/red]")
        raise click.exceptions.Exit(1)


@app.command()
def stats():
    """Show daily session statistics."""
    try:
        manager = StatsManager()
        stats = manager.get_today_stats()
        
        console.print(f"[bold]📊 Today's Stats ({stats.date})[/bold]")
        console.print(f"  💼 Work Sessions: [green]{stats.work_sessions}[/green] ({stats.work_minutes} min)")
        console.print(f"  ☕ Breaks Taken: [blue]{stats.breaks_taken}[/blue]")
        console.print(f"  🔥 Longest Focus: [yellow]{stats.longest_focus} min[/yellow]")
        console.print(f"  ✅ Tasks Completed: [cyan]{stats.tasks_completed}[/cyan]")
    except Exception as e:
        console.print(f"[red]❌ Error loading stats: {e}[/red]")
        raise click.exceptions.Exit(1)


@app.command()
@click.argument("task", required=True)
def break_down(task: str):
    """Break down a complex task into steps.
    
    Example:
        gh wizard break "Release HyperCode v2.0"
    """
    try:
        from gh_wizard.tasks import TaskBreakdown
        breakdown = TaskBreakdown()
        steps = breakdown.breakdown(task)
        console.print(f"[bold]📋 Task Breakdown: {task}[/bold]\n")
        for i, step in enumerate(steps, 1):
            console.print(f"  {i}. {step['name']}")
            console.print(f"     ⏱️  ~{step['time_estimate']} min")
            console.print(f"     {step['description']}\n")
    except Exception as e:
        console.print(f"[red]❌ Error breaking down task: {e}[/red]")
        sys.exit(1)


@app.command()
@click.option('--repo', help='Filter by repository')
@click.option('--priority', type=click.Choice(['urgent', 'important', 'normal', 'low']), help='Filter by priority')
def status(repo: str, priority: str):
    """Show current GitHub status with smart filtering."""
    try:
        console.print("[bold]📊 GitHub Status[/bold]")
        if repo:
            console.print(f"Filter: Repo={repo}")
        if priority:
            console.print(f"Filter: Priority={priority}")
        console.print("[yellow]Coming in Phase 2[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.exceptions.Exit(1)


@app.group()
def pomodoro():
    """🍅 Pomodoro Timer - Focus & Break management."""


@pomodoro.command(name="start")
@click.option("--work", default=25, help="Work duration in minutes")
@click.option("--short", default=5, help="Short break duration in minutes")
@click.option("--long", default=15, help="Long break duration in minutes")
def start_pomodoro(work: int, short: int, long: int):
    """Start the Pomodoro timer.
    
    Controls:
        p: Pause
        r: Resume
        n: Next phase
        s: Stop
    """
    pomodoro_session = PomodoroSession(work_minutes=work, short_break_minutes=short, long_break_minutes=long)
    display = ProgressDisplay()
    stats_manager = StatsManager()
    break_reminder = BreakReminder()
    
    pomodoro_session.start()
    
    console.print("[bold green]🍅 Pomodoro Timer Started![/bold green]")
    console.print("[dim]Press 'p' to pause, 'r' to resume, 'n' to next phase, 's' or Ctrl+C to stop[/dim]")
    
    try:
        with Live(display.render_pomodoro_display(pomodoro_session), refresh_per_second=4) as live:
            while pomodoro_session.is_running:
                # Check for keyboard input
                if msvcrt.kbhit():
                    try:
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'p':
                            pomodoro_session.pause()
                        elif key == 'r':
                            pomodoro_session.resume()
                        elif key == 's':
                            pomodoro_session.stop()
                            break
                        elif key == 'n':
                            # Record stats before switching if completing work
                            if pomodoro_session.current_phase == "work":
                                stats_manager.record_work_session(pomodoro_session.work_minutes)
                            else:
                                stats_manager.record_break()
                            pomodoro_session.next_phase()
                            notify_phase_complete(pomodoro_session.current_phase)
                            if pomodoro_session.current_phase != "work":
                                suggestion = break_reminder.get_break_suggestion()
                                console.print(f"\n[bold blue]🎉 Break Time! {suggestion}[/bold blue]")
                    except UnicodeDecodeError:
                        pass
                
                if not pomodoro_session.is_paused:
                    if pomodoro_session.is_phase_complete():
                        # Record stats
                        if pomodoro_session.current_phase == "work":
                            stats_manager.record_work_session(pomodoro_session.work_minutes)
                        else:
                            stats_manager.record_break()
                            
                        pomodoro_session.next_phase()
                        notify_phase_complete(pomodoro_session.current_phase)
                        
                        if pomodoro_session.current_phase != "work":
                            suggestion = break_reminder.get_break_suggestion()
                            console.print(f"\n[bold blue]🎉 Break Time! {suggestion}[/bold blue]")

                live.update(display.render_pomodoro_display(pomodoro_session))
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        pomodoro_session.stop()
        console.print("\n[yellow]Timer stopped.[/yellow]")


@pomodoro.command(name="work-on")
@click.argument("task_id", required=True)
@click.option("--work", default=25, help="Work duration in minutes")
def work_on_task(task_id: str, work: int):
    """Start a Pomodoro session for a specific task."""
    try:
        matrix = EisenhowerMatrix()
        matrix.load()
        
        # Find task
        found_task = None
        found_id = None
        if task_id in matrix.tasks:
            found_id = task_id
            found_task = matrix.tasks[task_id]
        else:
            for tid, t in matrix.tasks.items():
                if task_id.lower() in t.title.lower():
                    found_id = tid
                    found_task = t
                    break
        
        if not found_task:
            console.print(f"[red]❌ Task '{task_id}' not found.[/red]")
            return
            
        console.print(f"[bold green]🎯 Working on: {found_task.title}[/bold green]")
        
        # Start timer with task context
        pomodoro_session = PomodoroSession(work_minutes=work)
        display = ProgressDisplay()
        stats_manager = StatsManager()
        break_reminder = BreakReminder()
        
        pomodoro_session.start()
        
        console.print("[dim]Press 'p' to pause, 'r' to resume, 'n' to next phase, 's' or Ctrl+C to stop[/dim]")
        
        try:
            with Live(display.render_pomodoro_display(pomodoro_session, task_title=found_task.title), refresh_per_second=4) as live:
                while pomodoro_session.is_running:
                    if msvcrt.kbhit():
                        try:
                            key = msvcrt.getch().decode('utf-8').lower()
                            if key == 'p': pomodoro_session.pause()
                            elif key == 'r': pomodoro_session.resume()
                            elif key == 's': 
                                pomodoro_session.stop()
                                break
                            elif key == 'n':
                                if pomodoro_session.current_phase == "work":
                                    stats_manager.record_work_session(pomodoro_session.work_minutes)
                                else:
                                    stats_manager.record_break()
                                pomodoro_session.next_phase()
                                notify_phase_complete(pomodoro_session.current_phase)
                                if pomodoro_session.current_phase != "work":
                                    suggestion = break_reminder.get_break_suggestion(pomodoro_session.completed_sessions)
                                    console.print(f"\n[bold blue]🎉 Break Time! {suggestion}[/bold blue]")
                        except UnicodeDecodeError:
                            pass
                    
                    if not pomodoro_session.is_paused and pomodoro_session.is_phase_complete():
                        if pomodoro_session.current_phase == "work":
                            stats_manager.record_work_session(pomodoro_session.work_minutes)
                        else:
                            stats_manager.record_break()
                        
                        pomodoro_session.next_phase()
                        notify_phase_complete(pomodoro_session.current_phase)
                        
                        if pomodoro_session.current_phase != "work":
                            suggestion = break_reminder.get_break_suggestion(pomodoro_session.completed_sessions)
                            console.print(f"\n[bold blue]🎉 Break Time! {suggestion}[/bold blue]")
                    
                    live.update(display.render_pomodoro_display(pomodoro_session, task_title=found_task.title))
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            pomodoro_session.stop()
            console.print("\n[yellow]Timer stopped.[/yellow]")
            
        # Ask to complete task
        if Confirm.ask(f"Did you complete '{found_task.title}'?"):
            if found_id:
                matrix.mark_complete(found_id)
            matrix.save()
            stats_manager.record_task_completion()
            console.print("[green]✅ Task completed![/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@pomodoro.command(name="complete-task")
@click.argument("task_id", required=True)
def complete_pomodoro_task(task_id: str):
    """Complete a task from the matrix and record stats."""
    try:
        matrix = EisenhowerMatrix()
        matrix.load()
        stats_manager = StatsManager()
        
        # Reuse search logic or just try direct first
        found_id = None
        if task_id in matrix.tasks:
            found_id = task_id
        else:
            for tid, t in matrix.tasks.items():
                if task_id.lower() in t.title.lower():
                    found_id = tid
                    break
        
        if found_id:
            matrix.mark_complete(found_id)
            matrix.save()
            stats_manager.record_task_completion()
            console.print(f"[green]✅ Task '{matrix.tasks[found_id].title}' completed![/green]")
        else:
            console.print(f"[red]❌ Task '{task_id}' not found.[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error completing task: {e}[/red]")
        sys.exit(1)


@app.group()
def priorities():
    """⚡ Eisenhower Matrix - Task Prioritization."""


@priorities.command(name="add")
def add_task():
    """Add a new task to the matrix."""
    matrix = EisenhowerMatrix()
    matrix.load()
    
    title = Prompt.ask("Task title")
    urgent = Confirm.ask("Is it urgent?")
    important = Confirm.ask("Is it important?")
    estimated = Prompt.ask("Estimated time (min)", default="0")
    
    task = Task(
        id=str(int(time.time())),
        title=title,
        is_urgent=urgent,
        is_important=important,
        estimated_time=int(estimated)
    )
    
    matrix.add_task(task)
    matrix.save()
    console.print(f"[green]Task added to {task.get_quadrant().value}![/green]")


@priorities.command(name="list")
def list_tasks():
    """List tasks by priority."""
    matrix = EisenhowerMatrix()
    matrix.load()
    console.print(matrix.render_priority_list())


@priorities.command(name="matrix")
def show_matrix():
    """Show the Eisenhower Matrix."""
    matrix = EisenhowerMatrix()
    matrix.load()
    matrix.render_matrix()


@priorities.command(name="done")
@click.argument("task_id", required=False)
def complete_task(task_id: str):
    """Mark a task as complete."""
    matrix = EisenhowerMatrix()
    matrix.load()
    
    if not task_id:
        console.print(matrix.render_priority_list())
        task_id = Prompt.ask("Enter Task ID (or title substring)")
        
        found = False
        # Try exact match first
        if task_id in matrix.tasks:
            found = True
        else:
            # Try partial match
            for tid, t in matrix.tasks.items():
                if task_id.lower() in t.title.lower():
                    task_id = tid
                    found = True
                    break
        
        if not found:
            console.print("[red]Task not found.[/red]")
            return

    matrix.mark_complete(task_id)
    matrix.save()
    console.print("[green]Task marked as complete![/green]")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
