from enum import Enum
from datetime import date


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Owner:
    def __init__(self, name: str, age: int, occupation: str):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.pets: list[Pet] = []
        self.schedule: DailySchedule = DailySchedule(date.today())


class Pet:
    def __init__(self, name: str, breed: str, age: int, gender: str, owner: "Owner"):
        self.name = name
        self.breed = breed
        self.age = age
        self.gender = gender
        self.owner = owner


class Task:
    def __init__(self, title: str, duration: int, priority: Priority, pet: Pet):
        self.title = title
        self.duration = duration
        self.priority = priority
        self.pet = pet


class DailySchedule:
    def __init__(self, day: date):
        self.day = day
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task: Task):
        self.tasks.remove(task)

    def view_schedule(self):
        for task in self.tasks:
            print(f"[{task.priority.value.upper()}] {task.title} — {task.duration} min (Pet: {task.pet.name})")

    def edit_schedule(self, old_task: Task, new_task: Task):
        index = self.tasks.index(old_task)
        self.tasks[index] = new_task

    def clear_schedule(self):
        self.tasks.clear()
