import streamlit as st
import pandas as pd

from models.subject import Subject
from ai.scheduler import generate_schedule
from utils.visualization import create_study_chart
from utils.progress_tracker import get_study_stats, load_progress


def planner_tab():
    st.header("AI Study Planner")

    # Show streak at top
    stats = get_study_stats()
    if stats['streak'] > 0:
        st.success(f"🔥 You're on a {stats['streak']}-day study streak! Keep it up!")

    subjects = []

    num_subjects = st.number_input("Number of subjects", 1, 10, value=1)

    for i in range(int(num_subjects)):
        st.markdown(f"### Subject {i + 1}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            name = st.text_input(f"Name", key=f"name{i}", placeholder=f"Subject {i + 1}")
        with col2:
            marks = st.number_input(f"Marks (0-100)", 0, 100, 50, key=f"marks{i}")
        with col3:
            exam = st.number_input(f"Days to exam", 1, 365, 7, key=f"exam{i}")
        with col4:
            difficulty = st.slider(f"Difficulty (1-5)", 1, 5, 3, key=f"diff{i}")

        if name and name.strip() != "":
            subjects.append(Subject(name.strip(), marks, exam, difficulty))

        st.markdown("---")

    hours = st.number_input("Daily study hours", 1, 24, 6, key="hours_input")

    if st.button("Generate Study Plan"):
        if len(subjects) == 0:
            st.warning("⚠️ Please enter at least one subject name.")
            return

        if len(subjects) < int(num_subjects):
            st.warning(f"⚠️ You selected {int(num_subjects)} subjects but only entered {len(subjects)} names.")
            return

        schedule = generate_schedule(subjects, hours)

        if len(schedule) == 0:
            st.warning("No schedule generated. Check inputs.")
            return

        data = []
        names = []
        hrs = []

        for s in schedule:
            data.append({
                "Subject": s.name,
                "Marks": s.marks,
                "Days Left": s.exam_days,
                "Difficulty": s.difficulty,
                "Priority Score": round(s.priority, 2),
                "Study Hours": round(s.study_hours, 2)
            })

            names.append(s.name)
            hrs.append(s.study_hours)

        df = pd.DataFrame(data)

        total_allocated = sum(hrs)

        st.success(f"✅ Study Plan Generated for {len(subjects)} Subjects!")
        st.markdown(f"**Daily Hours:** {hours} | **Total Allocated:** {total_allocated:.1f}")

        st.dataframe(df, use_container_width=True)

        if len(names) > 0:
            fig = create_study_chart(names, hrs)
            st.pyplot(fig)
        else:
            st.warning("Graph cannot be generated.")

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Subjects", len(subjects))
        with col2:
            st.metric("Daily Hours Available", hours)
        with col3:
            st.metric("Total Hours Allocated", f"{total_allocated:.1f}")

        # Progress info
        st.markdown("---")
        st.info(
            "💡 **Track your progress in the Chatbot tab!** Log daily study hours, maintain your streak, and get rescheduling suggestions.")