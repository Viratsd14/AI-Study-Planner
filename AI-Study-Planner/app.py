import streamlit as st
import base64
from planner_ui import planner_tab
from chatbot_ui import chatbot_tab
from utils.progress_tracker import load_progress

st.set_page_config(page_title="AI Study Planner", layout="wide")


def set_bg(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.75)),
                    url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .title {{
    text-align: center;
    color: white;
    font-size: 60px;
    font-weight: 700;
    letter-spacing: 1px;
    }}

    .subtitle {{
    text-align: center;
    color: #e0e0e0;
    font-size: 22px;
    opacity: 0.9;
    }}

    div.stButton > button {{
        height: 180px;
        width: 300px;
        border-radius: 18px;
        font-size: 20px;
        font-weight: 600;
        background: rgba(255,255,255,0.15);
        color: white;
        border: none;
        backdrop-filter: blur(12px);
        white-space: pre-line;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover {{
        background: rgba(255,255,255,0.3);
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }}

    div[data-testid="column"] {{
        display: flex;
        justify-content: center;
    }}

    .streak-badge {{
        display: inline-block;
        background: linear-gradient(135deg, #ff6b6b, #feca57);
        color: white;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    </style>
    """, unsafe_allow_html=True)


if "page" not in st.session_state:
    st.session_state.page = "home"


def home_page():
    # Show streak badge if active
    progress = load_progress()
    if progress.get('streak', 0) > 0:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px; margin-top: 20px;">
            <div class="streak-badge">
                🔥 {progress['streak']} Day Streak! Keep it up! 🔥
            </div>
        </div>
        """, unsafe_allow_html=True)

    set_bg("assets/bg.jpg")

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    st.markdown('<div class="title">📚 AI Study Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Plan smarter. Study better. Stress less.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    spacer1, left, right, spacer2 = st.columns([2, 1, 1, 2])

    with left:
        if st.button(
                "📊 Scheduler\n\nCreate structured study plans",
                key="scheduler_btn"
        ):
            st.session_state.page = "planner"

    with right:
        if st.button(
                "🤖 Chatbot\n\nPlan using natural language",
                key="chatbot_btn"
        ):
            st.session_state.page = "chatbot"


if st.session_state.page == "home":
    home_page()

elif st.session_state.page == "planner":
    if st.button("⬅ Back", key="back_planner"):
        st.session_state.page = "home"

    planner_tab()

elif st.session_state.page == "chatbot":
    if st.button("⬅ Back", key="back_chatbot"):
        st.session_state.page = "home"

    chatbot_tab()