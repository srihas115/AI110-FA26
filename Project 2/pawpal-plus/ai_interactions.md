# AI Interactions Log

## Agent Workflow

**What task did you give the agent?**

I asked Codex to finish Project 2 from the attached CodePath assignment and official PawPal+ starter. The requested outcome was a complete, tested project rather than isolated code snippets.

**What did the agent do?**

- Extracted the assignment requirements from the saved course page and checked the official starter repository.
- Created `pawpal_system.py` with the `Owner`, `Pet`, `Task`, and `Scheduler` classes.
- Added sorting, filtering, overlap detection, daily/weekly recurrence, priority-based planning, and next-slot search.
- Replaced the placeholder Streamlit UI with working pet, task, editing, completion, filter, warning, and planning flows.
- Added `main.py`, 13 pytest cases, the draft/final UML source, README evidence, and this reflection.
- Ran the tests, CLI demonstration, and Python syntax compilation.

**What did you have to verify or fix manually?**

I verified that the scheduler reads tasks through `Owner.get_all_tasks()`, that recurrence creates a new ID instead of reusing a completed task, and that adjacent tasks are not reported as conflicts. I also reviewed the conflict policy: the app warns about every overlap, while the generated plan keeps the highest-priority non-overlapping work. The final verification commands and output are recorded in the README.

## Prompt Comparison

No multi-model prompt comparison was performed for this project.
