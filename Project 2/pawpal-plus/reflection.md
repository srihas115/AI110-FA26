# PawPal+ Project Reflection

## 1. System Design

### a. Initial design

The three core user actions I identified were: add a pet, schedule a care task, and view a daily household schedule. My initial UML used four classes. `Task` held the activity details and completion state, `Pet` held profile data and tasks, `Owner` managed pets, and `Scheduler` organized the data. The key relationship was that a scheduler receives an owner instead of a single pet. That lets one plan include every pet.

### b. Design changes

The first draft only modeled a task's description, time, recurrence, and status. During implementation I added duration, priority, date, notes, and a stable task ID. Duration makes overlap detection possible, priority gives the planner a defensible way to resolve conflicts, and IDs let the UI edit or complete two otherwise identical tasks safely. I also added an owner-level `get_all_tasks()` method so the scheduler never depends on one pet.

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

The scheduler considers due date, completion status, the owner's available start/end time, fixed task start time, duration, and priority. A task must be open, due on the plan date, and completely inside the availability window. The planner considers high-priority work before medium and low work. After selection, it sorts the final plan by time so it is easy to follow.

I treated medication and other high-priority care as more important than convenience tasks when schedules overlap. I kept date and availability as hard constraints because showing a completed task or a task outside the owner's available hours would make the plan misleading.

### b. Tradeoffs

Tasks have fixed start times. The planner keeps the higher-priority task during an overlap and leaves the warning visible instead of silently moving the other task. This is predictable and avoids inventing a time that may not work for the owner. The tradeoff is that a lower-priority task may be omitted until the user edits it. A future version could propose a new time by combining the conflict detector with `next_available_slot()`.

## 3. AI Collaboration

### a. How I used AI

I used Codex to turn the assignment into a checklist, inspect the starter repository, draft the class relationships, implement the backend and Streamlit wiring, and create tests. The most useful prompts were outcome-based: complete the rubric, preserve the required four-class architecture, and verify each algorithm with tests. Keeping the architecture, UI, tests, and documentation as distinct phases made the work easier to review.

### b. Judgment and verification

One design decision I did not accept in its simplest form was conflict detection based only on identical `HH:MM` strings. That would miss a 30-minute walk at 08:00 overlapping an 08:20 medication. I used interval comparison instead and added a test proving that 08:00–08:30 conflicts with 08:20–08:30 while a task beginning at 08:30 does not. I verified the complete implementation with `python -m pytest`, `py_compile`, and the CLI demo rather than trusting generated code by inspection alone.

## 4. Testing and Verification

### a. What I tested

The suite tests task completion, task addition, owner aggregation across two pets, chronological sorting, pet/status filtering, daily recurrence, weekly recurrence, one-time completion, overlap conflicts across pets, priority-based conflict resolution, availability-window filtering, next-slot discovery, and invalid task input. These behaviors cover both basic object relationships and the algorithms that are most likely to create incorrect schedules.

### b. Confidence

My confidence is 5/5 for the in-memory core. All 13 tests pass, the command-line demo exercises the multi-pet flow, and invalid data is rejected early. With more time, I would add automated browser tests for Streamlit widget interactions, persistence tests, daylight-saving/time-zone scenarios, and property-based tests that generate many random task intervals.

## 5. Reflection

### a. What went well

I am most satisfied with the separation between the backend and the UI. The same `Owner`, `Pet`, `Task`, and `Scheduler` behavior powers both `main.py` and Streamlit, so the CLI tests real application logic instead of a second implementation. The scheduler also handles multiple pets through the owner as the assignment requires.

### b. What I would improve

In another iteration, I would persist owners, pets, and tasks to JSON or a database and support multiple owners. I would also let the planner suggest a replacement time for a skipped conflicting task, while requiring the user to confirm the change.

### c. Key takeaway

The main lesson was that acting as the lead architect means defining invariants before asking AI for code. Decisions such as fixed `HH:MM` times, priority ordering, recurrence semantics, and whether touching intervals count as conflicts made the generated implementation much easier to test and explain. AI accelerated the build, but explicit constraints and human verification determined whether the result was trustworthy.

