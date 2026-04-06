import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, DailySchedule, Priority


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def owner():
    return Owner(name="Alex", age=28, occupation="Teacher")


@pytest.fixture
def pet(owner):
    return Pet(name="Buddy", breed="Golden Retriever", age=3, gender="Male", owner=owner)


@pytest.fixture
def pet2(owner):
    return Pet(name="Luna", breed="Poodle", age=2, gender="Female", owner=owner)


@pytest.fixture
def schedule():
    return DailySchedule(date.today())


# ---------------------------------------------------------------------------
# Original tests (kept)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Sorting correctness — sort_by_time
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order(pet, schedule):
    """Tasks with start times must be sorted in chronological order."""
    t1 = Task(title="Lunch", duration=15, priority=Priority.MEDIUM, pet=pet,
              start_time=time(12, 0))
    t2 = Task(title="Morning Walk", duration=30, priority=Priority.HIGH, pet=pet,
              start_time=time(8, 0))
    t3 = Task(title="Evening Run", duration=20, priority=Priority.LOW, pet=pet,
              start_time=time(18, 0))
    for t in [t1, t2, t3]:
        schedule.add_task(t)

    schedule.sort_by_time()

    times = [t.start_time for t in schedule.tasks]
    assert times == sorted(times), "Tasks should be in ascending time order"


def test_sort_by_time_no_time_tasks_go_last(pet, schedule):
    """Tasks without a start_time must appear after all timed tasks."""
    timed = Task(title="Morning Walk", duration=30, priority=Priority.HIGH, pet=pet,
                 start_time=time(8, 0))
    no_time = Task(title="Grooming", duration=20, priority=Priority.MEDIUM, pet=pet)
    schedule.add_task(no_time)
    schedule.add_task(timed)

    schedule.sort_by_time()

    assert schedule.tasks[0].start_time is not None, "Timed task should come first"
    assert schedule.tasks[-1].start_time is None, "Task with no time should be last"


def test_generate_schedule_priority_ordering(pet, schedule):
    """generate_schedule must return HIGH priority tasks before MEDIUM and LOW."""
    low = Task(title="Playtime", duration=10, priority=Priority.LOW, pet=pet)
    high = Task(title="Medication", duration=10, priority=Priority.HIGH, pet=pet)
    medium = Task(title="Feeding", duration=10, priority=Priority.MEDIUM, pet=pet)
    for t in [low, high, medium]:
        schedule.add_task(t)

    result = schedule.generate_schedule(available_minutes=60)

    priorities = [t.priority for t in result]
    assert priorities == [Priority.HIGH, Priority.MEDIUM, Priority.LOW]


def test_generate_schedule_shorter_duration_first_on_tie(pet, schedule):
    """When priority is equal, the shorter task should be scheduled first."""
    long_task = Task(title="Long Bath", duration=45, priority=Priority.MEDIUM, pet=pet)
    short_task = Task(title="Quick Brush", duration=10, priority=Priority.MEDIUM, pet=pet)
    schedule.add_task(long_task)
    schedule.add_task(short_task)

    result = schedule.generate_schedule(available_minutes=60)

    assert result[0].title == "Quick Brush", "Shorter task should come first on priority tie"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task(pet):
    """Completing a daily task must return a new task due the following day."""
    today = date.today()
    task = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet,
                recurrence="daily", due_date=today)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.recurrence == "daily"
    assert next_task.title == "Walk"


def test_weekly_recurrence_creates_task_in_seven_days(pet):
    """Completing a weekly task must return a new task due seven days later."""
    today = date.today()
    task = Task(title="Bath", duration=60, priority=Priority.MEDIUM, pet=pet,
                recurrence="weekly", due_date=today)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=7)


def test_one_off_task_returns_none_on_complete(pet):
    """Completing a non-recurring task must return None (no next occurrence)."""
    task = Task(title="Vet Visit", duration=90, priority=Priority.HIGH, pet=pet)

    result = task.mark_complete()

    assert result is None


def test_complete_task_adds_next_occurrence_to_schedule(pet, schedule):
    """complete_task() must auto-add the next recurring task to the schedule."""
    today = date.today()
    task = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet,
                recurrence="daily", due_date=today)
    schedule.add_task(task)

    schedule.complete_task(task)

    titles = [t.title for t in schedule.tasks]
    assert titles.count("Walk") == 2, "Next occurrence should be added to the schedule"
    next_task = next(t for t in schedule.tasks if not t.completed)
    assert next_task.due_date == today + timedelta(days=1)


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_pet_same_time(pet, schedule):
    """Two tasks for the same pet at the same start_time must raise a conflict."""
    t1 = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet,
              start_time=time(8, 0))
    t2 = Task(title="Feeding", duration=15, priority=Priority.MEDIUM, pet=pet,
              start_time=time(8, 0))
    schedule.add_task(t1)
    schedule.add_task(t2)

    conflicts = schedule.detect_conflicts()

    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feeding" in conflicts[0]
    assert "Buddy" in conflicts[0]


def test_detect_conflicts_cross_pet_same_time(pet, pet2, schedule):
    """Two tasks for different pets at the same start_time must raise a conflict."""
    t1 = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet,
              start_time=time(9, 0))
    t2 = Task(title="Grooming", duration=20, priority=Priority.MEDIUM, pet=pet2,
              start_time=time(9, 0))
    schedule.add_task(t1)
    schedule.add_task(t2)

    conflicts = schedule.detect_conflicts()

    assert len(conflicts) == 1
    assert "Buddy" in conflicts[0]
    assert "Luna" in conflicts[0]


def test_detect_conflicts_no_conflict_different_times(pet, schedule):
    """Tasks at different times must not produce any conflicts."""
    t1 = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet,
              start_time=time(8, 0))
    t2 = Task(title="Feeding", duration=15, priority=Priority.MEDIUM, pet=pet,
              start_time=time(10, 0))
    schedule.add_task(t1)
    schedule.add_task(t2)

    assert schedule.detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks(pet, schedule):
    """A completed task must not participate in conflict detection."""
    t1 = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet,
              start_time=time(8, 0))
    t2 = Task(title="Feeding", duration=15, priority=Priority.MEDIUM, pet=pet,
              start_time=time(8, 0))
    t1.mark_complete()
    schedule.add_task(t1)
    schedule.add_task(t2)

    assert schedule.detect_conflicts() == []


def test_detect_conflicts_ignores_tasks_without_time(pet, schedule):
    """Tasks without a start_time must be excluded from conflict detection."""
    t1 = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet)
    t2 = Task(title="Feeding", duration=15, priority=Priority.MEDIUM, pet=pet)
    schedule.add_task(t1)
    schedule.add_task(t2)

    assert schedule.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_generate_schedule_required_task_always_included(pet, schedule):
    """Required tasks must appear in the result even when available_minutes is 0."""
    required = Task(title="Medication", duration=30, priority=Priority.HIGH,
                    pet=pet, required=True)
    optional = Task(title="Playtime", duration=20, priority=Priority.LOW, pet=pet)
    schedule.add_task(required)
    schedule.add_task(optional)

    result = schedule.generate_schedule(available_minutes=0)

    assert required in result
    assert optional not in result


def test_generate_schedule_empty_schedule(schedule):
    """generate_schedule on an empty schedule must return an empty list."""
    assert schedule.generate_schedule(available_minutes=60) == []


def test_sort_by_time_empty_schedule(schedule):
    """sort_by_time on an empty schedule must not raise."""
    schedule.sort_by_time()
    assert schedule.tasks == []


def test_detect_conflicts_empty_schedule(schedule):
    """detect_conflicts on an empty schedule must return an empty list."""
    assert schedule.detect_conflicts() == []


def test_add_task_ignores_duplicate(pet, schedule):
    """Adding the same task twice must not grow the task list."""
    today = date.today()
    task = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet,
                due_date=today)
    schedule.add_task(task)
    schedule.add_task(task)

    assert len(schedule.tasks) == 1


def test_task_invalid_duration_raises(pet):
    """A task with zero or negative duration must raise ValueError."""
    with pytest.raises(ValueError, match="duration"):
        Task(title="Bad Task", duration=0, priority=Priority.LOW, pet=pet)


def test_task_invalid_recurrence_raises(pet):
    """An unrecognized recurrence string must raise ValueError."""
    with pytest.raises(ValueError, match="recurrence"):
        Task(title="Bad Task", duration=10, priority=Priority.LOW, pet=pet,
             recurrence="monthly")


def test_filter_tasks_by_completion(pet, schedule):
    """filter_tasks(completed=False) must return only incomplete tasks."""
    done = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet)
    pending = Task(title="Feeding", duration=10, priority=Priority.MEDIUM, pet=pet,
                   due_date=date.today() + timedelta(days=1))
    done.mark_complete()
    schedule.add_task(done)
    schedule.add_task(pending)

    incomplete = schedule.filter_tasks(completed=False)

    assert pending in incomplete
    assert done not in incomplete


def test_filter_tasks_by_pet_name(pet, pet2, schedule):
    """filter_tasks(pet_name=...) must return only tasks for that pet."""
    buddy_task = Task(title="Walk", duration=30, priority=Priority.HIGH, pet=pet)
    luna_task = Task(title="Grooming", duration=20, priority=Priority.MEDIUM, pet=pet2)
    schedule.add_task(buddy_task)
    schedule.add_task(luna_task)

    result = schedule.filter_tasks(pet_name="Buddy")

    assert buddy_task in result
    assert luna_task not in result


def test_carry_forward_required_incomplete_only(pet, schedule):
    """carry_forward_required must only copy incomplete required tasks."""
    done_required = Task(title="Medication", duration=15, priority=Priority.HIGH,
                         pet=pet, required=True)
    pending_required = Task(title="Walk", duration=30, priority=Priority.HIGH,
                            pet=pet, required=True,
                            due_date=date.today() + timedelta(days=1))
    done_required.mark_complete()
    schedule.add_task(done_required)
    schedule.add_task(pending_required)

    next_schedule = DailySchedule(date.today() + timedelta(days=1))
    schedule.carry_forward_required(next_schedule)

    assert pending_required in next_schedule.tasks
    assert done_required not in next_schedule.tasks
