import streamlit as st
import pandas as pd
import random
import re
from datetime import datetime, date, timedelta

from models.subject import Subject
from ai.scheduler import generate_schedule, reschedule as reschedule_function
from utils.visualization import create_study_chart, create_weekly_chart
from utils.progress_tracker import (
    log_study_session, get_missed_subjects,
    get_study_stats, load_progress, reset_progress,
    has_logged_today, get_today_logs, get_today_date
)

# -----------------------------
# ✅ Known Subjects
# -----------------------------
KNOWN_SUBJECTS = [
    "math", "os", "ai", "dbms", "cn",
    "physics", "chemistry", "biology",
    "english", "java", "python", "history",
    "geography", "economics", "accountancy"
]

# -----------------------------
# 🎨 Styling
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.stChatMessage {
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# 🧠 SMART SUBJECT DETECTION
# -----------------------------
def detect_subjects(text):
    text = text.lower()
    subjects = []

    for sub in KNOWN_SUBJECTS:
        pattern = r'\b' + re.escape(sub) + r'\b'
        if re.search(pattern, text):
            subjects.append(sub.capitalize())

    return subjects


# -----------------------------
# 🧠 EXTRACT NUMBERS
# -----------------------------
def extract_numbers(text):
    return [int(n) for n in re.findall(r'\b(\d+)\b', text)]


# -----------------------------
# 🧠 GET NEXT QUESTION
# -----------------------------
def get_next_question(data):
    subjects = data["subjects"]

    if not subjects:
        return "Which subjects are you studying? (e.g., Math, Physics, Chemistry)"

    for i, sub in enumerate(subjects):
        if i >= len(data["subject_details"]):
            return f"Enter **marks and difficulty** for **{sub}** (format: marks, difficulty)\nExample: 85, 4"

    for i, sub in enumerate(subjects):
        if i >= len(data["exam_days"]):
            return f"How many **days left** for **{sub}** exam?"

    if not data["hours"]:
        return "How many **total hours** can you study **daily**?"

    return None


# -----------------------------
# 🧠 PARSE INPUT
# -----------------------------
def parse_input(text, data):
    text_lower = text.lower()
    numbers = extract_numbers(text)

    new_subjects = detect_subjects(text)
    for sub in new_subjects:
        if sub not in data["subjects"]:
            data["subjects"].append(sub)

    if not data["subjects"]:
        return data

    current_idx = len(data["subject_details"])

    if current_idx < len(data["subjects"]) and len(numbers) >= 2:
        marks = numbers[0]
        difficulty = numbers[1]

        if 0 <= marks <= 100 and 1 <= difficulty <= 5:
            data["subject_details"].append({
                "marks": marks,
                "difficulty": difficulty
            })
            data["marks"].append(marks)

    elif len(data["subject_details"]) == len(data["subjects"]) and len(data["exam_days"]) < len(data["subjects"]):
        if len(numbers) >= 1:
            days = numbers[0]
            if 1 <= days <= 365:
                data["exam_days"].append(days)

    elif (len(data["exam_days"]) == len(data["subjects"]) and
          len(data["subject_details"]) == len(data["subjects"]) and
          not data["hours"]):
        if len(numbers) >= 1:
            hours = numbers[0]
            if 1 <= hours <= 24:
                data["hours"] = hours

    return data


# -----------------------------
# 💬 GENERATE REPLY
# -----------------------------
def generate_reply(data):
    subjects = data["subjects"]
    details_count = len(data["subject_details"])
    days_count = len(data["exam_days"])
    total_subjects = len(subjects)

    if total_subjects == 0:
        return "Which subjects are you studying? (e.g., Math, Physics, Chemistry)"

    if details_count < total_subjects:
        current_sub = subjects[details_count]
        if details_count == 0:
            subject_list = ", ".join([f"**{s}**" for s in subjects])
            return f"Great! I see you're studying {subject_list}. Enter **marks and difficulty** for **{current_sub}** (format: marks, difficulty)\nExample: 85, 4"
        else:
            return f"✓ {details_count}/{total_subjects} subjects details collected. Enter **marks and difficulty** for **{current_sub}** (format: marks, difficulty)"

    if days_count < total_subjects:
        current_sub = subjects[days_count]
        if days_count == 0:
            return f"✓ All marks & difficulty collected. How many **days left** for **{current_sub}** exam?"
        else:
            return f"✓ {days_count}/{total_subjects} exam dates collected. How many **days left** for **{current_sub}** exam?"

    if not data["hours"]:
        return "✓ All exam dates noted. How many **total hours** can you study **daily**?"

    return "🎉 Perfect! Generating your study plan with personalized suggestions..."


# -----------------------------
# 🎯 GENERATE SUGGESTIONS
# -----------------------------
def generate_suggestions(subjects, df):
    suggestions = []

    sorted_subs = sorted(subjects, key=lambda x: x.priority, reverse=True)

    weakest = sorted_subs[0]
    suggestions.append(f"🚨 **Priority Focus: {weakest.name}**\n"
                       f"   - Allocated **{weakest.study_hours:.1f} hours** (highest priority)\n"
                       f"   - Marks: {weakest.marks}/100 | "
                       f"Exam in {weakest.exam_days} days | "
                       f"Difficulty: {weakest.difficulty}/5")

    low_marks = [s for s in subjects if s.marks < 60]
    if low_marks:
        sub_names = ", ".join([s.name for s in low_marks])
        suggestions.append(f"📉 **Improvement Needed: {sub_names}**\n"
                           f"   - Scoring below 60. Focus on concept clarity and practice.")

    urgent = [s for s in subjects if s.exam_days <= 3]
    if urgent:
        sub_names = ", ".join([s.name for s in urgent])
        suggestions.append(f"⏰ **Urgent Revision: {sub_names}**\n"
                           f"   - Exam in 3 days or less. Solve past papers!")

    hard = [s for s in subjects if s.difficulty >= 4]
    if hard:
        sub_names = ", ".join([s.name for s in hard])
        suggestions.append(f"🔥 **Challenging: {sub_names}**\n"
                           f"   - Break into smaller topics, use visual aids.")

    strong = [s for s in subjects if s.marks >= 80 and s.difficulty <= 3]
    if strong:
        sub_names = ", ".join([s.name for s in strong])
        suggestions.append(f"✅ **Strong Areas: {sub_names}**\n"
                           f"   - You're doing well! Minimal revision needed.")

    total_hours = sum(s.study_hours for s in subjects)
    if total_hours > 10:
        suggestions.append("⚠️ **Warning:** Schedule exceeds 10 hours. Take breaks!")
    elif total_hours < 4:
        suggestions.append("💡 **Tip:** You can study more. Add 1-2 hours!")

    return suggestions


# -----------------------------
# 📈 PROGRESS TRACKER UI - COMPLETELY REWRITTEN FOR RELIABILITY
# -----------------------------
# -----------------------------
# 📈 PROGRESS TRACKER UI - FIXED FOR INPUT
# -----------------------------
# -----------------------------
# 📈 PROGRESS TRACKER UI - FIXED SESSION STATE ERROR
# -----------------------------
def show_progress_tracker():
    """Show progress tracker using schedule from session state"""
    st.markdown("---")
    st.markdown("### 📈 Progress Tracker & Daily Log")

    today = get_today_date()

    # Get schedule from session state
    if "current_schedule" not in st.session_state or st.session_state["current_schedule"] is None:
        st.error("No active schedule found. Please generate a plan first.")
        return

    schedule = st.session_state["current_schedule"]
    daily_limit = st.session_state.get("current_daily_limit", 6)

    # Load fresh stats
    stats = get_study_stats(7)
    today_logs = get_today_logs()

    # Calculate today's hours
    today_hours = sum(float(log.get("hours_completed", 0)) for log in today_logs)

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔥 Streak", f"{stats['streak']} days")
    with col2:
        st.metric("⏰ Total Hours", f"{stats['total_hours']:.1f}")
    with col3:
        st.metric("📅 Today", f"{today_hours:.1f} hrs")
    with col4:
        logged_subjects = set(log.get("subject") for log in today_logs)
        missed_count = len([s for s in schedule if s.name not in logged_subjects])
        st.metric("⚠️ To Log", missed_count)

    # Show what's already logged today
    logged_subjects = {}
    for log in today_logs:
        sub_name = log.get("subject", "Unknown")
        hrs = float(log.get("hours_completed", 0))
        logged_subjects[sub_name] = logged_subjects.get(sub_name, 0) + hrs

    if logged_subjects:
        st.success("✅ **Logged today:** " + ", ".join([f"{k} ({v:.1f}h)" for k, v in logged_subjects.items()]))

    # Logging section - CRITICAL FIX: Don't use session_state for widget values
    st.markdown("#### ✏️ Log Today's Study")

    for sub in schedule:
        is_logged = sub.name in logged_subjects
        already_logged_hours = logged_subjects.get(sub.name, 0)

        # CRITICAL FIX: Use unique keys but DON'T tie to session_state values
        hours_key = f"hours_input_{sub.name}_{today}"
        notes_key = f"notes_input_{sub.name}_{today}"
        btn_key = f"log_btn_{sub.name}_{today}"
        full_btn_key = f"full_btn_{sub.name}_{today}"

        with st.expander(
                f"{'✅' if is_logged else '📝'} {sub.name} (Plan: {sub.study_hours:.1f}h, Logged: {already_logged_hours:.1f}h)",
                expanded=not is_logged):

            # Show existing logs
            if is_logged:
                st.info(f"Already logged {already_logged_hours:.1f}h for {sub.name} today")
                st.caption("Add more hours below if you studied extra:")

            # CRITICAL FIX: Use columns but NO session_state in value parameter
            col1, col2 = st.columns([1, 2])

            with col1:
                # Widget manages its own state - don't use value=st.session_state[...]
                hours_input = st.number_input(
                    "Hours to log",
                    min_value=0.0,
                    max_value=float(sub.study_hours * 3),
                    value=0.0,  # Always start at 0, not from session_state
                    step=0.5,
                    key=hours_key  # Streamlit handles state internally
                )

            with col2:
                notes_input = st.text_input(
                    "What did you study?",
                    value="",  # Always start empty
                    key=notes_key,  # Streamlit handles state internally
                    placeholder="e.g., Chapter 3, solved 5 problems"
                )

            # Show what will be logged
            if hours_input > 0:
                st.caption(f"Ready to log: **{hours_input:.1f} hours** for {sub.name}")

            # Buttons row
            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                # Main log button - disabled if no hours
                if st.button(
                        f"✅ Log {hours_input:.1f}h" if hours_input > 0 else "⬜ Enter hours first",
                        key=btn_key,
                        disabled=hours_input <= 0,
                        use_container_width=True,
                        type="primary" if hours_input > 0 else "secondary"
                ):
                    if hours_input > 0:
                        try:
                            # Log the session
                            streak = log_study_session(sub.name, hours_input, notes_input)

                            if streak >= 0:
                                st.success(f"🔥 Logged {hours_input:.1f}h for {sub.name}! Streak: {streak} days!")
                                st.balloons()
                                # Clear inputs by rerunning
                                st.rerun()
                            else:
                                st.error("Failed to save. Check data directory permissions.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            with btn_col2:
                # Quick full hours button
                if st.button(
                        f"⏩ Log Full ({sub.study_hours:.1f}h)",
                        key=full_btn_key,
                        disabled=is_logged and already_logged_hours >= sub.study_hours,
                        use_container_width=True
                ):
                    try:
                        streak = log_study_session(sub.name, sub.study_hours, "Full planned hours completed")

                        if streak >= 0:
                            st.success(f"🔥 Logged full {sub.study_hours:.1f}h for {sub.name}! Streak: {streak} days!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Failed to save")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Quick actions section
    st.markdown("#### ⚡ Quick Actions")

    logged_subjects_set = set(log.get("subject") for log in today_logs)
    missed_subs_list = [s for s in schedule if s.name not in logged_subjects_set]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Log All as Complete", key=f"all_done_{today}",
                     disabled=len(missed_subs_list) == 0,
                     use_container_width=True):
            try:
                success_count = 0
                for sub in missed_subs_list:
                    result = log_study_session(sub.name, sub.study_hours, "Completed full planned hours")
                    if result >= 0:
                        success_count += 1

                if success_count > 0:
                    st.success(f"Logged {success_count} subjects! Great work! 🔥")
                    st.balloons()
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    with col2:
        if st.button("🔄 Reschedule Missed", key=f"resch_{today}",
                     disabled=len(missed_subs_list) == 0,
                     use_container_width=True):
            try:
                for sub in missed_subs_list:
                    sub.exam_days = max(1, sub.exam_days - 1)
                    sub.remaining_hours += sub.study_hours

                total_hours = sum(s.remaining_hours for s in schedule)
                new_schedule = generate_schedule(schedule, total_hours)
                st.session_state["current_schedule"] = new_schedule

                st.success("Rescheduled! Hours redistributed.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    with col3:
        if st.button("📊 Refresh Stats", key=f"refresh_{today}", use_container_width=True):
            st.rerun()

    # Weekly chart
    if stats['recent_daily_hours']:
        st.markdown("#### 📊 Last 7 Days")
        try:
            fig = create_weekly_chart(stats['recent_daily_hours'])
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Chart error: {str(e)}")

    # Subject breakdown table
    if stats['subject_breakdown']:
        st.markdown("#### 📚 All-Time Stats")
        sub_data = []
        for sub_name, sub_stats in stats['subject_breakdown'].items():
            sub_data.append({
                "Subject": sub_name,
                "Total Hours": f"{float(sub_stats.get('total_hours', 0)):.1f}",
                "Sessions": int(sub_stats.get('sessions_count', 0)),
                "Last Studied": str(sub_stats.get('last_studied', 'Never'))[:10] if sub_stats.get(
                    'last_studied') else 'Never'
            })
        if sub_data:
            st.dataframe(pd.DataFrame(sub_data), use_container_width=True)

    # Reset option
    with st.expander("⚠️ Danger Zone - Reset Data"):
        if st.button("🗑️ Delete All Progress", key=f"reset_{today}"):
            if reset_progress():
                st.error("All data deleted!")
                st.rerun()
            else:
                st.error("Failed to reset!")

# -----------------------------
# 📊 GENERATE PLAN
# -----------------------------
def generate_chat_plan(data):
    while len(data["subject_details"]) < len(data["subjects"]):
        data["subject_details"].append({"marks": 50, "difficulty": 3})
        data["marks"].append(50)

    while len(data["exam_days"]) < len(data["subjects"]):
        data["exam_days"].append(3)

    data["subject_details"] = data["subject_details"][:len(data["subjects"])]
    data["marks"] = data["marks"][:len(data["subjects"])]
    data["exam_days"] = data["exam_days"][:len(data["subjects"])]

    subjects = []
    for i in range(len(data["subjects"])):
        details = data["subject_details"][i]
        subjects.append(Subject(
            name=data["subjects"][i],
            marks=details["marks"],
            exam_days=data["exam_days"][i],
            difficulty=details["difficulty"]
        ))

    schedule = generate_schedule(subjects, data["hours"])

    table = []
    for s in schedule:
        table.append({
            "Subject": s.name,
            "Marks": s.marks,
            "Days Left": s.exam_days,
            "Difficulty": s.difficulty,
            "Priority Score": round(s.priority, 2),
            "Study Hours": round(s.study_hours, 2)
        })

    names = [s.name for s in schedule]
    hrs = [s.study_hours for s in schedule]

    df = pd.DataFrame(table)
    suggestions = generate_suggestions(schedule, df)

    return df, names, hrs, schedule, suggestions, data["hours"]


# -----------------------------
# 🤖 CHATBOT
# -----------------------------
def chatbot_tab():
    st.title("🤖 AI Study Planner Chatbot")
    st.markdown(
        "List your subjects, then enter **marks, difficulty** for each. I'll ask for exam days and daily study hours separately!")

    # Show current streak at top
    stats = get_study_stats()
    if stats['streak'] > 0:
        st.success(f"🔥 You're on a {stats['streak']}-day study streak! Keep it up!")

    # Initialize session states
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_data" not in st.session_state:
        st.session_state.user_data = {
            "subjects": [],
            "subject_details": [],
            "marks": [],
            "exam_days": [],
            "difficulty": [],
            "hours": None
        }

    # CRITICAL: Store schedule persistently
    if "current_schedule" not in st.session_state:
        st.session_state.current_schedule = None

    if "current_daily_limit" not in st.session_state:
        st.session_state.current_daily_limit = 6

    # Welcome message
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hi! Which subjects are you studying? (e.g., Math, Physics, Chemistry, Biology)"
        })

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your response...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        data = st.session_state.user_data
        data = parse_input(user_input, data)

        response = generate_reply(data)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        # Check if plan is complete
        all_complete = (
                len(data["subjects"]) > 0 and
                len(data["subject_details"]) == len(data["subjects"]) and
                len(data["exam_days"]) == len(data["subjects"]) and
                data["hours"] is not None
        )

        if all_complete:
            # Generate plan
            df, names, hrs, schedule, suggestions, daily_limit = generate_chat_plan(data)

            # CRITICAL FIX: Store in session state so it persists across reruns
            st.session_state["current_schedule"] = schedule
            st.session_state["current_daily_limit"] = daily_limit

            total_allocated = sum(s.study_hours for s in schedule)

            st.success("✅ Your Study Plan is Ready!")

            st.markdown(
                f"### 📚 {len(schedule)} Subjects | ⏰ Daily Limit: {daily_limit} hrs | 📖 Total Allocated: {total_allocated:.1f} hrs")

            if total_allocated > daily_limit:
                st.error(
                    f"⚠️ Warning: You need {total_allocated:.1f} hours but only have {daily_limit} hours available!")
            elif total_allocated < daily_limit:
                remaining = daily_limit - total_allocated
                st.success(f"✨ You have {remaining:.1f} extra hours for breaks or revision!")

            st.markdown("### 📋 Schedule")
            st.dataframe(df, use_container_width=True)

            st.markdown("### 📊 Hours Distribution")
            fig = create_study_chart(names, hrs)
            st.pyplot(fig)

            st.markdown("### 🎯 Priorities")
            cols = st.columns(min(len(schedule), 4))
            for i, sub in enumerate(schedule):
                with cols[i % len(cols)]:
                    st.metric(
                        label=sub.name,
                        value=f"{sub.study_hours:.1f} hrs",
                        delta=f"Priority: {sub.priority:.0f}"
                    )

            st.markdown("### 💡 Personalized Suggestions")
            for suggestion in suggestions:
                st.info(suggestion)

            # Reset chat data for next plan, but KEEP schedule for progress tracking
            st.session_state.user_data = {
                "subjects": [],
                "subject_details": [],
                "marks": [],
                "exam_days": [],
                "difficulty": [],
                "hours": None
            }

            st.markdown("---")
            st.info("🔄 Scroll down to see Progress Tracker, or type new subjects for another plan!")

    # ALWAYS show progress tracker if we have a schedule
    if st.session_state.get("current_schedule") is not None:
        show_progress_tracker()