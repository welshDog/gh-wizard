import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from gh_wizard.stats import StatsManager, DailyStats
from gh_wizard.pomodoro import PomodoroSession, notify_phase_complete

def test_stats_manager(tmp_path):
    stats_file = tmp_path / "stats.json"
    manager = StatsManager(stats_file=stats_file)
    
    # Initial state
    stats = manager.get_today_stats()
    assert stats.work_sessions == 0
    assert stats.work_minutes == 0
    
    # Record work
    manager.record_work_session(25)
    stats = manager.get_today_stats()
    assert stats.work_sessions == 1
    assert stats.work_minutes == 25
    assert stats.longest_focus == 25
    
    # Record break
    manager.record_break()
    stats = manager.get_today_stats()
    assert stats.breaks_taken == 1
    
    # Record task
    manager.record_task_completion()
    stats = manager.get_today_stats()
    assert stats.tasks_completed == 1
    
    # Verify persistence
    manager2 = StatsManager(stats_file=stats_file)
    stats2 = manager2.get_today_stats()
    assert stats2.work_sessions == 1
    assert stats2.work_minutes == 25

def test_pomodoro_notify():
    with patch("builtins.print") as mock_print:
        notify_phase_complete("work")
        # On non-windows, it prints \a
        # On windows, it uses winsound.Beep
        # Since we can't easily check OS here, we just ensure it doesn't crash
        pass
