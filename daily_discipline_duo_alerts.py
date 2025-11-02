import streamlit as st
import json
import datetime
import pandas as pd
import time
import threading
from typing import Dict, Any

# Try push notifications
try:
    from streamlit_push_notifications import send_push
    PUSH_AVAILABLE = True
except ImportError:
    PUSH_AVAILABLE = False
    def send_push(title, body, **kwargs):
        st.warning(f"Alert: {title} - {body}")

# === CONFIG ===
USERS = ["Shaylen", "Sherwin"]
DATA_FILES = {
    "Shaylen": "shaylen_data.json",
    "Sherwin": "sherwin_data.json"
}

QUOTES = [
    {"quote": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Aristotle"},
    {"quote": "Discipline is the bridge between goals and accomplishment.", "author": "Jim Rohn"},
    {"quote": "Small daily improvements are the key to staggering long-term results.", "author": "James Clear"},
    {"quote": "You don't rise to the level of your goals. You fall to the level of your systems.", "author": "James Clear"},
    {"quote": "The pain of discipline is nothing like the pain of regret.", "author": "Sarah Bombell"},
    {"quote": "Consistency compounds.", "author": "Unknown"},
    {"quote": "Do something today that your future self will thank you for.", "author": "Unknown"},
    {"quote": "Success is nothing more than a few simple disciplines, practiced every day.", "author": "Jim Rohn"},
    {"quote": "The secret of your future is hidden in your daily routine.", "author": "Mike Murdock"},
    {"quote": "Mastery is time and intense focus.", "author": "Robert Greene"},
]

def load_user_data(username: str) -> Dict[str, Any]:
    try:
        with open(DATA_FILES[username], "r") as f:
            return json.load(f)
    except:
        return {
            "habits": [],
            "tasks": [],
            "wake_up": "7:00 AM",
            "bed_time": "11:00 PM",
            "current_day": datetime.date.today().isoformat(),
            "checkins": {},
            "journal_entries": [],
            "gratitude": [],
            "streaks": {"habits": 0, "tasks": 0},
            "quote_index": 0,
            "notifications_enabled": True,
            "next_reminder_time": None
        }

def save_user_data(username: str, data: Dict[str, Any]):
    with open(DATA_FILES[username], "w") as f:
        json.dump(data, f, indent=2)

def send_alert(user: str, title: str, body: str):
    if PUSH_AVAILABLE:
        send_push(title=title, body=body)
    else:
        st.sidebar.success(f"Alert for {user}: {title} - {body}")

# === APP ===
st.set_page_config(page_title="Daily Discipline", layout="wide")
st.title("Daily Discipline Tracker")

user = st.sidebar.selectbox("Login", USERS)
data = load_user_data(user)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Setup", "Check-In", "Journal", "End of Day", "Alerts"])

with tab1:
    st.header("Setup")
    data["wake_up"] = st.text_input("Wake Up", data["wake_up"])
    data["bed_time"] = st.text_input("Bed Time", data["bed_time"])
    habits = st.text_area("Habits (1 per line)", "\n".join(data["habits"]))
    if st.button("Save Habits"):
        data["habits"] = [h.strip() for h in habits.split("\n") if h.strip()]
        save_user_data(user, data)
        st.success("Saved!")

with tab2:
    st.header("Hourly Check-In")
    try:
        hours = pd.date_range(data["wake_up"], data["bed_time"], freq="H").strftime("%I:%M %p").tolist()
    except:
        hours = [f"{h}:00 AM" if h < 12 else f"{h-12}:00 PM" for h in range(7, 24)]
    hour = st.selectbox("Hour", hours)
    for h in data["habits"]:
        st.checkbox(h, key=f"{h}_{hour}")
    if st.button("Check In"):
        st.success("Logged!")

with tab3:
    st.header("JRL Journal")
    entry = st.text_area("Notes")
    if st.button("Save"):
        data["journal_entries"].append({"time": datetime.datetime.now().strftime("%I:%M %p"), "entry": entry})
        save_user_data(user, data)
        st.success("Saved!")

with tab4:
    st.header("End of Day")
    if st.button("Report"):
        st.success("Done!")
        g1 = st.text_input("Grateful for 1")
        g2 = st.text_input("Grateful for 2")
        g3 = st.text_input("Grateful for 3")
        if st.button("Save Gratitude"):
            data["gratitude"].append([g1, g2, g3])
            save_user_data(user, data)

with tab5:
    st.header("Alerts")
    if st.button("Test Alert"):
        send_alert(user, "Test!", "It works!")