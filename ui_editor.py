import streamlit as st
import json
from utils import config_hash
from sheet_manager import save_config


def general_settings_section(config, key_suffix):
    st.subheader("General Settings")
    title = st.text_input("Page Title", config.get("custom_title", ""), key=f"title_{key_suffix}")
    refresh_interval = st.number_input("Auto-refresh (seconds)", 5, 120, config.get("refresh_interval_seconds", 30), key=f"refresh_{key_suffix}")
    return title, refresh_interval


def layout_section(layout, key_suffix):
    with st.expander("📐 Layout Settings"):
        view_col, col_col = st.columns(2)
        view = view_col.selectbox("View", ["grid", "list"], index=["grid", "list"].index(layout.get("view", "grid")), key=f"view_{key_suffix}")
        columns = col_col.number_input("Columns per row", 1, 5, layout.get("columns_per_row", 3), key=f"columns_{key_suffix}")
        stops = st.text_input("Stop IDs (comma-separated)", ",".join(layout.get("stop_order", [])), key=f"stops_{key_suffix}").split(",")
        padding = st.number_input("Padding between cards (px)", 0, 64, layout.get("padding_between_cards", 16), key=f"padding_{key_suffix}")
        border_radius = st.number_input("Card border radius (px)", 0, 30, layout.get("card_border_radius", 12), key=f"radius_{key_suffix}")
    return view, columns, stops, padding, border_radius


def display_section(display, key_suffix):
    with st.expander("🖥️ Display Options"):
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
        flags = {key: st.checkbox(label, display.get(key, False), key=f"{key}_{key_suffix}") for label, key in show_opts}
        max_age = st.number_input("Max departure age (sec)", 30, 600, display.get("max_departure_age_seconds", 180), key=f"age_{key_suffix}")
    return departures, max_age, flags


def font_section(fonts, key_suffix):
    with st.expander("🔤 Font Settings"):
        title_font = st.text_input("Title Font Family", fonts.get("title", {}).get("family", "Roboto"), key=f"title_font_{key_suffix}")
        title_size = st.number_input("Title Font Size", 10, 100, fonts.get("title", {}).get("size", 32), key=f"title_size_{key_suffix}")
        subtitle_font = st.text_input("Subtitle Font Family", fonts.get("subtitle", {}).get("family", "Roboto"), key=f"subtitle_font_{key_suffix}")
        subtitle_size = st.number_input("Subtitle Font Size", 10, 60, fonts.get("subtitle", {}).get("size", 24), key=f"subtitle_size_{key_suffix}")
        text_font = st.text_input("Text Font Family", fonts.get("text", {}).get("family", "Roboto"), key=f"text_font_{key_suffix}")
        text_size = st.number_input("Text Font Size", 10, 40, fonts.get("text", {}).get("size", 16), key=f"text_size_{key_suffix}")
        time_font = fonts.get("time", {}).get("family", "Roboto Mono")
        time_size = fonts.get("time", {}).get("size", 20)
    return {
        "title": {"family": title_font, "size": title_size, "weight": "bold"},
        "subtitle": {"family": subtitle_font, "size": subtitle_size, "weight": "normal"},
        "text": {"family": text_font, "size": text_size, "weight": "normal"},
        "time": {"family": time_font, "size": time_size, "weight": "medium"}
    }


def clock_style_section(clock_style, clock_settings, key_suffix):
    with st.expander("🕒 Clock Settings"):
        font_family = st.text_input("Clock Font Family", clock_style.get("font_family", "Roboto"), key=f"clock_font_{key_suffix}")
        font_size = st.number_input("Clock Font Size", 10, 60, clock_style.get("font_size", 20), key=f"clock_size_{key_suffix}")
        text_color = st.color_picker("Clock Text Color", clock_style.get("text_color", "#333333"), key=f"clock_color_{key_suffix}")
        show = st.checkbox("Show clock", clock_settings.get("show", True), key=f"clock_show_{key_suffix}")
        position = st.selectbox("Clock Position", ["top-left", "top-right", "bottom-left", "bottom-right"],
                                index=["top-left", "top-right", "bottom-left", "bottom-right"].index(clock_settings.get("position", "top-right")),
                                key=f"clock_pos_{key_suffix}")
    return {"font_family": font_family, "font_size": font_size, "font_weight": "bold", "text_color": text_color}, {"show": show, "position": position}


def color_section(colors, style, key_suffix):
    with st.expander("🎨 Color Settings"):
        text_color = st.color_picker("Text Color", colors.get("text", "#000000"), key=f"text_color_{key_suffix}")
        card_color = st.color_picker("Card Background", colors.get("card_background", "#f8f8f8"), key=f"card_bg_{key_suffix}")
        border_color = st.color_picker("Card Border Color", colors.get("card_border", "#dddddd"), key=f"border_color_{key_suffix}")
        highlight_color = st.color_picker("Highlight Color", colors.get("highlight_departure", "#ff0000"), key=f"highlight_{key_suffix}")
        shadow = st.checkbox("Card shadow", style.get("card_shadow", True), key=f"shadow_{key_suffix}")
        border = st.checkbox("Card border", style.get("card_border", True), key=f"border_{key_suffix}")
    return {
        "text": text_color,
        "background": "#ffffff",
        "card_background": card_color,
        "card_border": border_color,
        "highlight_departure": highlight_color,
        "clock_text": colors.get("clock_text", "#333333")
    }, shadow, border


def emoji_section(emojis, key_suffix):
    with st.expander("🚍 Emoji Settings"):
        bus = st.text_input("Bus emoji", emojis.get("bus", "🚍"), key=f"bus_{key_suffix}")
        tram = st.text_input("Tram emoji", emojis.get("tram", "🚋"), key=f"tram_{key_suffix}")
        metro = st.text_input("Metro emoji", emojis.get("metro", "🚇"), key=f"metro_{key_suffix}")
    return {"bus": bus, "tram": tram, "metro": metro}


def highlight_zone_section(zone, key_suffix):
    with st.expander("🔶 Top Highlight Zone"):
        enabled = st.checkbox("Enable Top Highlight", zone.get("enabled", True), key=f"zone_enabled_{key_suffix}")
        minutes = st.number_input("Highlight within minutes", 1, 30, zone.get("minutes_threshold", 5), key=f"zone_min_{key_suffix}")
        max_items = st.number_input("Max items in zone", 1, 10, zone.get("max_items", 3), key=f"zone_max_{key_suffix}")
        font_size = st.number_input("Highlight font size", 10, 40, zone.get("font_size", 22), key=f"zone_font_size_{key_suffix}")
        font_family = st.text_input("Highlight font family", zone.get("font_family", "Roboto"), key=f"zone_font_family_{key_suffix}")
        text_color = st.color_picker("Highlight font color", zone.get("text_color", "#ff6600"), key=f"zone_text_color_{key_suffix}")
        show_icon = st.checkbox("Show route icon", zone.get("show_route_icon", True), key=f"zone_icon_{key_suffix}")
        countdown = st.checkbox("Show countdown", zone.get("show_countdown", True), key=f"zone_countdown_{key_suffix}")
    return {
        "enabled": enabled,
        "minutes_threshold": minutes,
        "max_items": max_items,
        "font_size": font_size,
        "font_family": font_family,
        "text_color": text_color,
        "show_route_icon": show_icon,
        "show_countdown": countdown
    }


def show_config_editor():
    st.title("🛠️ BKK Display Config Editor")

    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.rerun()

    config = st.session_state.get("config", {})
    key_suffix = st.session_state.get("config_key_suffix", "default")

    title, refresh_interval = general_settings_section(config, key_suffix)
    view, columns, stops, padding, radius = layout_section(config.get("layout", {}), key_suffix)
    departures, max_age, display_flags = display_section(config.get("display", {}), key_suffix)
    fonts = font_section(config.get("style", {}).get("fonts", {}), key_suffix)
    clock_style, clock = clock_style_section(config.get("style", {}).get("clock", {}), config.get("clock", {}), key_suffix)
    colors, shadow, border = color_section(config.get("style", {}).get("colors", {}), config.get("style", {}), key_suffix)
    emojis = emoji_section(config.get("style", {}).get("custom_emojis", {}), key_suffix)
    highlight_zone = highlight_zone_section(config.get("top_highlight_zone", {}), key_suffix)

    new_config = {
        "custom_title": title,
        "refresh_interval_seconds": refresh_interval,
        "layout": {
            "view": view,
            "columns_per_row": columns,
            "stop_order": [s.strip() for s in stops if s.strip()],
            "padding_between_cards": padding,
            "card_border_radius": radius
        },
        "display": {
            "departures_per_stop": departures,
            "max_departure_age_seconds": max_age,
            **display_flags
        },
        "style": {
            "color_by_route": True,
            "card_shadow": shadow,
            "card_border": border,
            "fonts": fonts,
            "clock": clock_style,
            "colors": colors,
            "custom_emojis": emojis
        },
        "clock": clock,
        "top_highlight_zone": highlight_zone
    }

    st.subheader("💾 Save Config")
    config_json = json.dumps(new_config, indent=2, ensure_ascii=False)
    st.code(config_json, language="json")

    if st.button("Save to My Config"):
        ok, msg = save_config(st.session_state["email"], new_config)
        if ok:
            st.session_state.config = new_config
            st.session_state.config_key_suffix = config_hash(new_config)
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    st.download_button("⬇️ Download config.json", config_json, file_name="config.json", mime="application/json")
