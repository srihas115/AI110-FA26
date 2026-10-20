"""Streamlit interface for the PawPal+ pet-care scheduler."""

from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


def seed_demo_data(owner: Owner) -> None:
    """Populate the current session with a small two-pet demonstration."""
    owner.pets.clear()
    today = date.today()
    mochi = owner.add_pet(Pet("Mochi", "dog", "Shiba Inu", "Prefers shorter walks."))
    luna = owner.add_pet(Pet("Luna", "cat", "Domestic shorthair"))
    mochi.add_task(Task("Breakfast", "08:00", 15, "medium", "daily", today))
    mochi.add_task(Task("Evening walk", "18:00", 30, "high", "daily", today))
    luna.add_task(Task("Morning medication", "08:00", 10, "high", "daily", today))
    luna.add_task(Task("Play session", "12:30", 20, "low", "once", today))


def task_rows(entries: list[tuple[Pet, Task]]) -> list[dict[str, object]]:
    """Convert task entries to records suitable for a Streamlit table."""
    return [
        {
            "Pet": pet.name,
            "Date": task.due_date.isoformat(),
            "Time": task.time,
            "Task": task.description,
            "Minutes": task.duration_minutes,
            "Priority": task.priority.title(),
            "Frequency": task.frequency.title(),
            "Status": "Complete" if task.completed else "Open",
        }
        for pet, task in entries
    ]


if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption("A multi-pet care planner with priorities, recurrence, and conflict detection.")

with st.sidebar:
    st.header("Owner profile")
    with st.form("owner_form"):
        owner_name = st.text_input("Owner name", value=owner.name)
        owner_preferences = st.text_area("Preferences", value=owner.preferences)
        if st.form_submit_button("Save profile", width="stretch"):
            if owner_name.strip():
                owner.name = owner_name.strip()
                owner.preferences = owner_preferences.strip()
                st.success("Profile saved.")
            else:
                st.error("Owner name cannot be empty.")

    st.divider()
    if st.button("Load demo data", width="stretch"):
        seed_demo_data(owner)
        st.rerun()
    if st.button("Clear pets and tasks", width="stretch"):
        owner.pets.clear()
        st.rerun()

total_tasks = owner.get_all_tasks()
open_tasks = scheduler.filter_tasks(completed=False)
metric_one, metric_two, metric_three = st.columns(3)
metric_one.metric("Pets", len(owner.pets))
metric_two.metric("Open tasks", len(open_tasks))
metric_three.metric("Completed", len(total_tasks) - len(open_tasks))

pets_tab, tasks_tab, plan_tab = st.tabs(["Pets", "Tasks", "Daily plan"])

with pets_tab:
    left, right = st.columns([1, 1.3])
    with left:
        st.subheader("Add a pet")
        with st.form("add_pet_form", clear_on_submit=True):
            pet_name = st.text_input("Pet name")
            species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
            breed = st.text_input("Breed (optional)")
            pet_preferences = st.text_area("Care preferences (optional)")
            if st.form_submit_button("Add pet", width="stretch"):
                try:
                    owner.add_pet(Pet(pet_name, species, breed, pet_preferences))
                    st.success(f"Added {pet_name.strip()}.")
                except (TypeError, ValueError) as exc:
                    st.error(str(exc))

    with right:
        st.subheader("Your pets")
        if not owner.pets:
            st.info("Add your first pet, or load the demo data from the sidebar.")
        for pet in owner.pets:
            task_word = "task" if len(pet.tasks) == 1 else "tasks"
            with st.expander(f"{pet.name} · {pet.species.title()} · {len(pet.tasks)} {task_word}"):
                st.write(f"**Breed:** {pet.breed or 'Not specified'}")
                st.write(f"**Preferences:** {pet.preferences or 'None recorded'}")

with tasks_tab:
    if not owner.pets:
        st.info("Add a pet before creating care tasks.")
    else:
        st.subheader("Schedule a task")
        with st.form("add_task_form", clear_on_submit=True):
            first, second, third = st.columns(3)
            with first:
                selected_pet = st.selectbox("Pet", [pet.name for pet in owner.pets])
                description = st.text_input("Task description", placeholder="Morning walk")
                task_date = st.date_input("Due date", value=date.today())
            with second:
                task_time = st.time_input("Start time", value=time(8, 0))
                duration = st.number_input(
                    "Duration (minutes)", min_value=1, max_value=480, value=20
                )
            with third:
                priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
                frequency = st.selectbox("Repeat", ["once", "daily", "weekly"])
                notes = st.text_input("Notes (optional)")

            if st.form_submit_button("Add task", width="stretch"):
                try:
                    task = Task(
                        description=description,
                        time=task_time.strftime("%H:%M"),
                        duration_minutes=int(duration),
                        priority=priority,
                        frequency=frequency,
                        due_date=task_date,
                        notes=notes,
                    )
                    pet = owner.get_pet(selected_pet)
                    if pet is None:
                        raise ValueError("selected pet no longer exists")
                    pet.add_task(task)
                    st.success(f"Scheduled '{task.description}' for {pet.name}.")
                except (TypeError, ValueError) as exc:
                    st.error(str(exc))

        st.divider()
        st.subheader("Browse tasks")
        filter_one, filter_two = st.columns(2)
        with filter_one:
            pet_filter = st.selectbox(
                "Filter by pet", ["All pets", *[pet.name for pet in owner.pets]]
            )
        with filter_two:
            status_filter = st.selectbox("Filter by status", ["All", "Open", "Complete"])
        completed_filter = {"All": None, "Open": False, "Complete": True}[status_filter]
        visible_tasks = scheduler.sort_by_time(
            scheduler.filter_tasks(pet_name=pet_filter, completed=completed_filter)
        )
        if visible_tasks:
            st.dataframe(task_rows(visible_tasks), width="stretch", hide_index=True)
        else:
            st.info("No tasks match these filters.")

        if total_tasks:
            st.divider()
            st.subheader("Edit, complete, or delete")
            labels = {
                f"{pet.name} · {task.due_date} {task.time} · {task.description} · {task.task_id[:6]}": (
                    pet,
                    task,
                )
                for pet, task in scheduler.sort_by_time()
            }
            chosen_label = st.selectbox("Task to manage", list(labels))
            chosen_pet, chosen_task = labels[chosen_label]
            edit_key = chosen_task.task_id

            with st.form("edit_task_form"):
                edit_one, edit_two, edit_three = st.columns(3)
                with edit_one:
                    edit_description = st.text_input(
                        "Description",
                        value=chosen_task.description,
                        key=f"edit_description_{edit_key}",
                    )
                    edit_date = st.date_input(
                        "Date", value=chosen_task.due_date, key=f"edit_date_{edit_key}"
                    )
                with edit_two:
                    edit_time = st.time_input(
                        "Time",
                        value=time.fromisoformat(chosen_task.time),
                        key=f"edit_time_{edit_key}",
                    )
                    edit_duration = st.number_input(
                        "Minutes",
                        min_value=1,
                        max_value=480,
                        value=chosen_task.duration_minutes,
                        key=f"edit_duration_{edit_key}",
                    )
                with edit_three:
                    edit_priority = st.selectbox(
                        "Priority",
                        ["low", "medium", "high"],
                        index=["low", "medium", "high"].index(chosen_task.priority),
                        key=f"edit_priority_{edit_key}",
                    )
                    edit_frequency = st.selectbox(
                        "Repeat",
                        ["once", "daily", "weekly"],
                        index=["once", "daily", "weekly"].index(chosen_task.frequency),
                        key=f"edit_frequency_{edit_key}",
                    )
                edit_notes = st.text_input(
                    "Notes", value=chosen_task.notes, key=f"edit_notes_{edit_key}"
                )
                if st.form_submit_button("Save task changes", width="stretch"):
                    try:
                        chosen_pet.update_task(
                            chosen_task.task_id,
                            description=edit_description,
                            time=edit_time.strftime("%H:%M"),
                            duration_minutes=int(edit_duration),
                            priority=edit_priority,
                            frequency=edit_frequency,
                            due_date=edit_date,
                            notes=edit_notes,
                        )
                        st.success("Task updated.")
                    except (TypeError, ValueError) as exc:
                        st.error(str(exc))

            action_one, action_two = st.columns(2)
            with action_one:
                if st.button(
                    "Mark complete",
                    disabled=chosen_task.completed,
                    width="stretch",
                ):
                    next_task = scheduler.mark_task_complete(
                        chosen_pet.name, chosen_task.task_id
                    )
                    if next_task:
                        st.success(
                            f"Completed. Next occurrence: {next_task.due_date} at {next_task.time}."
                        )
                    else:
                        st.success("Task marked complete.")
                    st.rerun()
            with action_two:
                if st.button("Delete task", type="secondary", width="stretch"):
                    chosen_pet.remove_task(chosen_task.task_id)
                    st.rerun()

with plan_tab:
    st.subheader("Build a conflict-aware daily plan")
    if not owner.pets:
        st.info("Add pets and tasks to generate a plan.")
    else:
        plan_one, plan_two, plan_three, plan_four = st.columns(4)
        with plan_one:
            plan_date = st.date_input("Plan date", value=date.today(), key="plan_date")
        with plan_two:
            plan_start = st.time_input("Available from", value=time(6, 0))
        with plan_three:
            plan_end = st.time_input("Available until", value=time(22, 0))
        with plan_four:
            plan_pet = st.selectbox(
                "Include", ["All pets", *[pet.name for pet in owner.pets]], key="plan_pet"
            )

        conflicts = scheduler.detect_conflicts(plan_date)
        if conflicts:
            for warning in conflicts:
                st.warning(f"⚠️ {warning}")
        else:
            st.success("No open-task conflicts detected for this date.")

        if st.button("Generate schedule", type="primary", width="stretch"):
            try:
                plan = scheduler.generate_daily_plan(
                    plan_date,
                    plan_start.strftime("%H:%M"),
                    plan_end.strftime("%H:%M"),
                    plan_pet,
                )
                if not plan:
                    st.info("No open tasks fit the selected date and availability window.")
                else:
                    st.markdown(f"### {plan_date:%A, %B %d} plan")
                    st.dataframe(
                        [
                            {
                                "Time": task.time,
                                "Pet": pet.name,
                                "Task": task.description,
                                "Minutes": task.duration_minutes,
                                "Priority": task.priority.title(),
                                "Why included": reason,
                            }
                            for pet, task, reason in plan
                        ],
                        width="stretch",
                        hide_index=True,
                    )
                    if conflicts:
                        st.caption(
                            "When tasks overlap, the plan keeps the higher-priority task. "
                            "Ties favor the earlier or shorter task."
                        )
            except ValueError as exc:
                st.error(str(exc))

        st.divider()
        with st.expander("Find the next available slot"):
            requested_minutes = st.number_input(
                "Needed minutes", min_value=1, max_value=240, value=30
            )
            if st.button("Find slot"):
                try:
                    slot = scheduler.next_available_slot(
                        plan_date,
                        int(requested_minutes),
                        plan_start.strftime("%H:%M"),
                        plan_end.strftime("%H:%M"),
                    )
                    if slot:
                        st.success(f"The next available slot begins at {slot}.")
                    else:
                        st.warning("No long-enough slot exists in this window.")
                except ValueError as exc:
                    st.error(str(exc))
