from enum import Enum
from datetime import date, time, timedelta


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


class Owner:
    def __init__(self, name: str, age: int, occupation: str):
        """Initialize an Owner with personal details, an empty pet list, and today's schedule."""
        self.name = name
        self.age = age
        self.occupation = occupation
        self.pets: list[Pet] = []
        self.schedule: DailySchedule = DailySchedule(date.today())

    def add_pet(self, pet: "Pet"):
        """Add a new pet to the owner's pet list."""
        self.pets.append(pet)


class Pet:
    def __init__(self, name: str, breed: str, age: int, gender: str, owner: "Owner"):
        """Initialize a Pet with its details, a reference to its owner, and an empty task list."""
        self.name = name
        self.breed = breed
        self.age = age
        self.gender = gender
        self.owner = owner
        self.tasks: list["Task"] = []

    def add_task(self, task: "Task"):
        """Append a task to this pet's task list."""
        self.tasks.append(task)


RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


class Task:
    def __init__(self, title: str, duration: int, priority: Priority, pet: Pet,
                 required: bool = False, start_time: time | None = None,
                 recurrence: str | None = None, due_date: date | None = None):
        """Initialize a Task.

        Args:
            recurrence: 'daily', 'weekly', or None for one-off tasks.
            due_date:   The date this task is due. Defaults to today if not provided.
        """
        if duration <= 0:
            raise ValueError("duration must be a positive number of minutes")
        if recurrence is not None and recurrence not in RECURRENCE_DAYS:
            raise ValueError(f"recurrence must be 'daily', 'weekly', or None — got '{recurrence}'")
        self.title = title
        self.duration = duration
        self.priority = priority
        self.pet = pet
        self.required = required
        self.start_time: time | None = start_time
        self.recurrence: str | None = recurrence
        self.due_date: date = due_date or date.today()
        self.completed: bool = False

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed.

        Returns a new Task for the next occurrence if the task recurs, else None.
        timedelta is used to calculate the next due date:
            - 'daily'  -> due_date + timedelta(days=1)
            - 'weekly' -> due_date + timedelta(days=7)
        """
        self.completed = True
        if self.recurrence is None:
            return None
        days_ahead = RECURRENCE_DAYS[self.recurrence]
        next_due = self.due_date + timedelta(days=days_ahead)
        return Task(
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            pet=self.pet,
            required=self.required,
            start_time=self.start_time,
            recurrence=self.recurrence,
            due_date=next_due,
        )


class DailySchedule:
    def __init__(self, day: date):
        """Initialize a DailySchedule for a specific date with an empty task list."""
        self.day = day
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Add a task to the schedule, ignoring duplicates (same title, pet, and due_date)."""
        if any(t.title == task.title and t.pet == task.pet and t.due_date == task.due_date for t in self.tasks):
            return
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a specific task from the schedule."""
        self.tasks.remove(task)

    def detect_conflicts(self) -> list[str]:
        """Detect scheduling conflicts among incomplete timed tasks.

        Groups incomplete tasks by start_time, then checks each group for overlaps.
        Tasks without a start_time are ignored — they have no fixed slot to conflict with.

        Returns:
            A list of human-readable warning strings, one per conflicting pair.
            Same-pet conflicts name the shared pet; cross-pet conflicts name both pets.
            Returns an empty list if no conflicts are found.
        """
        warnings = []
        timed = [t for t in self.tasks if t.start_time is not None and not t.completed]
        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                if a.start_time == b.start_time:
                    if a.pet == b.pet:
                        msg = (f"CONFLICT: '{a.title}' and '{b.title}' are both scheduled "
                               f"for {a.pet.name} at {a.start_time.strftime('%I:%M %p')}.")
                    else:
                        msg = (f"CONFLICT: '{a.title}' ({a.pet.name}) and '{b.title}' ({b.pet.name}) "
                               f"overlap at {a.start_time.strftime('%I:%M %p')}.")
                    warnings.append(msg)
        return warnings

    def complete_task(self, task: Task) -> "Task | None":
        """Mark a task complete and, if it recurs, add the next occurrence to this schedule.

        Returns the newly created next-occurrence Task, or None for one-off tasks.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def generate_schedule(self, available_minutes: int) -> list[Task]:
        """Build a greedy schedule that fits within the owner's available time.

        Sorts incomplete tasks by: required first, then priority (HIGH → LOW),
        then duration (shorter first) to maximize the number of high-priority tasks
        that fit. Required tasks are always included even if they exceed the budget.
        Optional tasks are added one-by-one until no time remains.

        Args:
            available_minutes: Total minutes the owner has free today.

        Returns:
            An ordered list of Task objects that fit within available_minutes.
        """
        incomplete = [t for t in self.tasks if not t.completed]

        # Sort: required first, then by priority, then by duration (shorter first for tie-breaking)
        def sort_key(t: Task):
            return (0 if t.required else 1, PRIORITY_ORDER[t.priority], t.duration)

        sorted_tasks = sorted(incomplete, key=sort_key)

        result = []
        remaining = available_minutes

        for task in sorted_tasks:
            if task.required:
                result.append(task)
                remaining -= task.duration
            elif task.duration <= remaining:
                result.append(task)
                remaining -= task.duration

        return result

    def carry_forward_required(self, next_schedule: "DailySchedule"):
        """Copy any incomplete required tasks from this schedule into next_schedule."""
        for task in self.tasks:
            if task.required and not task.completed:
                next_schedule.add_task(task)

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[Task]:
        """Return tasks matching the given filters.

        Args:
            completed: If True, return only completed tasks. If False, return only incomplete tasks.
                       If None, completion status is not filtered.
            pet_name:  If provided, return only tasks assigned to a pet with that name.
                       If None, all pets are included.
        """
        result = self.tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet.name == pet_name]
        return result

    def sort_by_time(self):
        """Sort tasks in-place by start_time. Tasks without a start_time are placed at the end."""
        self.tasks.sort(key=lambda t: (t.start_time is None, t.start_time))

    def view_schedule(self):
        """Print all tasks for the day with their priority, duration, start time, and assigned pet."""
        for task in self.tasks:
            time_str = task.start_time.strftime("%I:%M %p") if task.start_time else "no time set"
            print(f"[{task.priority.value.upper()}] {task.title} — {task.duration} min @ {time_str} (Pet: {task.pet.name})")

    def edit_schedule(self, old_task: Task, new_task: Task):
        """Replace an existing task in the schedule with a new one."""
        index = self.tasks.index(old_task)
        self.tasks[index] = new_task

    def clear_schedule(self):
        """Remove all tasks from the schedule."""
        self.tasks.clear()
