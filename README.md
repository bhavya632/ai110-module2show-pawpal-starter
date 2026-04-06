# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The following features have been added to `pawpal_system.py` and `app.py` beyond the original skeleton:

**Greedy time-budget scheduler** — `generate_schedule(available_minutes)` sorts incomplete tasks by required status, then priority (HIGH → LOW), then duration (shorter first as a tie-breaker). Required tasks (e.g. feeding, medication) are always included; optional tasks are packed in greedily until the time budget runs out.

**Conflict detection** — `detect_conflicts()` groups timed tasks by `start_time` and returns a plain-English warning for every overlapping pair — both same-pet and cross-pet conflicts. The program never crashes; warnings are returned as a list of strings.

**Recurrence** — Tasks accept a `recurrence` parameter (`"daily"` or `"weekly"`). Calling `complete_task()` on a recurring task automatically creates the next occurrence using Python's `timedelta` (`+1 day` for daily, `+7 days` for weekly) and adds it to the schedule.

**Sort by time** — `sort_by_time()` reorders the schedule chronologically by `start_time`. Tasks with no start time are placed at the end.

**Filter tasks** — `filter_tasks(completed, pet_name)` returns a filtered subset of tasks. Both parameters are optional and composable — e.g. `filter_tasks(completed=False, pet_name="Buddy")` returns only Buddy's incomplete tasks.

**Duplicate guard** — `add_task()` silently ignores a task if one with the same title, pet, and due date already exists, preventing accidental double-scheduling.

**Input validation** — `Task` raises `ValueError` for non-positive durations or unrecognised recurrence strings.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
