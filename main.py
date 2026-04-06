from pawpal_system import Owner, Pet, Task, Priority
from datetime import date, time, timedelta

# Create owner
owner = Owner(name="Alex", age=28, occupation="Teacher")

# Create pets
buddy = Pet(name="Buddy", breed="Golden Retriever", age=3, gender="Male", owner=owner)
luna = Pet(name="Luna", breed="Siamese Cat", age=5, gender="Female", owner=owner)
owner.pets.extend([buddy, luna])

# Add tasks OUT OF ORDER (times are not chronological)
# recurrence='daily' and 'weekly' tasks auto-create their next occurrence when completed
evening_walk  = Task(title="Evening Walk",  duration=30, priority=Priority.HIGH,   pet=buddy, start_time=time(18, 0),  recurrence="daily")
feeding_am    = Task(title="Morning Feed",  duration=10, priority=Priority.HIGH,   pet=luna,  start_time=time(7, 30),  required=True, recurrence="daily")
grooming      = Task(title="Grooming",      duration=20, priority=Priority.LOW,    pet=buddy, start_time=time(14, 0),  recurrence="weekly")
vet_checkup   = Task(title="Vet Checkup",   duration=60, priority=Priority.MEDIUM, pet=luna,  start_time=time(10, 0))  # one-off
morning_walk  = Task(title="Morning Walk",  duration=25, priority=Priority.HIGH,   pet=buddy, start_time=time(8, 0),   recurrence="daily")
feeding_pm    = Task(title="Evening Feed",  duration=10, priority=Priority.HIGH,   pet=luna,  start_time=time(17, 0),  required=True, recurrence="daily")
playtime      = Task(title="Playtime",      duration=15, priority=Priority.LOW,    pet=buddy)  # no time, no recurrence

for task in [evening_walk, feeding_am, grooming, vet_checkup, morning_walk, feeding_pm, playtime]:
    owner.schedule.add_task(task)

# Mark grooming complete via complete_task() — weekly, so next occurrence auto-added
owner.schedule.complete_task(grooming)

# ── 1. Raw order (insertion order) ──────────────────────────────────────────
print(f"=== Raw Schedule ({date.today()}) — insertion order ===")
owner.schedule.view_schedule()

# ── 2. Sorted by start_time ──────────────────────────────────────────────────
print("\n=== Sorted by Start Time ===")
owner.schedule.sort_by_time()
owner.schedule.view_schedule()

# ── 3. Filter: incomplete tasks only ────────────────────────────────────────
print("\n=== Filter: Incomplete tasks only ===")
for t in owner.schedule.filter_tasks(completed=False):
    time_str = t.start_time.strftime("%I:%M %p") if t.start_time else "no time set"
    print(f"  [{t.priority.value.upper()}] {t.title} — {t.duration} min @ {time_str} (Pet: {t.pet.name})")

# ── 4. Filter: completed tasks only ─────────────────────────────────────────
print("\n=== Filter: Completed tasks only ===")
for t in owner.schedule.filter_tasks(completed=True):
    time_str = t.start_time.strftime("%I:%M %p") if t.start_time else "no time set"
    print(f"  [{t.priority.value.upper()}] {t.title} — {t.duration} min @ {time_str} (Pet: {t.pet.name})")

# ── 5. Filter: Buddy's tasks only ───────────────────────────────────────────
print("\n=== Filter: Buddy's tasks only ===")
for t in owner.schedule.filter_tasks(pet_name="Buddy"):
    time_str = t.start_time.strftime("%I:%M %p") if t.start_time else "no time set"
    print(f"  [{t.priority.value.upper()}] {t.title} — {t.duration} min @ {time_str} (completed: {t.completed})")

# ── 6. Filter: Luna's incomplete tasks (combined filter) ────────────────────
print("\n=== Filter: Luna's incomplete tasks ===")
for t in owner.schedule.filter_tasks(completed=False, pet_name="Luna"):
    time_str = t.start_time.strftime("%I:%M %p") if t.start_time else "no time set"
    print(f"  [{t.priority.value.upper()}] {t.title} — {t.duration} min @ {time_str}")

# ── 7. Conflict detection demo ──────────────────────────────────────────────
print("\n=== Conflict Detection Demo ===")

# Same-pet conflict: Buddy has two tasks at 08:00 AM
bath_time = Task(title="Bath Time", duration=20, priority=Priority.MEDIUM, pet=buddy, start_time=time(8, 0))
owner.schedule.add_task(bath_time)

# Cross-pet conflict: Luna also has a task at 05:00 PM (same as Evening Feed)
nail_trim = Task(title="Nail Trim", duration=15, priority=Priority.LOW, pet=luna, start_time=time(17, 0))
owner.schedule.add_task(nail_trim)

conflicts = owner.schedule.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠ {warning}")
else:
    print("  No conflicts found.")

# ── 8. Recurrence demo ──────────────────────────────────────────────────────
print("\n=== Recurrence Demo ===")
print(f"Grooming was marked complete (weekly). Next occurrence auto-added:")
next_grooming = next(t for t in owner.schedule.tasks if t.title == "Grooming" and not t.completed)
print(f"  due_date: {next_grooming.due_date}  (today + timedelta(days=7) = {date.today() + timedelta(days=7)})")

print(f"\nNow completing 'Morning Feed' (daily):")
next_feed = owner.schedule.complete_task(feeding_am)
print(f"  due_date: {next_feed.due_date}  (today + timedelta(days=1) = {date.today() + timedelta(days=1)})")

print(f"\nNow completing 'Vet Checkup' (one-off, no recurrence):")
result = owner.schedule.complete_task(vet_checkup)
print(f"  next task returned: {result}  (None — no recurrence)")

print("\n=== All tasks after recurrence completions (sorted by time) ===")
owner.schedule.sort_by_time()
for t in owner.schedule.tasks:
    time_str = t.start_time.strftime("%I:%M %p") if t.start_time else "no time set"
    status = "DONE" if t.completed else f"due {t.due_date}"
    recur = f" [{t.recurrence}]" if t.recurrence else ""
    print(f"  [{t.priority.value.upper()}]{recur} {t.title} — {t.duration} min @ {time_str} | {status} (Pet: {t.pet.name})")