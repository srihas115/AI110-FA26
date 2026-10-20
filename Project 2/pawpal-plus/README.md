# PawPal+

PawPal+ is a multi-pet care planner built with Python, object-oriented design, and Streamlit. It keeps an owner's pets and tasks in one session, identifies schedule conflicts, creates recurring tasks, and builds a chronological daily plan that favors higher-priority care.

## Features

- Add multiple pets with species, breed, and care preferences.
- Add and edit tasks with a date, start time, duration, priority, and recurrence.
- Browse tasks by pet and completion status.
- Sort tasks chronologically across every pet owned by the user.
- Detect exact-time and overlapping conflicts across the household.
- Complete tasks and automatically create the next daily or weekly occurrence.
- Generate a plan inside the owner's availability window; when tasks overlap, higher priority wins.
- Find the next available time slot for a new activity.
- Verify all core behaviors with an automated pytest suite.

## Architecture

The application separates presentation from scheduling logic:

- `Task` represents one care activity and creates recurring copies.
- `Pet` stores pet details and owns that pet's task list.
- `Owner` owns multiple pets and exposes all pet tasks through `get_all_tasks()`.
- `Scheduler` reads through the `Owner`, then filters, sorts, detects conflicts, completes recurring tasks, and builds plans.
- `app.py` is the Streamlit presentation layer. The `Owner` is held in `st.session_state`, so changes survive Streamlit reruns.

The initial and final Mermaid diagrams are in `diagrams/uml_draft.mmd` and `diagrams/uml_final.mmd`.

## Project Structure

```text
pawpal-plus/
├── app.py
├── main.py
├── pawpal_system.py
├── requirements.txt
├── reflection.md
├── ai_interactions.md
├── diagrams/
│   ├── uml_draft.mmd
│   └── uml_final.mmd
└── tests/
    └── test_pawpal.py
```

## Setup and Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Run the command-line demonstration
python main.py

# Run the Streamlit interface
streamlit run app.py
```

All data is session-based for this version. Closing the Streamlit session clears it.

## Sample CLI Output

Running `python main.py` creates two pets and four deliberately unordered tasks. The two 08:00 tasks demonstrate conflict detection and priority selection.

```text
PawPal+ schedule for Jordan — October 20, 2026

Today's tasks (chronological):
  08:00 — Luna: Morning medication (10 min) [high]
  08:00 — Mochi: Breakfast (15 min) [medium]
  12:30 — Luna: Play session (20 min) [low]
  18:00 — Mochi: Evening walk (30 min) [medium]

Conflict check:
  WARNING: Oct 20: Luna's 'Morning medication' overlaps Mochi's 'Breakfast'.

Generated plan (higher priority wins a conflict):
  08:00 — Luna: Morning medication | Included because it is high priority and fits the available window.
  12:30 — Luna: Play session | Included because it is low priority and fits the available window.
  18:00 — Mochi: Evening walk | Included because it is medium priority and fits the available window.

Next open 25-minute slot: 07:00
```

## Smarter Scheduling

| Feature | Method(s) | Behavior |
|---|---|---|
| Chronological sorting | `Scheduler.sort_by_time()` | Sorts by date and `HH:MM`; priority breaks same-time ties. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet, completion status, and/or date while still reading all tasks through `Owner`. |
| Conflict detection | `Scheduler.detect_conflicts()` | Flags overlapping intervals, including conflicts between different pets. Back-to-back tasks are allowed. |
| Recurring care | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a daily or weekly task creates a fresh task one or seven days later. |
| Priority planning | `Scheduler.generate_daily_plan()` | Removes completed/out-of-window work and keeps the higher-priority task when intervals overlap. |
| Open-slot search | `Scheduler.next_available_slot()` | Scans the day's occupied intervals for the earliest gap long enough for a new task. |

The planner uses fixed start times. It resolves an overlap by keeping one task rather than moving the lower-priority task; the conflict remains visible so the owner can edit it.

## Demo Walkthrough

1. Open **Pets** and add at least two pets, or choose **Load demo data** in the sidebar.
2. Open **Tasks** to schedule care with time, duration, priority, and recurrence.
3. Use the pet and status controls to verify that tasks from the whole household can be filtered.
4. Select a task to edit it, mark it complete, or delete it. Completing a recurring task displays the date of its next occurrence.
5. Open **Daily plan**, select an availability window, and review any conflict warnings.
6. Generate the plan. Tasks appear chronologically, and each row explains why it was included.
7. Expand **Find the next available slot** to locate room for another activity.

## Testing PawPal+

Run the suite from this directory:

```bash
python -m pytest -q
```

The tests cover task completion/addition, multi-pet aggregation, chronological sorting, filtering, daily and weekly recurrence, one-time tasks, overlapping conflicts, priority conflict resolution, availability constraints, open-slot search, and invalid input.

```text
.............                                                            [100%]
13 passed in 0.03s
```

**Confidence level:** ★★★★★ (5/5). The core logic is deterministic and its main happy paths and edge cases are covered. A production version would add browser-level Streamlit tests and persistent storage tests.

