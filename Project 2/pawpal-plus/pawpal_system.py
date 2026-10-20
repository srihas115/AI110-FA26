"""Core object-oriented models and scheduling logic for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Iterable, Optional
from uuid import uuid4


VALID_PRIORITIES = ("low", "medium", "high")
VALID_FREQUENCIES = ("once", "daily", "weekly")
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


def _time_to_minutes(value: str) -> int:
    """Convert a validated HH:MM value to minutes after midnight."""
    try:
        parsed = datetime.strptime(value, "%H:%M")
    except ValueError as exc:
        raise ValueError("time must use 24-hour HH:MM format") from exc
    return parsed.hour * 60 + parsed.minute


@dataclass
class Task:
    """Represent one scheduled pet-care activity."""

    description: str
    time: str
    duration_minutes: int = 30
    priority: str = "medium"
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    notes: str = ""
    task_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        """Normalize and validate task data."""
        self.description = self.description.strip()
        self.priority = self.priority.strip().lower()
        self.frequency = self.frequency.strip().lower()
        self.notes = self.notes.strip()

        if not self.description:
            raise ValueError("description cannot be empty")
        _time_to_minutes(self.time)
        if (
            isinstance(self.duration_minutes, bool)
            or not isinstance(self.duration_minutes, int)
            or self.duration_minutes <= 0
        ):
            raise ValueError("duration_minutes must be a positive integer")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of: {', '.join(VALID_PRIORITIES)}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of: {', '.join(VALID_FREQUENCIES)}")
        if not isinstance(self.due_date, date):
            raise TypeError("due_date must be a datetime.date")

    @property
    def end_minutes(self) -> int:
        """Return the task's ending minute after midnight."""
        return _time_to_minutes(self.time) + self.duration_minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional[Task]:
        """Create the next daily or weekly occurrence, if applicable."""
        days = {"daily": 1, "weekly": 7}.get(self.frequency)
        if days is None:
            return None
        return replace(
            self,
            due_date=self.due_date + timedelta(days=days),
            completed=False,
            task_id=uuid4().hex,
        )


@dataclass
class Pet:
    """Store a pet's profile and care tasks."""

    name: str
    species: str
    breed: str = ""
    preferences: str = ""
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize and validate pet profile data."""
        self.name = self.name.strip()
        self.species = self.species.strip().lower()
        self.breed = self.breed.strip()
        self.preferences = self.preferences.strip()
        if not self.name:
            raise ValueError("pet name cannot be empty")
        if not self.species:
            raise ValueError("species cannot be empty")

    def add_task(self, task: Task) -> Task:
        """Add a Task to this pet and return it."""
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance")
        self.tasks.append(task)
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Find a task by its stable identifier."""
        return next((task for task in self.tasks if task.task_id == task_id), None)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by identifier and report whether it was found."""
        task = self.get_task(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        return True

    def update_task(self, task_id: str, **changes: object) -> Task:
        """Update editable task fields while preserving its identifier."""
        task = self.get_task(task_id)
        if task is None:
            raise ValueError("task not found")

        editable = {
            "description",
            "time",
            "duration_minutes",
            "priority",
            "frequency",
            "due_date",
            "notes",
        }
        unknown = set(changes) - editable
        if unknown:
            raise ValueError(f"unsupported task fields: {', '.join(sorted(unknown))}")

        candidate = replace(task, **changes)
        for attribute in editable:
            setattr(task, attribute, getattr(candidate, attribute))
        return task


@dataclass
class Owner:
    """Manage an owner's profile and collection of pets."""

    name: str
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize and validate owner data."""
        self.name = self.name.strip()
        self.preferences = self.preferences.strip()
        if not self.name:
            raise ValueError("owner name cannot be empty")

    def add_pet(self, pet: Pet) -> Pet:
        """Add a uniquely named pet and return it."""
        if not isinstance(pet, Pet):
            raise TypeError("pet must be a Pet instance")
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"a pet named {pet.name!r} already exists")
        self.pets.append(pet)
        return pet

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name without case sensitivity."""
        normalized = name.strip().casefold()
        return next((pet for pet in self.pets if pet.name.casefold() == normalized), None)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return tasks from every pet as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


TaskEntry = tuple[Pet, Task]
PlanEntry = tuple[Pet, Task, str]


class Scheduler:
    """Organize, filter, and plan tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler connected to one owner."""
        if not isinstance(owner, Owner):
            raise TypeError("owner must be an Owner instance")
        self.owner = owner

    def filter_tasks(
        self,
        *,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        on_date: Optional[date] = None,
    ) -> list[TaskEntry]:
        """Filter all owner tasks by pet, completion state, and date."""
        entries = self.owner.get_all_tasks()
        if pet_name and pet_name != "All pets":
            target = pet_name.strip().casefold()
            entries = [(pet, task) for pet, task in entries if pet.name.casefold() == target]
        if completed is not None:
            entries = [(pet, task) for pet, task in entries if task.completed is completed]
        if on_date is not None:
            entries = [(pet, task) for pet, task in entries if task.due_date == on_date]
        return entries

    def sort_by_time(self, tasks: Optional[Iterable[TaskEntry]] = None) -> list[TaskEntry]:
        """Return task entries in chronological order with priority as a tie-breaker."""
        entries = list(self.owner.get_all_tasks() if tasks is None else tasks)
        return sorted(
            entries,
            key=lambda entry: (
                entry[1].due_date,
                _time_to_minutes(entry[1].time),
                -PRIORITY_RANK[entry[1].priority],
                entry[0].name.casefold(),
            ),
        )

    def detect_conflicts(self, on_date: Optional[date] = None) -> list[str]:
        """Return warnings for overlapping unfinished tasks across all pets."""
        entries = self.sort_by_time(self.filter_tasks(completed=False, on_date=on_date))
        warnings: list[str] = []
        for index, (left_pet, left_task) in enumerate(entries):
            left_start = _time_to_minutes(left_task.time)
            for right_pet, right_task in entries[index + 1 :]:
                if right_task.due_date != left_task.due_date:
                    break
                right_start = _time_to_minutes(right_task.time)
                if right_start >= left_task.end_minutes:
                    break
                if left_start < right_task.end_minutes and right_start < left_task.end_minutes:
                    warnings.append(
                        f"{left_task.due_date:%b %d}: {left_pet.name}'s "
                        f"'{left_task.description}' overlaps {right_pet.name}'s "
                        f"'{right_task.description}'."
                    )
        return warnings

    def mark_task_complete(self, pet_name: str, task_id: str) -> Optional[Task]:
        """Complete a task and add its next recurrence to the same pet."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"pet {pet_name!r} not found")
        task = pet.get_task(task_id)
        if task is None:
            raise ValueError("task not found")
        if task.completed:
            return None

        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def generate_daily_plan(
        self,
        on_date: date,
        available_start: str = "06:00",
        available_end: str = "22:00",
        pet_name: Optional[str] = None,
    ) -> list[PlanEntry]:
        """Choose non-overlapping tasks in a time window, favoring higher priority."""
        window_start = _time_to_minutes(available_start)
        window_end = _time_to_minutes(available_end)
        if window_start >= window_end:
            raise ValueError("available_start must be before available_end")

        candidates = self.filter_tasks(
            pet_name=pet_name,
            completed=False,
            on_date=on_date,
        )
        candidates = [
            entry
            for entry in candidates
            if _time_to_minutes(entry[1].time) >= window_start
            and entry[1].end_minutes <= window_end
        ]
        candidates.sort(
            key=lambda entry: (
                -PRIORITY_RANK[entry[1].priority],
                _time_to_minutes(entry[1].time),
                entry[1].duration_minutes,
            )
        )

        selected: list[TaskEntry] = []
        for entry in candidates:
            task = entry[1]
            start = _time_to_minutes(task.time)
            overlaps = any(
                start < chosen.end_minutes
                and _time_to_minutes(chosen.time) < task.end_minutes
                for _, chosen in selected
            )
            if not overlaps:
                selected.append(entry)

        selected = self.sort_by_time(selected)
        return [
            (
                pet,
                task,
                f"Included because it is {task.priority} priority and fits the available window.",
            )
            for pet, task in selected
        ]

    def next_available_slot(
        self,
        on_date: date,
        duration_minutes: int,
        available_start: str = "06:00",
        available_end: str = "22:00",
    ) -> Optional[str]:
        """Find the earliest free slot across all pets for the requested duration."""
        if (
            isinstance(duration_minutes, bool)
            or not isinstance(duration_minutes, int)
            or duration_minutes <= 0
        ):
            raise ValueError("duration_minutes must be positive")
        cursor = _time_to_minutes(available_start)
        window_end = _time_to_minutes(available_end)
        if cursor >= window_end:
            raise ValueError("available_start must be before available_end")

        entries = self.sort_by_time(self.filter_tasks(completed=False, on_date=on_date))
        for _, task in entries:
            task_start = _time_to_minutes(task.time)
            if task.end_minutes <= cursor:
                continue
            if task_start - cursor >= duration_minutes:
                break
            cursor = max(cursor, task.end_minutes)

        if cursor + duration_minutes > window_end:
            return None
        hours, minutes = divmod(cursor, 60)
        return f"{hours:02d}:{minutes:02d}"
