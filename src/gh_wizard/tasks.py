"""Task breakdown engine for complex workflows."""

from typing import List, Dict, Any
from pydantic import BaseModel

from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)


class TaskStep(BaseModel):
    """Single task step."""
    name: str
    description: str
    time_estimate: int  # minutes
    priority: str = "normal"  # normal, high, critical
    dependencies: List[str] = []
    commands: List[str] = []


class TaskBreakdown:
    """Break down complex tasks into manageable steps."""

    # Common workflow patterns
    PATTERNS = {
        "release": [
            {"name": "Update CHANGELOG", "time": 10, "desc": "Document all changes in CHANGELOG"},
            {"name": "Run Test Suite", "time": 15, "desc": "Execute full test suite to ensure quality"},
            {"name": "Create Release Branch", "time": 5, "desc": "Branch from main for release"},
            {"name": "Tag Version", "time": 2, "desc": "Create git tag with version"},
            {"name": "Push Changes", "time": 3, "desc": "Push branch and tags to GitHub"},
            {"name": "Draft Release Notes", "time": 15, "desc": "Create release notes on GitHub"},
        ],
        "feature": [
            {"name": "Create Feature Branch", "time": 3, "desc": "Branch from main"},
            {"name": "Implement Feature", "time": 120, "desc": "Write the actual feature code"},
            {"name": "Add Tests", "time": 30, "desc": "Write unit and integration tests"},
            {"name": "Update Documentation", "time": 20, "desc": "Update docs with new feature"},
            {"name": "Create Pull Request", "time": 10, "desc": "Open PR with description"},
            {"name": "Address Code Review", "time": 20, "desc": "Make changes from review"},
            {"name": "Merge", "time": 5, "desc": "Merge PR to main"},
        ],
        "bugfix": [
            {"name": "Reproduce Bug", "time": 15, "desc": "Create minimal reproduction"},
            {"name": "Write Failing Test", "time": 10, "desc": "TDD: write test that fails"},
            {"name": "Fix Bug", "time": 30, "desc": "Implement the fix"},
            {"name": "Verify Tests Pass", "time": 5, "desc": "Run test suite"},
            {"name": "Create PR", "time": 5, "desc": "Open pull request"},
        ],
        "refactor": [
            {"name": "Plan Refactoring", "time": 30, "desc": "Document what needs to change"},
            {"name": "Run Tests (before)", "time": 5, "desc": "Ensure tests pass before changes"},
            {"name": "Implement Changes", "time": 120, "desc": "Refactor the code"},
            {"name": "Run Tests (after)", "time": 5, "desc": "Verify tests still pass"},
            {"name": "Update Documentation", "time": 20, "desc": "Update docs if API changed"},
            {"name": "Create PR", "time": 5, "desc": "Open pull request"},
        ],
    }

    def breakdown(self, task: str) -> List[Dict[str, Any]]:
        """Break down a task into steps.
        
        Args:
            task: Task description
            
        Returns:
            List of task steps
        """
        # Simple pattern matching
        task_lower = task.lower()
        
        for pattern, steps in self.PATTERNS.items():
            if pattern in task_lower:
                result = []
                for step in steps:
                    result.append({
                        "name": step["name"],
                        "description": step["desc"],
                        "time_estimate": step["time"],
                        "priority": "high" if pattern == "release" else "normal",
                    })
                logger.info(f"Broke down task '{task}' using pattern: {pattern}")
                return result
        
        # Default breakdown if no pattern matches
        logger.warning(f"No pattern matched for task: {task}")
        return [
            {
                "name": "Plan",
                "description": "Break down the work",
                "time_estimate": 15,
                "priority": "high",
            },
            {
                "name": "Implement",
                "description": "Do the work",
                "time_estimate": 60,
                "priority": "normal",
            },
            {
                "name": "Test",
                "description": "Verify it works",
                "time_estimate": 20,
                "priority": "high",
            },
            {
                "name": "Document",
                "description": "Update docs",
                "time_estimate": 15,
                "priority": "normal",
            },
        ]
