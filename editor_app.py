import streamlit as st
from ui_auth import login_ui
from ui_editor import show_config_editor
from utils import config_hash

st.set_page_config(page_title="BKK Config Editor", layout="centered")

# --- Initialize session state ---
default_states = {
    "logged_in": False,
    "email": "",
    "config": {},
    "uploaded_config": None,
    "config_key_suffix": "default",
    "awaiting_2fa": False,
    "pending_email": "",
    "pending_password": "",
    "generated_code": "",
    "code_sent_time": 0,
}

for key, default_value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# --- Auth or Editor View ---
if not st.session_state.logged_in:
    login_ui()
    st.stop()
else:
    show_config_editor()
