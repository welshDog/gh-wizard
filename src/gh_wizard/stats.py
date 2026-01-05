"""Statistics tracking for user sessions."""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)


class DailyStats(BaseModel):
    """Stats for a single day."""
    date: str  # ISO format YYYY-MM-DD
    work_sessions: int = 0
    work_minutes: int = 0
    breaks_taken: int = 0
    longest_focus: int = 0  # minutes
    tasks_completed: int = 0


class StatsManager:
    """Manage usage statistics."""

    def __init__(self, stats_file: Optional[Path] = None):
        """Initialize stats manager.
        
        Args:
            stats_file: Path to stats file. Defaults to ~/.ghwizard/stats.json
        """
        if stats_file is None:
            stats_file = Path.home() / ".ghwizard" / "stats.json"
        
        self.stats_file = stats_file
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, DailyStats]:
        """Load stats from file."""
        if not self.stats_file.exists():
            return {}
        
        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {k: DailyStats(**v) for k, v in data.items()}
        except Exception as e:
            logger.error("Error loading stats: %s", e)
            return {}

    def save(self) -> None:
        """Save stats to file."""
        try:
            data = {k: v.model_dump() for k, v in self.stats.items()}
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Error saving stats: %s", e)

    def get_today_stats(self) -> DailyStats:
        """Get stats for today."""
        today = date.today().isoformat()
        if today not in self.stats:
            self.stats[today] = DailyStats(date=today)
        return self.stats[today]

    def record_work_session(self, minutes: int) -> None:
        """Record a completed work session."""
        stats = self.get_today_stats()
        stats.work_sessions += 1
        stats.work_minutes += minutes
        if minutes > stats.longest_focus:
            stats.longest_focus = minutes
        self.save()
        logger.info("Recorded work session: %s min", minutes)

    def record_break(self) -> None:
        """Record a break taken."""
        stats = self.get_today_stats()
        stats.breaks_taken += 1
        self.save()
        logger.info("Recorded break")

    def record_task_completion(self) -> None:
        """Record a task completion."""
        stats = self.get_today_stats()
        stats.tasks_completed += 1
        self.save()
        logger.info("Recorded task completion")
