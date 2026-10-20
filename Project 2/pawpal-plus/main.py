"""Command-line demonstration of the PawPal+ scheduling logic."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner(plan_date: date) -> Owner:
    """Create sample data for two pets with deliberately unordered tasks."""
    owner = Owner("Jordan", preferences="Finish medication tasks before work.")
    mochi = owner.add_pet(Pet("Mochi", "dog", "Shiba Inu"))
    luna = owner.add_pet(Pet("Luna", "cat", "Domestic shorthair"))

    mochi.add_task(
        Task("Evening walk", "18:00", 30, "medium", "daily", plan_date)
    )
    luna.add_task(Task("Morning medication", "08:00", 10, "high", "daily", plan_date))
    mochi.add_task(Task("Breakfast", "08:00", 15, "medium", "daily", plan_date))
    luna.add_task(Task("Play session", "12:30", 20, "low", "once", plan_date))
    return owner


def main() -> None:
    """Print sorted tasks, conflict warnings, and the generated daily plan."""
    plan_date = date.today()
    owner = build_demo_owner(plan_date)
    scheduler = Scheduler(owner)

    print(f"PawPal+ schedule for {owner.name} — {plan_date:%B %d, %Y}")
    print("\nToday's tasks (chronological):")
    for pet, task in scheduler.sort_by_time(scheduler.filter_tasks(on_date=plan_date)):
        print(
            f"  {task.time} — {pet.name}: {task.description} "
            f"({task.duration_minutes} min) [{task.priority}]"
        )

    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts(plan_date)
    for warning in conflicts:
        print(f"  WARNING: {warning}")

    print("\nGenerated plan (higher priority wins a conflict):")
    for pet, task, reason in scheduler.generate_daily_plan(plan_date, "07:00", "20:00"):
        print(f"  {task.time} — {pet.name}: {task.description} | {reason}")

    slot = scheduler.next_available_slot(plan_date, 25, "07:00", "20:00")
    print(f"\nNext open 25-minute slot: {slot or 'No slot available'}")


if __name__ == "__main__":
    main()
