"""Main CLI entry point for GitHub Wizard."""

import click
from rich.console import Console
from gh_wizard.utils.logger import setup_logger
from gh_wizard.ui.dashboard import show_dashboard
from gh_wizard.session import SessionManager

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


@session.command()
@click.argument("name", required=True)
def start(name: str):
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
        raise click.Exit(1)


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
        raise click.Exit(1)


@session.command()
def pause():
    """Pause current session and save context."""
    try:
        manager = SessionManager()
        manager.pause()
        console.print("[yellow]⏸️  Session paused[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error pausing session: {e}[/red]")
        raise click.Exit(1)


@session.command()
def list():
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
        raise click.Exit(1)


@app.command()
def dashboard():
    """Show dashboard with all repo status."""
    try:
        show_dashboard()
    except Exception as e:
        console.print(f"[red]❌ Error loading dashboard: {e}[/red]")
        raise click.Exit(1)


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
        raise click.Exit(1)


@app.command()
@click.option('--repo', help='Filter by repository')
@click.option('--priority', type=click.Choice(['urgent', 'important', 'normal', 'low']), help='Filter by priority')
def status(repo: str, priority: str):
    """Show current GitHub status with smart filtering."""
    try:
        console.print("[bold]📊 GitHub Status[/bold]")
        console.print("[yellow]Coming in Phase 2[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Exit(1)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
