"""Tests for task breakdown."""

import pytest
from gh_wizard.tasks import TaskBreakdown


def test_release_breakdown():
    """Test release task breakdown."""
    breakdown = TaskBreakdown()
    steps = breakdown.breakdown("Release HyperCode v2.0")
    
    assert len(steps) > 0
    assert any("CHANGELOG" in step["name"] for step in steps)
    assert any("Test" in step["name"] for step in steps)


def test_feature_breakdown():
    """Test feature task breakdown."""
    breakdown = TaskBreakdown()
    steps = breakdown.breakdown("Implement new parser")
    
    assert len(steps) > 0
    assert any("Test" in step["name"] for step in steps)


def test_bugfix_breakdown():
    """Test bugfix task breakdown."""
    breakdown = TaskBreakdown()
    steps = breakdown.breakdown("Fix parser crash")
    
    assert len(steps) > 0
    assert any("Reproduce" in step["name"] for step in steps)


def test_default_breakdown():
    """Test default breakdown for unknown task."""
    breakdown = TaskBreakdown()
    steps = breakdown.breakdown("Some random task")
    
    assert len(steps) > 0
    assert "Plan" in [step["name"] for step in steps]
