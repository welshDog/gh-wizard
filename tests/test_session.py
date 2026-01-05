"""Tests for session management."""

import pytest
import tempfile
from pathlib import Path
from gh_wizard.session import SessionManager


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_session_start(temp_config_dir):
    """Test starting a session."""
    manager = SessionManager(config_dir=temp_config_dir)
    session_id = manager.start("Test Session")
    
    assert session_id is not None
    assert len(session_id) > 0
    
    # Verify session was created
    session = manager.get_current_session()
    assert session is not None
    assert session["name"] == "Test Session"


def test_session_pause_resume(temp_config_dir):
    """Test pausing and resuming sessions."""
    manager = SessionManager(config_dir=temp_config_dir)
    session_id = manager.start("Test Session")
    
    # Pause
    manager.pause(session_id)
    session = manager._load_session(session_id)
    assert session["status"] == "paused"
    
    # Resume
    manager.resume(session_id)
    session = manager._load_session(session_id)
    assert session["status"] == "active"


def test_session_context(temp_config_dir):
    """Test updating session context."""
    manager = SessionManager(config_dir=temp_config_dir)
    session_id = manager.start("Test Session")
    
    context = {"repo": "test-repo", "branch": "feature/test"}
    manager.update_context(session_id, context)
    
    session = manager._load_session(session_id)
    assert session["context"]["repo"] == "test-repo"
    assert session["context"]["branch"] == "feature/test"


def test_session_breadcrumbs(temp_config_dir):
    """Test adding breadcrumbs."""
    manager = SessionManager(config_dir=temp_config_dir)
    session_id = manager.start("Test Session")
    
    manager.add_breadcrumb("Started work", session_id)
    manager.add_breadcrumb("Implemented feature", session_id)
    
    session = manager._load_session(session_id)
    assert len(session["breadcrumbs"]) == 2
    assert session["breadcrumbs"][0]["message"] == "Started work"
