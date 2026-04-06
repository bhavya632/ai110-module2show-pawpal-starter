from pawpal_system import Priority, Owner, Pet, Task, DailySchedule
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

with st.expander("Welcome to the PawPal+", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, age=30, occupation="")

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed", value="Shiba Inu")
    age = st.number_input("Age", min_value=0, value=2)
    gender = st.selectbox("Gender", ["Male", "Female"])
    pet_submitted = st.form_submit_button("Add Pet")

if pet_submitted:
    new_pet = Pet(name=pet_name, breed=breed, age=int(age), gender=gender, owner=st.session_state.owner)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.pet = new_pet
    st.success(f"{pet_name} added!")

if st.session_state.owner.pets:
    st.write("Your pets:")
    st.dataframe(
        [{"Name": p.name, "Breed": p.breed, "Age": p.age, "Gender": p.gender}
         for p in st.session_state.owner.pets],
        use_container_width=True,
        hide_index=True,
    )

if "pet" not in st.session_state:
    st.info("Add a pet above before scheduling tasks.")
    st.stop()

st.divider()

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    start_time_input = st.time_input("Start time", value=None, help="Optional. Used to sort tasks chronologically.")
with col5:
    required = st.checkbox("Required", value=False, help="Required tasks (e.g. feeding, medication) always appear in the schedule.")

if st.button("Add task"):
    existing_titles = [t["title"] for t in st.session_state.tasks if t["pet"] == st.session_state.pet.name]
    if task_title in existing_titles:
        st.warning(f'"{task_title}" is already scheduled for {st.session_state.pet.name}.')
    else:
        task = Task(
            title=task_title,
            duration=int(duration),
            priority=Priority[priority.upper()],
            pet=st.session_state.pet,
            required=required,
            start_time=start_time_input,
        )
        st.session_state.pet.add_task(task)
        st.session_state.owner.schedule.add_task(task)
        st.session_state.tasks.append(
            {
                "title": task_title,
                "duration_minutes": int(duration),
                "priority": priority,
                "start_time": start_time_input.strftime("%I:%M %p") if start_time_input else "—",
                "required": "Yes" if required else "No",
                "pet": st.session_state.pet.name,
            }
        )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.dataframe(
        st.session_state.tasks,
        use_container_width=True,
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Task"),
            "duration_minutes": st.column_config.NumberColumn("Duration (min)"),
            "priority": st.column_config.TextColumn("Priority"),
            "start_time": st.column_config.TextColumn("Start Time"),
            "required": st.column_config.TextColumn("Required"),
            "pet": st.column_config.TextColumn("Pet"),
        },
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Filter Tasks")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    status_filter = st.selectbox("Completion status", ["All", "Incomplete", "Completed"])
with filter_col2:
    pet_names = ["All"] + [p.name for p in st.session_state.owner.pets]
    pet_filter = st.selectbox("Pet", pet_names)

if st.button("Apply filter"):
    schedule = st.session_state.owner.schedule
    completed_arg = None if status_filter == "All" else (status_filter == "Completed")
    pet_arg = None if pet_filter == "All" else pet_filter
    filtered = schedule.filter_tasks(completed=completed_arg, pet_name=pet_arg)

    if not filtered:
        st.info("No tasks match the selected filters.")
    else:
        st.success(f"{len(filtered)} task(s) found.")
        st.dataframe(
            [
                {
                    "Task": t.title,
                    "Pet": t.pet.name,
                    "Priority": t.priority.value.capitalize(),
                    "Duration (min)": t.duration,
                    "Start Time": t.start_time.strftime("%I:%M %p") if t.start_time else "—",
                    "Required": "Yes" if t.required else "No",
                    "Done": "Yes" if t.completed else "No",
                }
                for t in filtered
            ],
            use_container_width=True,
            hide_index=True,
        )

st.divider()

st.subheader("Build Schedule")

available_minutes = st.number_input(
    "Your available time today (minutes)",
    min_value=1,
    max_value=1440,
    value=120,
    help="The scheduler will fit as many tasks as possible within this time budget.",
)

# Overload warning shown before generating
schedule = st.session_state.owner.schedule
incomplete_tasks = [t for t in schedule.tasks if not t.completed]
total_minutes = sum(t.duration for t in incomplete_tasks)
if incomplete_tasks:
    if total_minutes > available_minutes:
        st.warning(
            f"You have {total_minutes} min of pet tasks but only {available_minutes} min available. "
            "Some tasks will be left out — mark lower-priority tasks as optional so the scheduler can skip them."
        )
    else:
        st.success(f"All {total_minutes} min of tasks fit within your {available_minutes} min budget.")

if st.button("Generate schedule"):
    if not schedule.tasks:
        st.info("No tasks added yet.")
    else:
        fitted = schedule.generate_schedule(available_minutes)

        if not fitted:
            st.warning("No tasks fit within your available time.")
        else:
            # --- Conflict detection -------------------------------------------
            # Build a temporary schedule from only the fitted tasks so that
            # detect_conflicts() runs on exactly what will be shown to the owner.
            fitted_schedule = DailySchedule(schedule.day)
            for t in fitted:
                fitted_schedule.add_task(t)

            # Sort chronologically using the Scheduler's sort_by_time() method.
            fitted_schedule.sort_by_time()

            conflicts = fitted_schedule.detect_conflicts()
            if conflicts:
                st.error(
                    "**Scheduling conflicts detected** — two or more tasks overlap. "
                    "Adjust their start times before your day begins."
                )
                for msg in conflicts:
                    # Extract the time portion for the suggestion line.
                    # Message format: "CONFLICT: 'A' ... at HH:MM AM/PM."
                    at_idx = msg.rfind(" at ")
                    conflict_time = msg[at_idx + 4:].rstrip(".") if at_idx != -1 else "that time"
                    st.warning(
                        f"{msg}\n\n"
                        f"**Fix:** Open the task list above and change one of these tasks "
                        f"to a different start time so nothing overlaps at {conflict_time}."
                    )
            else:
                st.success("No conflicts — your schedule is clear!")

            # --- Schedule table ----------------------------------------------
            st.markdown(f"### Today's Schedule — {fitted_schedule.day.strftime('%A, %B %d')}")

            rows = []
            for task in fitted_schedule.tasks:
                rows.append({
                    "Task": task.title,
                    "Pet": task.pet.name,
                    "Priority": task.priority.value.capitalize(),
                    "Duration (min)": task.duration,
                    "Start Time": task.start_time.strftime("%I:%M %p") if task.start_time else "—",
                    "Required": "Yes" if task.required else "No",
                })

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Task": st.column_config.TextColumn("Task", width="medium"),
                    "Pet": st.column_config.TextColumn("Pet"),
                    "Priority": st.column_config.TextColumn("Priority"),
                    "Duration (min)": st.column_config.NumberColumn("Duration (min)"),
                    "Start Time": st.column_config.TextColumn("Start Time"),
                    "Required": st.column_config.TextColumn("Required"),
                },
            )

            # --- Summary row -------------------------------------------------
            scheduled_minutes = sum(t.duration for t in fitted_schedule.tasks)
            skipped = [t for t in incomplete_tasks if t not in fitted]
            st.caption(
                f"Scheduled: {scheduled_minutes} min across {len(fitted_schedule.tasks)} task(s) "
                f"| Skipped: {len(skipped)} task(s)"
            )

            if skipped:
                with st.expander("Skipped tasks (did not fit in your time budget)"):
                    for t in skipped:
                        st.markdown(f"- **{t.title}** — {t.duration} min, {t.priority.value} priority")
