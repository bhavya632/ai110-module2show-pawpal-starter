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
    st.table([{"name": p.name, "breed": p.breed, "age": p.age, "gender": p.gender} for p in st.session_state.owner.pets])

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
    st.table(st.session_state.tasks)
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
        st.write(f"{len(filtered)} task(s) found:")
        st.table([
            {
                "title": t.title,
                "pet": t.pet.name,
                "priority": t.priority.value,
                "duration_minutes": t.duration,
                "start_time": t.start_time.strftime("%I:%M %p") if t.start_time else "—",
                "required": "Yes" if t.required else "No",
                "completed": "Yes" if t.completed else "No",
            }
            for t in filtered
        ])

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
            st.markdown(f"### Today's Schedule ({schedule.day})")

            # Sort fitted tasks by start_time (None times go last)
            fitted.sort(key=lambda t: (t.start_time is None, t.start_time))

            # Group by pet
            by_pet: dict[str, list] = {}
            for task in fitted:
                by_pet.setdefault(task.pet.name, []).append(task)

            for pet_name, pet_tasks in by_pet.items():
                st.markdown(f"**{pet_name}**")
                for task in pet_tasks:
                    label = " *(required)*" if task.required else ""
                    time_str = f" @ {task.start_time.strftime('%I:%M %p')}" if task.start_time else ""
                    st.markdown(
                        f"- **[{task.priority.value.upper()}]** {task.title} — {task.duration} min{time_str}{label}"
                    )

            scheduled_minutes = sum(t.duration for t in fitted)
            skipped = [t for t in incomplete_tasks if t not in fitted]
            st.caption(f"Scheduled: {scheduled_minutes} min | Skipped: {len(skipped)} task(s)")

            if skipped:
                with st.expander("Skipped tasks"):
                    for t in skipped:
                        st.markdown(f"- {t.title} ({t.duration} min, {t.priority.value})")