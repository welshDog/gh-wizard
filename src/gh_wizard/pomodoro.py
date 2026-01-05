"""Pomodoro timer with break reminders and hyperfocus mode."""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from pathlib import Path

from gh_wizard.utils.logger import setup_logger
from gh_wizard.utils.config import Config

logger = setup_logger(__name__)


class PomodoroSession:
    """Single Pomodoro session with work and break cycles."""

    def __init__(
        self,
        work_minutes: int = 25,
        short_break_minutes: int = 5,
        long_break_minutes: int = 15,
        sessions_until_long_break: int = 4,
    ):
        """Initialize Pomodoro session.
        
        Args:
            work_minutes: Duration of work session
            short_break_minutes: Duration of short break
            long_break_minutes: Duration of long break
            sessions_until_long_break: How many work sessions before long break
        """
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.sessions_until_long_break = sessions_until_long_break
        
        self.completed_sessions = 0
        self.is_running = False
        self.is_paused = False
        self.current_phase = "work"  # work or break
        self.time_remaining = work_minutes * 60
        self.total_time = work_minutes * 60
        self.start_time: Optional[datetime] = None
        self.paused_time: Optional[datetime] = None
        self.pause_offset = 0  # Track paused duration

    def start(self) -> None:
        """Start the Pomodoro session."""
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.now()
        logger.info(f"Pomodoro session started: {self.work_minutes} min work")

    def pause(self) -> None:
        """Pause the Pomodoro session."""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.paused_time = datetime.now()
            logger.info("Pomodoro session paused")

    def resume(self) -> None:
        """Resume the Pomodoro session."""
        if self.is_paused and self.paused_time:
            pause_duration = (datetime.now() - self.paused_time).total_seconds()
            self.pause_offset += pause_duration
            self.is_paused = False
            self.paused_time = None
            logger.info("Pomodoro session resumed")

    def stop(self) -> None:
        """Stop the Pomodoro session."""
        self.is_running = False
        self.is_paused = False
        logger.info("Pomodoro session stopped")

    def get_elapsed_seconds(self) -> int:
        """Get elapsed seconds since session started."""
        if not self.start_time:
            return 0
        
        elapsed = (datetime.now() - self.start_time).total_seconds() - self.pause_offset
        return max(0, int(elapsed))

    def get_remaining_seconds(self) -> int:
        """Get remaining seconds in current phase."""
        elapsed = self.get_elapsed_seconds()
        remaining = self.total_time - elapsed
        return max(0, remaining)

    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0-100)."""
        if self.total_time == 0:
            return 0
        elapsed = self.get_elapsed_seconds()
        return min(100, (elapsed / self.total_time) * 100)

    def is_phase_complete(self) -> bool:
        """Check if current phase is complete."""
        return self.get_remaining_seconds() <= 0

    def advance_to_break(self) -> str:
        """Advance to break phase. Returns break type."""
        self.completed_sessions += 1
        
        # Determine break type
        if self.completed_sessions % self.sessions_until_long_break == 0:
            break_type = "long"
            self.total_time = self.long_break_minutes * 60
        else:
            break_type = "short"
            self.total_time = self.short_break_minutes * 60
        
        self.current_phase = "break"
        self.time_remaining = self.total_time
        self.pause_offset = 0
        self.start_time = datetime.now()
        
        logger.info(f"Moving to {break_type} break after {self.completed_sessions} sessions")
        return break_type

    def advance_to_work(self) -> None:
        """Advance to work phase."""
        self.current_phase = "work"
        self.total_time = self.work_minutes * 60
        self.time_remaining = self.total_time
        self.pause_offset = 0
        self.start_time = datetime.now()
        logger.info("Moving to work phase")

    def format_time(self, seconds: Optional[int] = None) -> str:
        """Format seconds as MM:SS."""
        if seconds is None:
            seconds = self.get_remaining_seconds()
        
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"


class BreakReminder:
    """Intelligent break reminders with system activity awareness."""

    def __init__(
        self,
        config: Optional[Config] = None,
        reminder_callback: Optional[Callable] = None,
    ):
        """Initialize break reminder.
        
        Args:
            config: Config manager instance
            reminder_callback: Callable when break should be taken
        """
        self.config = config or Config()
        self.reminder_callback = reminder_callback
        self.last_activity_time = datetime.now()
        self.idle_threshold = 3600  # 1 hour in seconds
        self.break_suggestions = [
            "Time for a quick walk! 🚶",
            "Stretch those muscles! 🤸",
            "Grab some water 💧",
            "Look away from the screen 👀",
            "Do some deep breathing 🌬️",
            "Check the weather! 🌤️",
        ]

    def should_take_break(self, session: PomodoroSession) -> bool:
        """Determine if a break should be suggested."""
        if session.current_phase == "break":
            return False
        
        # Check if extended work detected
        if session.get_elapsed_seconds() > self.idle_threshold:
            logger.warning("Extended work session detected - break overdue!")
            return True
        
        return False

    def get_break_suggestion(self) -> str:
        """Get a random break suggestion."""
        import random
        return random.choice(self.break_suggestions)

    def trigger_reminder(self, session: PomodoroSession) -> None:
        """Trigger break reminder."""
        suggestion = self.get_break_suggestion()
        
        if self.reminder_callback:
            self.reminder_callback(
                title="⏰ Break Time!",
                message=f"You've worked for {session.get_elapsed_seconds() // 60} minutes.\n{suggestion}",
            )
        
        logger.info(f"Break reminder triggered: {suggestion}")

    def record_activity(self) -> None:
        """Record user activity."""
        self.last_activity_time = datetime.now()

    def get_idle_time(self) -> int:
        """Get idle time in seconds."""
        return int((datetime.now() - self.last_activity_time).total_seconds())
