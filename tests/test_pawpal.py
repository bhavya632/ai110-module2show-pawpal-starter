import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import Owner, Pet, Task, Priority


@pytest.fixture
def owner():
    return Owner(name="Alex", age=28, occupation="Teacher")


@pytest.fixture
def pet(owner):
    return Pet(name="Buddy", breed="Golden Retriever", age=3, gender="Male", owner=owner)


def test_mark_complete_changes_status(pet):
    task = Task(title="Morning Walk", duration=30, priority=Priority.HIGH, pet=pet)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count(pet):
    assert len(pet.tasks) == 0
    task = Task(title="Feeding", duration=10, priority=Priority.MEDIUM, pet=pet)
    pet.add_task(task)
    assert len(pet.tasks) == 1
