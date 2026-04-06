# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML included four classes: Owner (name, age, occupation), Pet (name, breed, age, gender), Task (create, edit, delete, duration, priority), and DailySchedule (view, edit, delete). The relationships were loose — I had not yet decided how Owner connected to Pet, or how DailySchedule would hold Task objects.

**b. Design changes**

Yes, the design changed significantly during implementation. The biggest additions were:

- A back-reference from Pet to Owner (the `owner` attribute), which was needed so any task could trace back to who owns the pet.
- A `Priority` enum instead of a plain string, which made sorting reliable and removed the risk of typos like `"High"` vs `"high"`.
- `recurrence`, `required`, `start_time`, and `due_date` attributes on Task — none of these were in the initial design but turned out to be essential for a real scheduler.
- `detect_conflicts()`, `generate_schedule()`, `filter_tasks()`, `sort_by_time()`, and `carry_forward_required()` on DailySchedule — the initial design only had view/edit/delete, which are UI actions, not scheduling logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints in order: whether a task is required (required tasks are never skipped), priority level (HIGH → MEDIUM → LOW), and duration (shorter tasks are preferred as a tie-breaker to maximize the number of tasks that fit). The most important constraint is required status, because missing medication or feeding has real consequences for a pet — no amount of available time should cause those to be dropped.

**b. Tradeoffs**

The conflict detection algorithm is O(n²) — it compares every pair of timed tasks. For a typical pet owner with 5–15 tasks per day, this is fast and the code is easy to read and debug. The tradeoff is that it would not scale well to hundreds of tasks. For this use case the tradeoff is reasonable: readability and correctness matter more than raw performance, and a daily pet schedule will never have enough tasks to make the quadratic cost noticeable.

A second tradeoff: conflict detection only flags tasks at the exact same `start_time`. It does not account for duration overlap (a 60-minute task at 8:00 AM and a 30-minute task at 8:30 AM would not be flagged). This keeps the logic simple but is a known limitation documented in the test suite.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools (Claude Code via the VS Code extension) were used across all phases of the project:

- **Design phase:** Asked the AI to analyze the codebase and list edge cases before writing any tests. This surfaced gaps like "pet with no tasks" and "two tasks at the exact same time" that I had not thought of.
- **Implementation phase:** Used the chat to generate the full test suite once I had described the behaviors I wanted to verify. The AI matched the exact method signatures and fixture patterns already in the file.
- **UI phase:** Asked the AI to update `app.py` to wire `detect_conflicts()` and `sort_by_time()` into the display, replacing manual lambda sorts and plain `st.table` calls.
- **Documentation phase:** Used the AI to draft the Features list and the "Testing PawPal+" README section, then reviewed and kept only what matched the actual code.

The most effective prompts were specific ones: "given these method signatures, what are the edge cases" and "replace this inline sort with the scheduler's sort_by_time() method." Vague prompts like "improve the app" produced suggestions that went beyond scope.

**b. Judgment and verification**

During the test-writing phase, the AI initially suggested a test for duration-overlap conflicts (e.g. a 60-minute task at 8:00 AM conflicting with a 30-minute task at 8:30 AM). I rejected this because `detect_conflicts()` only compares `start_time` values — it does not do any duration math. Adding a test for behavior the code does not implement would have made the test suite misleading. Instead, I kept the limitation as a comment in the test file and in the README confidence rating, which is more honest than either deleting the concern or testing something that would always fail.

**c. Separate chat sessions for different phases**

Using a separate session for each phase (design → tests → UI → documentation) kept the context focused. When working on tests, the conversation only contained the class definitions and existing test file — there was no noise from earlier UI discussions. When switching to the UI phase, the session started fresh with just `app.py` and `pawpal_system.py`. This made the AI's suggestions more targeted and made it easier to review what changed, because each session had a single clear goal rather than a long history of unrelated decisions.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers five areas across 25 tests:

- **Sorting:** `sort_by_time()` returns tasks in chronological order; tasks without a `start_time` go last; `generate_schedule()` orders by priority then duration.
- **Recurrence:** Daily tasks produce a next-day task; weekly tasks produce a +7-day task; one-off tasks return `None`; `complete_task()` auto-adds the next occurrence.
- **Conflict detection:** Same-pet and cross-pet conflicts at identical start times; completed and untimed tasks are correctly ignored; no false positives at different times.
- **Edge cases:** Required tasks bypass a zero-minute budget; duplicate tasks are silently ignored; invalid duration and recurrence values raise `ValueError`.
- **Filtering:** `filter_tasks` by completion status, by pet name, and by both combined; `carry_forward_required` skips completed tasks.

These tests mattered because the scheduler's correctness depends on several interacting rules. A bug in the sort key or the recurrence `timedelta` would be invisible without explicit tests.

**b. Confidence**

4 out of 5. The core scheduling behaviors are all tested and passing. The one gap is duration-overlap conflict detection — a 60-minute task starting at 8:00 AM and a 30-minute task starting at 8:30 AM would not be flagged. If I had more time I would implement duration-aware conflict detection and add tests for that scenario, as well as tests for multi-day scheduling with `carry_forward_required` across consecutive dates.

---

## 5. Reflection

**a. What went well**

The separation between the scheduler logic (`pawpal_system.py`) and the UI (`app.py`) worked well. Because `DailySchedule` owned all the scheduling methods, wiring the UI was mostly a matter of calling the right method and choosing the right Streamlit component to display the result. There was no scheduling logic scattered through `app.py`, which made both files easier to read and test independently.

**b. What you would improve**

The conflict detection logic. Right now it only catches tasks at the exact same `start_time`. A real pet scheduler should flag duration overlaps — if a walk takes 60 minutes and a grooming appointment starts 30 minutes later, that is a real conflict. I would replace the current exact-match check with an interval overlap check: two tasks conflict if `a.start_time < b.start_time + b.duration` and `b.start_time < a.start_time + a.duration`.

**c. Key takeaway**

The most important lesson was that AI tools are most valuable when you already have a clear design. When I gave the AI a specific method signature and asked for tests, the output was accurate and useful. When I asked open-ended questions, the suggestions were often reasonable but went beyond what the project needed. Being the lead architect meant deciding what to build, setting the scope, and evaluating every suggestion against that scope — not just accepting whatever the AI produced. The AI accelerated the work; the design decisions still had to come from me.
