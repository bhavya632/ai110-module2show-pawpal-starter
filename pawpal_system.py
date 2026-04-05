class Owner:
    def __init__(self, name: str, age: int, occupation: str):
        self.name = name
        self.age = age
        self.occupation = occupation


class Pet:
    def __init__(self, name: str, breed: str, age: int, gender: str):
        self.name = name
        self.breed = breed
        self.age = age
        self.gender = gender


class Task:
    def __init__(self, title: str, duration: int, priority: str):
        self.title = title
        self.duration = duration
        self.priority = priority

    def create_task(self):
        pass

    def edit_task(self):
        pass

    def delete_task(self):
        pass


class DailySchedule:
    def __init__(self):
        self.tasks: list[Task] = []

    def view_schedule(self):
        pass

    def edit_schedule(self):
        pass

    def delete_schedule(self):
        pass
