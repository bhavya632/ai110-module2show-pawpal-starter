from enum import Enum
from datetime import date


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Owner:
    def __init__(self, name: str, age: int, occupation: str):
        """Initialize an Owner with personal details, an empty pet list, and today's schedule."""
        self.name = name
        self.age = age
        self.occupation = occupation
        self.pets: list[Pet] = []
        self.schedule: DailySchedule = DailySchedule(date.today())


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


class Task:
    def __init__(self, title: str, duration: int, priority: Priority, pet: Pet):
        """Initialize a Task with a title, duration in minutes, priority level, and assigned pet."""
        self.title = title
        self.duration = duration
        self.priority = priority
        self.pet = pet
        self.completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True


class DailySchedule:
    def __init__(self, day: date):
        """Initialize a DailySchedule for a specific date with an empty task list."""
        self.day = day
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Add a task to the schedule."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a specific task from the schedule."""
        self.tasks.remove(task)

    def view_schedule(self):
        """Print all tasks for the day with their priority, duration, and assigned pet."""
        for task in self.tasks:
            print(f"[{task.priority.value.upper()}] {task.title} — {task.duration} min (Pet: {task.pet.name})")

    def edit_schedule(self, old_task: Task, new_task: Task):
        """Replace an existing task in the schedule with a new one."""
        index = self.tasks.index(old_task)
        self.tasks[index] = new_task

    def clear_schedule(self):
        """Remove all tasks from the schedule."""
        self.tasks.clear()
