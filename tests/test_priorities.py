import pytest
from gh_wizard.priorities import EisenhowerMatrix, Task, Quadrant, Priority

@pytest.fixture
def temp_matrix_file(tmp_path):
    return tmp_path / "test_matrix.json"

def test_task_quadrant():
    t1 = Task(id="1", title="Urgent Important", is_urgent=True, is_important=True)
    assert t1.get_quadrant() == Quadrant.Q1
    assert t1.get_priority() == Priority.CRITICAL
    
    t2 = Task(id="2", title="Not Urgent Important", is_urgent=False, is_important=True)
    assert t2.get_quadrant() == Quadrant.Q2
    assert t2.get_priority() == Priority.HIGH
    
    t3 = Task(id="3", title="Urgent Not Important", is_urgent=True, is_important=False)
    assert t3.get_quadrant() == Quadrant.Q3
    assert t3.get_priority() == Priority.NORMAL
    
    t4 = Task(id="4", title="Not Urgent Not Important", is_urgent=False, is_important=False)
    assert t4.get_quadrant() == Quadrant.Q4
    assert t4.get_priority() == Priority.LOW

def test_matrix_add_and_persistence(temp_matrix_file):
    matrix = EisenhowerMatrix()
    
    task = Task(id="1", title="Test Task", is_urgent=True, is_important=True)
    matrix.add_task(task)
    
    assert "1" in matrix.tasks
    assert "1" in matrix.quadrants[Quadrant.Q1]
    
    # Test Save
    matrix.save(str(temp_matrix_file))
    assert temp_matrix_file.exists()
    
    # Test Load
    new_matrix = EisenhowerMatrix()
    new_matrix.load(str(temp_matrix_file))
    
    assert "1" in new_matrix.tasks
    assert new_matrix.tasks["1"].title == "Test Task"

def test_mark_complete():
    matrix = EisenhowerMatrix()
    task = Task(id="1", title="Test Task")
    matrix.add_task(task)
    
    assert matrix.tasks["1"].completed is False
    
    matrix.mark_complete("1")
    assert matrix.tasks["1"].completed is True
