# PawPal+ 
## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan


## Smarter Scheduling

The following features have been added to `pawpal_system.py` and `app.py` beyond the original skeleton:

**Greedy time-budget scheduler** — `generate_schedule(available_minutes)` sorts incomplete tasks by required status, then priority (HIGH → LOW), then duration (shorter first as a tie-breaker). Required tasks (e.g. feeding, medication) are always included; optional tasks are packed in greedily until the time budget runs out.

**Conflict detection** — `detect_conflicts()` groups timed tasks by `start_time` and returns a plain-English warning for every overlapping pair — both same-pet and cross-pet conflicts. The program never crashes; warnings are returned as a list of strings.

**Recurrence** — Tasks accept a `recurrence` parameter (`"daily"` or `"weekly"`). Calling `complete_task()` on a recurring task automatically creates the next occurrence using Python's `timedelta` (`+1 day` for daily, `+7 days` for weekly) and adds it to the schedule.

**Sort by time** — `sort_by_time()` reorders the schedule chronologically by `start_time`. Tasks with no start time are placed at the end.

**Filter tasks** — `filter_tasks(completed, pet_name)` returns a filtered subset of tasks. Both parameters are optional and composable — e.g. `filter_tasks(completed=False, pet_name="Buddy")` returns only Buddy's incomplete tasks.

**Duplicate guard** — `add_task()` silently ignores a task if one with the same title, pet, and due date already exists, preventing accidental double-scheduling.

**Input validation** — `Task` raises `ValueError` for non-positive durations or unrecognised recurrence strings.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains **25 tests** across five areas:

| Area | What is verified |
|---|---|
| **Sorting** | `sort_by_time()` returns tasks in chronological order; tasks with no `start_time` are placed at the end; `generate_schedule()` orders by priority (HIGH → MEDIUM → LOW) and uses shorter duration as a tie-breaker |
| **Recurrence** | Completing a daily task produces a new task due the next day; weekly produces one due in 7 days; one-off tasks return `None`; `complete_task()` auto-adds the next occurrence to the schedule |
| **Conflict detection** | Same-pet conflicts at identical start times are flagged; cross-pet conflicts name both pets; completed tasks and tasks without a `start_time` are correctly ignored; no false positives when times differ |
| **Edge cases** | Required tasks bypass the time budget even when `available_minutes=0`; duplicate tasks are silently ignored; `ValueError` is raised for non-positive durations and unrecognized recurrence strings |
| **Filtering** | `filter_tasks(completed=False)` returns only pending tasks; `filter_tasks(pet_name=...)` scopes to one pet; `carry_forward_required()` copies only incomplete required tasks to the next schedule |

### Confidence level

**4 / 5 stars**

The core scheduling behaviors — priority ordering, recurrence math, conflict detection, and required-task guarantees — are all directly tested and passing. One star is withheld because conflict detection only catches tasks at the **exact same `start_time`**; duration-overlap conflicts (e.g. a 60-minute task at 8:00 AM and a 30-minute task at 8:30 AM) are not yet detected or tested.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 📸 Demo
<a href="assets/demo.png" target="_blank"><img src='assets/demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.

===
