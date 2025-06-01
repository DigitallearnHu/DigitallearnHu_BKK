import streamlit as st
import json
from utils import config_hash
from sheet_manager import save_config

def show_config_editor():
    st.title("🛠️ BKK Display Config Editor")

    top_col1, top_col2 = st.columns([1, 5])
    with top_col1:
        if st.button("🔒 Logout"):
            st.session_state.clear()
            st.rerun()
    with top_col2:
        st.markdown(f"**Logged in as:** `{st.session_state.email}`")

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
        elif st.session_state.get("uploaded_config"):
            st.session_state.uploaded_config = None

    if st.session_state.get("uploaded_config"):
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
    fonts = style.get("fonts", {})
    clock_style = style.get("clock", {})
    colors = style.get("colors", {})
    emojis = style.get("custom_emojis", {})
    highlight_zone = config.get("top_highlight_zone", {})
    clock_settings = config.get("clock", {})
    key_suffix = st.session_state.config_key_suffix

    st.subheader("General Settings")
    title = st.text_input("Page Title", config.get("custom_title", ""), key=f"title_{key_suffix}")
    refresh_interval = st.number_input("Auto-refresh (seconds)", 5, 120, config.get("refresh_interval_seconds", 30), key=f"refresh_{key_suffix}")

    st.subheader("Layout")
    view_col, col_col = st.columns(2)
    view = view_col.selectbox("View", ["grid", "list"], index=["grid", "list"].index(layout.get("view", "grid")), key=f"view_{key_suffix}")
    columns = col_col.number_input("Columns per row", 1, 5, layout.get("columns_per_row", 3), key=f"columns_{key_suffix}")
    stops = st.text_input("Stop IDs (comma-separated)", ",".join(layout.get("stop_order", [])), key=f"stops_{key_suffix}").split(",")
    padding = st.number_input("Padding between cards (px)", 0, 64, layout.get("padding_between_cards", 16), key=f"padding_{key_suffix}")
    border_radius = st.number_input("Card border radius (px)", 0, 30, layout.get("card_border_radius", 12), key=f"radius_{key_suffix}")

    st.subheader("Display Options")
    departures = st.slider("Departures per stop", 1, 10, display.get("departures_per_stop", 5), key=f"departures_{key_suffix}")
    show_opts = [
        ("Show wheelchair icon ♿", "show_wheelchair_icon"),
        ("Show stop location 📍", "show_stop_location"),
        ("Highlight soon departures 🔔", "highlight_soon_departures"),
        ("Show stop code", "show_stop_code"),
        ("Show direction", "show_direction"),
        ("Show stop name", "show_stop_name"),
        ("Group by direction", "group_by_direction"),
        ("Show route short name", "show_route_short_name"),
        ("Use 24h time", "use_24h_time")
    ]
    display_flags = {key: st.checkbox(label, display.get(key, False), key=f"{key}_{key_suffix}") for label, key in show_opts}
    max_age = st.number_input("Max departure age (sec)", 30, 600, display.get("max_departure_age_seconds", 180), key=f"age_{key_suffix}")

    st.subheader("Font Settings")
    title_font = st.text_input("Title Font Family", fonts.get("title", {}).get("family", "Roboto"), key=f"title_font_{key_suffix}")
    title_size = st.number_input("Title Font Size", 10, 100, fonts.get("title", {}).get("size", 32), key=f"title_size_{key_suffix}")
    subtitle_font = st.text_input("Subtitle Font Family", fonts.get("subtitle", {}).get("family", "Roboto"), key=f"subtitle_font_{key_suffix}")
    subtitle_size = st.number_input("Subtitle Font Size", 10, 60, fonts.get("subtitle", {}).get("size", 24), key=f"subtitle_size_{key_suffix}")
    text_font = st.text_input("Text Font Family", fonts.get("text", {}).get("family", "Roboto"), key=f"text_font_{key_suffix}")
    text_size = st.number_input("Text Font Size", 10, 40, fonts.get("text", {}).get("size", 16), key=f"text_size_{key_suffix}")

    st.subheader("Clock Style")
    clock_font = st.text_input("Clock Font Family", clock_style.get("font_family", "Roboto"), key=f"clock_font_{key_suffix}")
    clock_size = st.number_input("Clock Font Size", 10, 60, clock_style.get("font_size", 20), key=f"clock_size_{key_suffix}")
    clock_color = st.color_picker("Clock Text Color", clock_style.get("text_color", "#333333"), key=f"clock_color_{key_suffix}")

    st.subheader("Colors")
    text_color = st.color_picker("Text Color", colors.get("text", "#000000"), key=f"text_color_{key_suffix}")
    card_color = st.color_picker("Card Background", colors.get("card_background", "#f8f8f8"), key=f"card_bg_{key_suffix}")
    border_color = st.color_picker("Card Border Color", colors.get("card_border", "#dddddd"), key=f"border_color_{key_suffix}")
    highlight_color = st.color_picker("Highlight Color", colors.get("highlight_departure", "#ff0000"), key=f"highlight_{key_suffix}")

    card_shadow = st.checkbox("Card shadow", style.get("card_shadow", True), key=f"shadow_{key_suffix}")
    card_border = st.checkbox("Card border", style.get("card_border", True), key=f"border_{key_suffix}")

    st.subheader("Emojis")
    emoji_bus = st.text_input("Bus emoji", emojis.get("bus", "🚍"), key=f"bus_{key_suffix}")
    emoji_tram = st.text_input("Tram emoji", emojis.get("tram", "🚋"), key=f"tram_{key_suffix}")
    emoji_metro = st.text_input("Metro emoji", emojis.get("metro", "🚇"), key=f"metro_{key_suffix}")

    st.subheader("Clock Positioning")
    show_clock = st.checkbox("Show clock", clock_settings.get("show", True), key=f"clock_show_{key_suffix}")
    clock_pos = st.selectbox("Clock Position", ["top-left", "top-right", "bottom-left", "bottom-right"], index=["top-left", "top-right", "bottom-left", "bottom-right"].index(clock_settings.get("position", "top-right")), key=f"clock_pos_{key_suffix}")

    st.subheader("Top Highlight Zone")
    zone_enabled = st.checkbox("Enable Top Highlight", highlight_zone.get("enabled", True), key=f"zone_enabled_{key_suffix}")
    zone_minutes = st.number_input("Highlight departures within (minutes)", 1, 30, highlight_zone.get("minutes_threshold", 5), key=f"zone_min_{key_suffix}")
    zone_items = st.number_input("Max items in zone", 1, 10, highlight_zone.get("max_items", 3), key=f"zone_max_{key_suffix}")
    zone_font_size = st.number_input("Highlight font size", 10, 40, highlight_zone.get("font_size", 22), key=f"zone_font_size_{key_suffix}")
    zone_font_family = st.text_input("Highlight font family", highlight_zone.get("font_family", "Roboto"), key=f"zone_font_family_{key_suffix}")
    zone_text_color = st.color_picker("Highlight font color", highlight_zone.get("text_color", "#ff6600"), key=f"zone_text_color_{key_suffix}")
    zone_icon = st.checkbox("Show route icon", highlight_zone.get("show_route_icon", True), key=f"zone_icon_{key_suffix}")
    zone_countdown = st.checkbox("Show countdown", highlight_zone.get("show_countdown", True), key=f"zone_countdown_{key_suffix}")

    new_config = {
        "custom_title": title,
        "refresh_interval_seconds": refresh_interval,
        "layout": {
            "view": view,
            "columns_per_row": columns,
            "stop_order": [s.strip() for s in stops if s.strip()],
            "padding_between_cards": padding,
            "card_border_radius": border_radius
        },
        "display": {
            "departures_per_stop": departures,
            "max_departure_age_seconds": max_age,
            **display_flags
        },
        "style": {
            "color_by_route": True,
            "card_shadow": card_shadow,
            "card_border": card_border,
            "fonts": {
                "title": {"family": title_font, "size": title_size, "weight": "bold"},
                "subtitle": {"family": subtitle_font, "size": subtitle_size, "weight": "normal"},
                "text": {"family": text_font, "size": text_size, "weight": "normal"},
                "time": {"family": clock_font, "size": clock_size, "weight": "medium"}
            },
            "clock": {
                "font_family": clock_font,
                "font_size": clock_size,
                "font_weight": "bold",
                "text_color": clock_color
            },
            "colors": {
                "text": text_color,
                "background": "#ffffff",
                "card_background": card_color,
                "card_border": border_color,
                "highlight_departure": highlight_color,
                "clock_text": clock_color
            },
            "custom_emojis": {
                "bus": emoji_bus,
                "tram": emoji_tram,
                "metro": emoji_metro
            }
        },
        "clock": {
            "show": show_clock,
            "position": clock_pos
        },
        "top_highlight_zone": {
            "enabled": zone_enabled,
            "minutes_threshold": zone_minutes,
            "max_items": zone_items,
            "font_size": zone_font_size,
            "font_family": zone_font_family,
            "text_color": zone_text_color,
            "show_route_icon": zone_icon,
            "show_countdown": zone_countdown
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
