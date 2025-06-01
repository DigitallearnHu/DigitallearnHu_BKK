import json
import hashlib
import random
import time
import streamlit as st

def config_hash(config: dict) -> str:
    return hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]

def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email and len(email) >= 5

def generate_6_digit_code() -> str:
    return f"{random.randint(100000, 999999)}"

def can_resend_code() -> bool:
    return time.time() - st.session_state.code_sent_time > 60

def countdown_timer(seconds_left: int):
    countdown_placeholder = st.empty()
    for remaining in range(seconds_left, 0, -1):
        countdown_placeholder.info(f"⏳ You can request a new code in {remaining} seconds.")
        time.sleep(1)
    countdown_placeholder.info("You can request a new code now.")
