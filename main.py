from pawpal_system import Owner, Pet, Task, Priority
from datetime import date

# Create owner
owner = Owner(name="Alex", age=28, occupation="Teacher")

# Create pets and link them to the owner
buddy = Pet(name="Buddy", breed="Golden Retriever", age=3, gender="Male", owner=owner)
luna = Pet(name="Luna", breed="Siamese Cat", age=5, gender="Female", owner=owner)
owner.pets.extend([buddy, luna])

# Create tasks with different durations and priorities
morning_walk = Task(title="Morning Walk", duration=30, priority=Priority.HIGH, pet=buddy)
feeding = Task(title="Feeding", duration=10, priority=Priority.MEDIUM, pet=luna)
grooming = Task(title="Grooming", duration=20, priority=Priority.LOW, pet=buddy)

# Add tasks to the owner's schedule
owner.schedule.add_task(morning_walk)
owner.schedule.add_task(feeding)
owner.schedule.add_task(grooming)

# Print today's schedule
print(f"=== Today's Schedule ({date.today()}) ===")
owner.schedule.view_schedule()
