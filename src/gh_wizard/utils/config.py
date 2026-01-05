"""Configuration management."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)


class Config:
    """Manage wizard configuration."""

    DEFAULT_CONFIG = {
        "dnd_mode": False,
        "pomodoro_enabled": True,
        "pomodoro_work_minutes": 25,
        "pomodoro_break_minutes": 5,
        "theme": "auto",  # auto, light, dark
        "watched_repos": [],
    }

    def __init__(self, config_file: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_file: Path to config file. Defaults to ~/.ghwizard/config.json
        """
        if config_file is None:
            config_file = Path.home() / ".ghwizard" / "config.json"
        
        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value."""
        self.config[key] = value
        self._save_config()
        logger.debug(f"Config updated: {key} = {value}")

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple config values."""
        self.config.update(updates)
        self._save_config()
        logger.debug(f"Config updated: {updates}")

    # Private methods
    def _load_config(self) -> Dict[str, Any]:
        """Load config from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return self.DEFAULT_CONFIG.copy()

    def _save_config(self) -> None:
        """Save config to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
