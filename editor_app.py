import streamlit as st
import json
from sheet_manager import register_user, login_user, save_config, load_config

st.set_page_config(page_title="BKK Config Editor", layout="centered")

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.config = {}

# --- Login/Register ---
def login_ui():
    st.title("🔐 Login or Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    mode = st.radio("Mode", ["Login", "Register"])

    if st.button("Continue"):
        if not email or not password:
            st.warning("Please enter both email and password.")
            return

        if mode == "Register":
            ok, msg = register_user(email, password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        elif mode == "Login":
            ok, msg, _ = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.config = load_config(email) or {}
                st.success("Login successful.")
            else:
                st.error(msg)

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# --- Load Config ---
st.title("🛠️ BKK Display Config Editor")

config = st.session_state.config or {}

# Set defaults
layout = config.get("layout", {})
display = config.get("display", {})
style = config.get("style", {})

stops = st.text_input("Stop IDs (comma-separated)", ",".join(layout.get("stop_order", []))).split(",")

st.subheader("Layout")
layout_col = st.columns(2)
view = layout_col[0].selectbox("View", ["grid", "list"], index=["grid", "list"].index(layout.get("view", "grid")))
columns = layout_col[1].number_input("Columns per row", 1, 5, layout.get("columns_per_row", 3))

st.subheader("Display Options")
departures = st.slider("Departures per stop", 1, 10, display.get("departures_per_stop", 5))
wheelchair = st.checkbox("Show wheelchair icon ♿", display.get("show_wheelchair_icon", True))
location = st.checkbox("Show stop location 📍", display.get("show_stop_location", True))
highlight = st.checkbox("Highlight soon departures 🔔", display.get("highlight_soon_departures", True))
stop_code = st.checkbox("Show stop code", display.get("show_stop_code", False))
direction = st.checkbox("Show direction", display.get("show_direction", False))
routes_filter = st.text_input("Only show these routes (comma-separated)", ",".join(display.get("filter_routes", [])))

st.subheader("Style")
fonts = st.columns(3)
title_size = fonts[0].number_input("Title font size", 10, 100, style.get("title_font_size", 32))
subtitle_size = fonts[1].number_input("Subtitle font size", 10, 60, style.get("subtitle_font_size", 24))
text_size = fonts[2].number_input("Text font size", 10, 40, style.get("text_font_size", 16))
emoji_bus = st.text_input("Bus emoji", style.get("custom_emojis", {}).get("bus", "🚍"))
emoji_tram = st.text_input("Tram emoji", style.get("custom_emojis", {}).get("tram", "🚋"))

# Build new config
new_config = {
    "custom_title": st.text_input("Page Title", config.get("custom_title", "🚏 BKK Megállók Dashboard")),
    "refresh_interval_seconds": st.number_input("Auto-refresh (seconds)", 5, 120, config.get("refresh_interval_seconds", 30)),
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

# Show + Save
st.subheader("💾 Save Config")
config_json = json.dumps(new_config, indent=2, ensure_ascii=False)
st.code(config_json, language="json")

if st.button("Save to My Config"):
    ok, msg = save_config(st.session_state.email, new_config)
    if ok:
        st.success(msg)
    else:
        st.error(msg)
