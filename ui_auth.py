import streamlit as st
import time
from sheet_manager import register_user, login_user, load_config, find_user
from email_sender import send_2fa_code
from utils import is_valid_email, generate_6_digit_code, config_hash, can_resend_code

def verify_2fa_ui():
    st.title("🔐 Email Verification")

    st.info(f"A 6-digit verification code was sent to `{st.session_state.pending_email}`. It will be valid for 1 minute.")
    seconds_passed = int(time.time() - st.session_state.code_sent_time)
    seconds_left = max(0, 60 - seconds_passed)

    code_input = st.text_input("Enter your 6-digit verification code", max_chars=6)
    col1, col2, col3 = st.columns([3, 2, 1])
    verify_clicked = col1.button("Verify Code")
    resend_clicked = col2.button("Resend Code", disabled=seconds_left > 0)
    cancel_clicked = col3.button("❌ Cancel")

    if verify_clicked:
        if seconds_passed > 60:
            st.error("⏳ This code has expired. Please request a new one.")
        elif len(code_input) != 6:
            st.warning("Please enter all 6 digits of the verification code.")
        elif code_input != st.session_state.generated_code:
            st.error("❌ Invalid code. Please try again.")
        else:
            ok, msg = register_user(st.session_state.pending_email, st.session_state.pending_password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.awaiting_2fa = False
                st.session_state.email = st.session_state.pending_email
                st.session_state.config = load_config(st.session_state.email) or {}
                st.session_state.config_key_suffix = config_hash(st.session_state.config)
                st.session_state.generated_code = ""
                st.session_state.pending_email = ""
                st.session_state.pending_password = ""
                st.session_state.code_sent_time = 0
                st.success("✅ Registration successful.")
                st.rerun()
            else:
                st.error(msg)

    if resend_clicked:
        code = generate_6_digit_code()
        st.session_state.generated_code = code
        sent = send_2fa_code(st.session_state.pending_email, code)
        if sent:
            st.session_state.code_sent_time = time.time()
            st.success("✅ Verification code resent.")
        else:
            st.error("❌ Failed to send verification code.")

    if cancel_clicked:
        st.session_state.awaiting_2fa = False
        st.session_state.pending_email = ""
        st.session_state.pending_password = ""
        st.session_state.generated_code = ""
        st.session_state.code_sent_time = 0
        st.rerun()

def login_form_ui():
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
        if user:
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

def login_ui():
    if st.session_state.logged_in:
        return
    st.title("🔐 Login or Register")
    if st.session_state.awaiting_2fa:
        verify_2fa_ui()
    else:
        login_form_ui()
