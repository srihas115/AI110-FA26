"""Automated tests for PawPal+'s core models and scheduling algorithms."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def plan_date() -> date:
    """Return a stable date for deterministic tests."""
    return date(2026, 10, 20)


@pytest.fixture
def household(plan_date: date) -> tuple[Owner, Pet, Pet, Scheduler]:
    """Create an owner with two pets and no tasks."""
    owner = Owner("Jordan")
    mochi = owner.add_pet(Pet("Mochi", "dog"))
    luna = owner.add_pet(Pet("Luna", "cat"))
    return owner, mochi, luna, Scheduler(owner)


def test_mark_complete_changes_task_status(plan_date: date) -> None:
    task = Task("Breakfast", "08:00", due_date=plan_date)

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count(plan_date: date) -> None:
    pet = Pet("Mochi", "dog")

    pet.add_task(Task("Walk", "07:30", due_date=plan_date))

    assert len(pet.tasks) == 1
    assert pet.tasks[0].description == "Walk"


def test_owner_aggregates_tasks_from_multiple_pets(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    owner, mochi, luna, _ = household
    mochi.add_task(Task("Walk", "07:30", due_date=plan_date))
    luna.add_task(Task("Medication", "09:00", due_date=plan_date))

    entries = owner.get_all_tasks()

    assert {pet.name for pet, _ in entries} == {"Mochi", "Luna"}
    assert len(entries) == 2


def test_sorting_returns_chronological_order(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    _, mochi, luna, scheduler = household
    mochi.add_task(Task("Dinner", "18:00", due_date=plan_date))
    luna.add_task(Task("Medication", "08:00", due_date=plan_date))
    mochi.add_task(Task("Lunch walk", "12:00", due_date=plan_date))

    sorted_entries = scheduler.sort_by_time()

    assert [task.time for _, task in sorted_entries] == ["08:00", "12:00", "18:00"]


def test_filtering_by_pet_and_status(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    _, mochi, luna, scheduler = household
    completed = mochi.add_task(Task("Breakfast", "08:00", due_date=plan_date))
    completed.mark_complete()
    mochi.add_task(Task("Walk", "12:00", due_date=plan_date))
    luna.add_task(Task("Medication", "09:00", due_date=plan_date))

    results = scheduler.filter_tasks(pet_name="mochi", completed=False)

    assert len(results) == 1
    assert results[0][1].description == "Walk"


@pytest.mark.parametrize(
    ("frequency", "expected_days"), [("daily", 1), ("weekly", 7)]
)
def test_completing_recurring_task_creates_next_occurrence(
    household: tuple[Owner, Pet, Pet, Scheduler],
    plan_date: date,
    frequency: str,
    expected_days: int,
) -> None:
    _, mochi, _, scheduler = household
    original = mochi.add_task(
        Task("Medication", "08:00", frequency=frequency, due_date=plan_date)
    )

    next_task = scheduler.mark_task_complete(mochi.name, original.task_id)

    assert original.completed is True
    assert next_task is not None
    assert next_task.task_id != original.task_id
    assert next_task.completed is False
    assert next_task.due_date == plan_date + timedelta(days=expected_days)
    assert len(mochi.tasks) == 2


def test_one_time_task_does_not_recur(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    _, mochi, _, scheduler = household
    task = mochi.add_task(Task("Grooming", "15:00", due_date=plan_date))

    next_task = scheduler.mark_task_complete(mochi.name, task.task_id)

    assert next_task is None
    assert len(mochi.tasks) == 1


def test_conflict_detection_finds_overlapping_tasks_across_pets(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    _, mochi, luna, scheduler = household
    mochi.add_task(Task("Walk", "08:00", 30, due_date=plan_date))
    luna.add_task(Task("Medication", "08:20", 10, due_date=plan_date))
    luna.add_task(Task("Breakfast", "08:30", 10, due_date=plan_date))

    conflicts = scheduler.detect_conflicts(plan_date)

    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Medication" in conflicts[0]


def test_daily_plan_keeps_higher_priority_task_when_times_overlap(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    _, mochi, luna, scheduler = household
    mochi.add_task(Task("Leisure walk", "08:00", 30, "low", due_date=plan_date))
    luna.add_task(Task("Medication", "08:00", 10, "high", due_date=plan_date))
    mochi.add_task(Task("Dinner", "18:00", 15, "medium", due_date=plan_date))

    plan = scheduler.generate_daily_plan(plan_date, "07:00", "20:00")

    assert [task.description for _, task, _ in plan] == ["Medication", "Dinner"]


def test_daily_plan_excludes_completed_and_out_of_window_tasks(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    _, mochi, _, scheduler = household
    completed = mochi.add_task(Task("Breakfast", "08:00", due_date=plan_date))
    completed.mark_complete()
    mochi.add_task(Task("Midday walk", "12:00", due_date=plan_date))
    mochi.add_task(Task("Late walk", "22:00", due_date=plan_date))

    plan = scheduler.generate_daily_plan(plan_date, "09:00", "20:00")

    assert [task.description for _, task, _ in plan] == ["Midday walk"]


def test_next_available_slot_uses_gaps_between_tasks(
    household: tuple[Owner, Pet, Pet, Scheduler], plan_date: date
) -> None:
    _, mochi, luna, scheduler = household
    mochi.add_task(Task("Breakfast", "08:00", 30, due_date=plan_date))
    luna.add_task(Task("Medication", "09:00", 15, due_date=plan_date))

    slot = scheduler.next_available_slot(plan_date, 30, "08:00", "10:00")

    assert slot == "08:30"


def test_task_validation_rejects_bad_values(plan_date: date) -> None:
    with pytest.raises(ValueError, match="HH:MM"):
        Task("Walk", "8am", due_date=plan_date)
    with pytest.raises(ValueError, match="positive"):
        Task("Walk", "08:00", duration_minutes=0, due_date=plan_date)
    with pytest.raises(ValueError, match="priority"):
        Task("Walk", "08:00", priority="urgent", due_date=plan_date)
