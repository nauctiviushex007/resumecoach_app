
"""ResumeCoach - entry point. Run with: streamlit run app.py"""

import os
import streamlit as st
from backend.ai import Asker
from frontend import ui

st.set_page_config(
    page_title="ResumeCoach",
    page_icon="📄",
    layout="wide"
)


def secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


# Optional password protection
password = secret("APP_PASSWORD")

if password and not st.session_state.get("ok"):
    pw = st.text_input("Password", type="password")

    if pw and pw == password:
        st.session_state.ok = True
        st.rerun()

    st.stop()


# Initialize AI assistant
if "asker" not in st.session_state:
    st.session_state.asker = Asker(
        secret("ANTHROPIC_API_KEY"),
        secret("LLM_MODEL", "claude-sonnet-4-6")
    )

asker = st.session_state.asker


# Initialize UI
ui.init_state()

# Load the upgraded design
ui.load_styles()
ui.visual_fix()

# Display the upgraded hero section
ui.header(asker)

# Display application features
ui.sidebar(asker)

# Sidebar and application features
ui.sidebar(asker)
ui.inputs()

if st.session_state.analysis:
    st.divider()
    ui.results()
    ui.coach(asker)
    ui.letter(asker)
