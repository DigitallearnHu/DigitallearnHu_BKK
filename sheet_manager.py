import hashlib
import json
import streamlit as st
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_NAME = "UsersAndConfigs"
WORKSHEET_NAME = "users"

# Setup credentials and open sheet
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    json_data = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1BcOHJxaSAh5uGrS9y0jEMoKDlEDUXHfWtPIQGaXH1U4").worksheet("Datas")
    return sheet

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def find_user(sheet, email):
    try:
        records = sheet.get_all_records()
        for i, row in enumerate(records, start=2):  # Row 2 = first data row
            if row["Email"].strip().lower() == email.strip().lower():
                return i, row
        return None, None
    except Exception as e:
        print(f"❌ Error finding user: {e}")
        return None, None

def register_user(email, password):
    sheet = get_sheet()
    _, existing = find_user(sheet, email)
    if existing:
        return False, "Email already registered."
    hashed = hash_password(password)
    now = datetime.now().isoformat()
    sheet.append_row([email, hashed, now, 0, "{}"])
    return True, "User registered."

def login_user(email, password):
    sheet = get_sheet()
    row_num, user = find_user(sheet, email)
    if not user:
        return False, "User not found.", None
    if hash_password(password) != user["Password"]:
        return False, "Incorrect password.", None
    return True, "Login successful.", row_num

def save_config(email, config_json):
    sheet = get_sheet()
    row_num, user = find_user(sheet, email)

    if not user or not row_num:
        return False, "User not found or invalid row number."

    today = date.today().isoformat()
    last_upload_raw = user.get("LastUpload", "")
    last_upload_date = last_upload_raw.split("T")[0] if "T" in last_upload_raw else ""

    try:
        upload_count = int(user.get("UploadCount", 0))
    except ValueError:
        upload_count = 0

    MAX_UPLOADS_PER_DAY = int(st.secrets.get("MAX_UPLOADS_PER_DAY", 10))

    if last_upload_date == today and upload_count >= MAX_UPLOADS_PER_DAY:
        return False, f"Daily upload limit reached ({MAX_UPLOADS_PER_DAY}/day)."

    if last_upload_date != today:
        upload_count = 1
    else:
        upload_count += 1

    now = datetime.now().isoformat()
    config_str = json.dumps(config_json)

    try:
        sheet.update(f"C{row_num}", [[now]])                     # LastUpload
        sheet.update(f"D{row_num}", [[str(upload_count)]])       # UploadCount
        sheet.update(f"E{row_num}", [[config_str]])              # Config
    except Exception as e:
        return False, f"Error updating sheet: {e}"

    return True, f"✅ Upload #{upload_count} saved successfully."

def load_config(email):
    sheet = get_sheet()
    _, user = find_user(sheet, email)
    if not user:
        return None
    try:
        return json.loads(user["Config"])
    except Exception:
        return {}
