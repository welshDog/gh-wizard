"""Smart notification management."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel

from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class Notification(BaseModel):
    """Single notification."""
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    repo: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = []


class NotificationManager:
    """Manage and filter notifications intelligently."""

    def __init__(self, dnd_mode: bool = False, watched_repos: Optional[List[str]] = None):
        """Initialize notification manager.
        
        Args:
            dnd_mode: Do Not Disturb mode (silent)
            watched_repos: List of repos to watch. If None, watch all.
        """
        self.dnd_mode = dnd_mode
        self.watched_repos = watched_repos or []
        self.notifications: List[Notification] = []

    def add(self, notification: Notification) -> bool:
        """Add a notification.
        
        Returns:
            True if should be shown, False if filtered
        """
        # Check DND mode
        if self.dnd_mode and notification.priority != NotificationPriority.CRITICAL:
            logger.debug(f"Notification suppressed (DND mode): {notification.title}")
            return False
        
        # Check watched repos
        if self.watched_repos and notification.repo and notification.repo not in self.watched_repos:
            logger.debug(f"Notification filtered (repo not watched): {notification.title}")
            return False
        
        self.notifications.append(notification)
        logger.info(f"Notification added: {notification.title}")
        return True

    def batch_summary(self) -> Optional[str]:
        """Create a summary of all notifications.
        
        Returns:
            Summary text or None if no notifications
        """
        if not self.notifications:
            return None
        
        # Group by priority
        by_priority = {}
        for notif in self.notifications:
            priority = notif.priority.value
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(notif)
        
        summary = []
        for priority in ["critical", "high", "normal", "low"]:
            if priority in by_priority:
                count = len(by_priority[priority])
                summary.append(f"{count} {priority} notification(s)")
        
        return ", ".join(summary)

    def get_by_priority(self, priority: NotificationPriority) -> List[Notification]:
        """Get notifications by priority."""
        return [n for n in self.notifications if n.priority == priority]

    def get_by_repo(self, repo: str) -> List[Notification]:
        """Get notifications for a specific repo."""
        return [n for n in self.notifications if n.repo == repo]

    def clear(self) -> None:
        """Clear all notifications."""
        self.notifications = []
        logger.info("Notifications cleared")
