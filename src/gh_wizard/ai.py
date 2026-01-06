"""AI and pattern learning utilities."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
from collections import Counter

from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)


class PatternLearner:
    """Learn patterns from user workflows."""

    def __init__(self, history_file: Optional[Path] = None):
        """Initialize pattern learner.
        
        Args:
            history_file: Path to history file. Defaults to ~/.ghwizard/history.json
        """
        if history_file is None:
            history_file = Path.home() / ".ghwizard" / "history.json"
        
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()

    def record_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Record an action for pattern learning.
        
        Args:
            action_type: Type of action (e.g., 'commit', 'pr_created', 'issue_resolved')
            details: Action details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": action_type,
            "details": details,
        }
        self.history.append(entry)
        self._save_history()
        logger.debug(f"Action recorded: {action_type}")

    def get_common_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Get common patterns from recent history.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary of patterns and frequencies
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for entry in self.history:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if timestamp > cutoff:
                recent.append(entry)
        
        # Count action types
        action_counts = Counter(e["type"] for e in recent)
        
        # Count repos
        repo_counts: Counter[str] = Counter()
        for e in recent:
            if "repo" in e["details"]:
                repo_counts[e["details"]["repo"]] += 1
        
        return {
            "period_days": days,
            "total_actions": len(recent),
            "action_distribution": dict(action_counts.most_common()),
            "repo_distribution": dict(repo_counts.most_common()),
        }

    def suggest_next_steps(self, current_context: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on patterns.
        
        Args:
            current_context: Current work context
            
        Returns:
            List of suggested next steps
        """
        # TODO: Implement ML-based suggestions
        suggestions = [
            "Have you written tests for this feature?",
            "Don't forget to update the documentation",
            "Consider adding error handling",
        ]
        logger.debug(f"Generated {len(suggestions)} suggestions")
        return suggestions

    # Private methods
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    result: List[Dict[str, Any]] = json.load(f)
                    return result
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")
        return []

    def _save_history(self) -> None:
        """Save history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
