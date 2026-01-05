"""Dashboard renderer."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from gh_wizard.github_api import GitHubAPIClient
from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()


def show_dashboard() -> None:
    """Display the main dashboard."""
    try:
        client = GitHubAPIClient()
        
        # Get repos status
        data = client.get_repos_status()
        
        if "viewer" not in data or "repositories" not in data["viewer"]:
            console.print("[red]Failed to fetch repositories[/red]")
            return
        
        repos = data["viewer"]["repositories"]["nodes"]
        
        # Create table
        table = Table(title="📊 Your Repositories")
        table.add_column("Repository", style="cyan")
        table.add_column("Issues", justify="right", style="yellow")
        table.add_column("Pull Requests", justify="right", style="green")
        table.add_column("Branch", style="magenta")
        
        for repo in repos:
            issues = repo["issues"]["totalCount"]
            prs = repo["pullRequests"]["totalCount"]
            branch = repo["defaultBranchRef"]["name"] if repo["defaultBranchRef"] else "N/A"
            
            table.add_row(
                repo["name"],
                str(issues),
                str(prs),
                branch,
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error loading dashboard: {e}[/red]")
        logger.error(f"Dashboard error: {e}")
