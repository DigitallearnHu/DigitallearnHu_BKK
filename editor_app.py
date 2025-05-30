import streamlit as st
import json
import hashlib
import random
import time
from sheet_manager import register_user, login_user, save_config, load_config, find_user
from email_sender import send_2fa_code
from streamlit_autorefresh import st_autorefresh

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
def set_session_states():
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

set_session_states()

def config_hash(config: dict) -> str:
    return hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]

def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email and len(email) >= 5

def generate_6_digit_code() -> str:
    return f"{random.randint(100000, 999999)}"

def can_resend_code() -> bool:
    return time.time() - st.session_state.code_sent_time > 60

def login_ui():
    st.title("🔐 Login or Register")

    if st.session_state.awaiting_2fa:
        st.info(f"A 6-digit verification code was sent to {st.session_state.pending_email}. Please enter it below.")

        seconds_passed = int(time.time() - st.session_state.code_sent_time)
        seconds_left = max(0, 60 - seconds_passed)

        if seconds_left > 0:
            st_autorefresh(interval=1000, limit=60, key="count")

        code_input = st.text_input("Enter your 6-digit verification code", max_chars=6, key="code_input")

        if seconds_left > 0:
            st.info(f"⏳ You can request a new code in {seconds_left} seconds.")
        else:
            st.info("You can request a new code now.")

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Verify Code"):
                if len(code_input) != 6:
                    st.warning("Please enter all 6 digits of the verification code.")
                elif code_input != st.session_state.generated_code:
                    st.error("❌ Invalid code. Please try again.")
                else:
                    ok, msg = register_user(st.session_state.pending_email, st.session_state.pending_password)
                    if ok:
                        st.success("✅ Registration successful. Redirecting to dashboard...")
                        st.session_state.awaiting_2fa = False
                        st.session_state.logged_in = False
                        st.session_state.email = st.session_state.pending_email
                        st.session_state.config = load_config(st.session_state.email) or {}
                        st.session_state.config_key_suffix = config_hash(st.session_state.config)
                        st.session_state.generated_code = ""
                        st.session_state.pending_email = ""
                        st.session_state.pending_password = ""
                        set_session_states()
                        st.rerun()
                    else:
                        st.error(msg)
        with col2:
            if st.button("Resend Code", disabled=seconds_left > 0):
                code = generate_6_digit_code()
                st.session_state.generated_code = code
                sent = send_2fa_code(st.session_state.pending_email, code)
                if sent:
                    st.session_state.code_sent_time = time.time()
                    st.success("✅ Verification code resent.")
                else:
                    st.error("❌ Failed to send verification code.")

        return

    email = st.text_input("Email", key="email_input")
    password = st.text_input("Password", type="password", key="password_input")

    if st.button("Continue"):
        if not email or not password:
            st.warning("Please enter both email and password.")
            return
        if not is_valid_email(email):
            st.error("❌ Please enter a valid email address.")
            return

        row_num, user = find_user(email)

        if user == "exists":
            ok, msg, _ = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.config = load_config(email) or {}
                st.session_state.config_key_suffix = config_hash(st.session_state.config)
                st.success("Login successful.")
                st.rerun()
            else:
                st.error(msg)
        else:
            code = generate_6_digit_code()
            sent = send_2fa_code(email, code)
            if sent:
                st.session_state.awaiting_2fa = True
                st.session_state.pending_email = email
                st.session_state.pending_password = password
                st.session_state.generated_code = code
                st.session_state.code_sent_time = time.time()
                st.info(f"A 6-digit verification code has been sent to {email}. Please enter it below.")
                st.rerun()
            else:
                st.error("Failed to send verification code. Please try again later.")

def show_config_editor():
    st.title("🛠️ BKK Display Config Editor")

    top_col1, top_col2 = st.columns([1, 5])
    with top_col1:
        if st.button("🔒 Logout"):
            st.session_state.clear()
            st.rerun()
    with top_col2:
        st.markdown(f"**Logged in as:** `{st.session_state.email}`")

    # Upload config section
    if "just_applied_config" in st.session_state:
        del st.session_state["just_applied_config"]
    else:
        uploaded_file = st.file_uploader("Upload your config.json", type=["json"])

        if uploaded_file:
            try:
                uploaded_config = json.load(uploaded_file)
                st.session_state.uploaded_config = uploaded_config
                st.success("✅ File uploaded. Click 'Apply Config' below to use it.")
            except Exception as e:
                st.error(f"❌ Failed to load config: {e}")
        elif "uploaded_config" in st.session_state and st.session_state.uploaded_config:
            st.session_state.uploaded_config = None

    if "uploaded_config" in st.session_state and st.session_state.uploaded_config:
        if st.button("✅ Apply Uploaded Config"):
            st.session_state.config = st.session_state.uploaded_config
            st.session_state.uploaded_config = None
            st.session_state.config_key_suffix = config_hash(st.session_state.config)
            st.session_state.just_applied_config = True
            st.rerun()

    config = st.session_state.config or {}
    layout = config.get("layout", {})
    display = config.get("display", {})
    style = config.get("style", {})
    key_suffix = st.session_state.config_key_suffix

    stops = st.text_input("Stop IDs (comma-separated)", ",".join(layout.get("stop_order", [])), key=f"stops_{key_suffix}").split(",")

    st.subheader("Layout")
    layout_col = st.columns(2)
    view = layout_col[0].selectbox("View", ["grid", "list"], index=["grid", "list"].index(layout.get("view", "grid")), key=f"view_{key_suffix}")
    columns = layout_col[1].number_input("Columns per row", 1, 5, layout.get("columns_per_row", 3), key=f"columns_{key_suffix}")

    st.subheader("Display Options")
    dep_val = display.get("departures_per_stop", 5)
    departures = st.slider("Departures per stop", 1, 10, dep_val if 1 <= dep_val <= 10 else 5, key=f"departures_{key_suffix}")

    wheelchair = st.checkbox("Show wheelchair icon ♿", display.get("show_wheelchair_icon", True), key=f"wheelchair_{key_suffix}")
    location = st.checkbox("Show stop location 📍", display.get("show_stop_location", True), key=f"location_{key_suffix}")
    highlight = st.checkbox("Highlight soon departures 🔔", display.get("highlight_soon_departures", True), key=f"highlight_{key_suffix}")
    stop_code = st.checkbox("Show stop code", display.get("show_stop_code", False), key=f"code_{key_suffix}")
    direction = st.checkbox("Show direction", display.get("show_direction", False), key=f"direction_{key_suffix}")
    routes_filter = st.text_input("Only show these routes (comma-separated)", ",".join(display.get("filter_routes", [])), key=f"routes_{key_suffix}")

    st.subheader("Style")
    fonts = st.columns(3)
    title_size = fonts[0].number_input("Title font size", 10, 100, style.get("title_font_size", 32), key=f"title_size_{key_suffix}")
    subtitle_size = fonts[1].number_input("Subtitle font size", 10, 60, style.get("subtitle_font_size", 24), key=f"subtitle_size_{key_suffix}")
    text_size = fonts[2].number_input("Text font size", 10, 40, style.get("text_font_size", 16), key=f"text_size_{key_suffix}")
    emoji_bus = st.text_input("Bus emoji", style.get("custom_emojis", {}).get("bus", "🚍"), key=f"bus_{key_suffix}")
    emoji_tram = st.text_input("Tram emoji", style.get("custom_emojis", {}).get("tram", "🚋"), key=f"tram_{key_suffix}")

    new_config = {
        "custom_title": st.text_input("Page Title", config.get("custom_title", "🚏 BKK Megállók Dashboard"), key=f"title_{key_suffix}"),
        "refresh_interval_seconds": st.number_input("Auto-refresh (seconds)", 5, 120, config.get("refresh_interval_seconds", 30), key=f"refresh_{key_suffix}"),
        "layout": {
            "view": view,
            "columns_per_row": columns,
            "stop_order": [s.strip() for s in stops if s.strip()]
        },
        "display": {
            "departures_per_stop": departures,
            "show_wheelchair_icon": wheelchair,
            "show_stop_location": location,
            "highlight_soon_departures": highlight,
            "filter_routes": [r.strip() for r in routes_filter.split(",") if r.strip()],
            "show_stop_code": stop_code,
            "show_direction": direction
        },
        "style": {
            "title_font_size": title_size,
            "subtitle_font_size": subtitle_size,
            "text_font_size": text_size,
            "color_by_route": True,
            "custom_emojis": {
                "bus": emoji_bus,
                "tram": emoji_tram
            }
        }
    }

    st.subheader("💾 Save Config")
    config_json = json.dumps(new_config, indent=2, ensure_ascii=False)
    st.code(config_json, language="json")

    if st.button("Save to My Config"):
        ok, msg = save_config(st.session_state.email, new_config)
        if ok:
            st.session_state.config = new_config
            st.session_state.config_key_suffix = config_hash(new_config)
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    st.download_button("⬇️ Download config.json", config_json, file_name="config.json", mime="application/json")

if not st.session_state.logged_in:
    login_ui()
    st.stop()
else:
    show_config_editor()
