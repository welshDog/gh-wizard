import pytest
import time
from gh_wizard.pomodoro import PomodoroSession


def test_pomodoro_initialization():
    session = PomodoroSession(work_minutes=25, short_break_minutes=5)
    assert session.work_minutes == 25
    assert session.short_break_minutes == 5
    assert session.current_phase == "work"
    assert session.is_running is False

def test_pomodoro_start_stop():
    session = PomodoroSession()
    session.start()
    assert session.is_running is True
    assert session.start_time is not None
    
    session.stop()
    assert session.is_running is False

def test_pomodoro_pause_resume():
    session = PomodoroSession()
    session.start()
    assert session.is_paused is False
    
    session.pause()
    assert session.is_paused is True
    assert session.paused_time is not None
    
    # Wait a bit
    time.sleep(0.1)
    
    session.resume()
    assert session.is_paused is False
    assert session.paused_time is None
    assert session.pause_offset > 0

def test_pomodoro_next_phase():
    session = PomodoroSession(work_minutes=1, short_break_minutes=1)
    session.start()
    assert session.current_phase == "work"
    
    # Force next phase
    session.next_phase()
    assert session.current_phase == "short_break"
    assert session.completed_sessions == 1
    
    session.next_phase()
    assert session.current_phase == "work"
