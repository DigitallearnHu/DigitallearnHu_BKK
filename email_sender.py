import smtplib
import ssl
from email.message import EmailMessage
import streamlit as st

def send_2fa_code(to_email: str, code: str) -> bool:
    """
    Send a 6-digit 2FA code email using SMTP2Go via credentials in Streamlit secrets.
    Returns True on success, False on failure.
    """

    smtp_host = st.secrets["SMTP_HOST"]
    smtp_port = st.secrets.get("SMTP_PORT", 587)
    smtp_user = st.secrets["SMTP_USER"]
    smtp_pass = st.secrets["SMTP_PASSWORD"]
    sender_email = st.secrets["SMTP_SENDER"]

    message = EmailMessage()
    message["Subject"] = "Your 2FA Verification Code"
    message["From"] = sender_email
    message["To"] = to_email
    message.set_content(f"Your verification code is: {code}")

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send 2FA email: {e}")
        return False
