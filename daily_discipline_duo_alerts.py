import streamlit as st
import json
import datetime
import pandas as pd
from typing import Dict, Any

# === CONFIG ===
USERS = ["Shaylen", "Sherwin"]
DATA_FILES = {
    "Shaylen": "shaylen_data.json",
    "Sherwin": "sherwin_data.json"
}

# === MOTIVATIONAL QUOTES (Rotates Every Hour) ===
QUOTES = [
    {"quote": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Aristotle"},
    {"quote": "Discipline is the bridge between goals and accomplishment.", "author": "Jim Rohn"},
    {"quote": "Small daily improvements are the key to staggering long-term results.", "author": "James Clear"},
    {"quote": "You don’t rise to the level of your goals. You fall to the level of your systems.", "author": "James Clear"},
    {"quote": "The pain of discipline is nothing like the pain of regret.", "author": "Sarah Bombell"},
    {"quote": "Consistency compounds.", "author": "Unknown"},
    {"quote": "Do something today that your future self will thank you for.", "author": "Unknown"},
    {"quote": "Success is nothing more than a few simple disciplines, practiced every day.", "author": "Jim Rohn"},
    {"quote": "The secret of your future is hidden in your daily routine.", "author": "Mike Murdock"},
    {"quote": "Mastery is time and intense focus.", "author": "Robert Greene"},
]

# === DATA HANDLING ===
def load_user_data(username: str) -> Dict[str, Any]:
    try:
        with open(DATA_FILES[username], "r") as f:
            return json.load(f)
    except:
        return {
            "habits": [],
            "tasks": [],
            "wake_up": "6:00 AM",
            "bed_time": "11:00 PM",
            "current_day": datetime.date.today().isoformat(),
            "checkins": {},
            "journal_entries": [],
            "gratitude": [],
            "streaks": {"habits": 0, "tasks": 0},
            "quote_index": 0,
            "daily_schedule": {}  # hour: [task names]
        }

def save_user_data(username: str, data: Dict[str, Any]):
    with open(DATA_FILES[username], "w") as f:
        json.dump(data, f, indent=2)

# === APP ===
st.set_page_config(page_title="Daily Discipline", layout="wide")
st.title("Daily Discipline Tracker — 6 AM to 11 PM")

user = st.sidebar.selectbox("Login", USERS)
data = load_user_data(user)
current_day = datetime.date.today().isoformat()

# Reset daily
if data["current_day"] != current_day:
    data["current_day"] = current_day
    data["checkins"] = {}
    data["journal_entries"] = []
    data["quote_index"] = 0
    data["daily_schedule"] = {}
    save_user_data(user, data)

# === HOURS: 6:00 AM – 11:00 PM ===
hours = [f"{h:02d}:00 {'AM' if h < 12 else 'PM'}" for h in range(6, 24)]
if h == 12: hours[h-6] = "12:00 PM"
if h == 0: hours[h-6] = "12:00 AM"

# Auto-schedule tasks if not done
if data["tasks"] and not data["daily_schedule"]:
    priority_tasks = sorted(data["tasks"], key=lambda t: t.get("priority", 3))
    for i, task in enumerate(priority_tasks):
        if i < len(hours):
            hour = hours[i]
            if hour not in data["daily_schedule"]:
                data["daily_schedule"][hour] = []
            data["daily_schedule"][hour].append(task["name"])

# === TABS ===
tab1, tab2, tab3, tab4 = st.tabs(["Setup", "Daily Schedule", "Check-In", "End of Day"])

# === TAB 1: SETUP ===
with tab1:
    st.header("Setup")
    col1, col2 = st.columns(2)
    with col1:
        data["wake_up"] = st.selectbox("Wake Up", hours, index=hours.index("6:00 AM"))
    with col2:
        data["bed_time"] = st.selectbox("Bed Time", hours, index=hours.index("11:00 PM"))

    st.subheader("Habits")
    habit_input = st.text_area("Add habits (one per line)", "\n".join(data["habits"]))
    if st.button("Save Habits"):
        data["habits"] = [h.strip() for h in habit_input.split("\n") if h.strip()]
        save_user_data(user, data)
        st.success("Habits saved!")

    st.subheader("Add Tasks")
    task_name = st.text_input("Task Name")
    task_priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: ["Urgent", "Important", "Optional"][x-1])
    if st.button("Add Task"):
        data["tasks"].append({"name": task_name, "priority": task_priority, "completed": False})
        save_user_data(user, data)
        st.success("Task added!")

    if data["tasks"]:
        st.write("**Your Tasks**")
        for i, t in enumerate(data["tasks"]):
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.write(f"{t['name']} (P{t['priority']})")
            with col2:
                if st.button("✓", key=f"done_{i}"):
                    t["completed"] = True
                    save_user_data(user, data)
            with col3:
                if st.button("✗", key=f"undo_{i}"):
                    t["completed"] = False
                    save_user_data(user, data)

# === TAB 2: DAILY SCHEDULE (6 AM – 11 PM) ===
with tab2:
    st.header("Your Daily Schedule")
    current_hour = datetime.datetime.now().strftime("%I:%M %p")
    st.info(f"**Current Time: {current_hour}**")

    # Rotate quote hourly
    hour_index = datetime.datetime.now().hour
    quote = QUOTES[data["quote_index"] % len(QUOTES)]
    data["quote_index"] = (data["quote_index"] + 1) % len(QUOTES)
    st.success(f"**Quote of the Hour:**\n> “{quote['quote']}” — *{quote['author']}*")

    # Schedule table
    schedule_data = []
    for hour in hours:
        tasks = data["daily_schedule"].get(hour, [])
        status = "✅" if all(t in [tt["name"] for tt in data["tasks"] if tt["completed"]] for t in tasks) else "⏳"
        schedule_data.append({"Time": hour, "Tasks": ", ".join(tasks) if tasks else "—", "Status": status})

    df = pd.DataFrame(schedule_data)
    st.dataframe(df, use_container_width=True)

    # Progress
    total_tasks = len(data["tasks"])
    done_tasks = sum(1 for t in data["tasks"] if t["completed"])
    st.progress(done_tasks / total_tasks if total_tasks else 0)
    st.metric("Tasks Completed", f"{done_tasks}/{total_tasks}")

# === TAB 3: HOURLY CHECK-IN ===
with tab3:
    st.header("Hourly Check-In")
    selected_hour = st.selectbox("Check-in for", hours)
    for habit in data["habits"]:
        st.checkbox(habit, key=f"check_{habit}_{selected_hour}")
    if st.button("Log Check-In"):
        data["checkins"][selected_hour] = {"time": datetime.datetime.now().isoformat(), "habits": data["habits"]}
        save_user_data(user, data)
        st.balloons()

# === TAB 4: END OF DAY ===
with tab4:
    st.header("End of Day")
    if st.button("Generate Report"):
        st.success("Day Complete!")
        done = sum(1 for t in data["tasks"] if t["completed"])
        st.metric("Tasks Done", f"{done}/{len(data['tasks'])}")
        st.subheader("Gratitude")
        g1 = st.text_input("1. Grateful for...")
        g2 = st.text_input("2. Grateful for...")
        g3 = st.text_input("3. Grateful for...")
        if st.button("Save"):
            data["gratitude"].append([g1, g2, g3])
            save_user_data(user, data)
            st.success("Saved!")

save_user_data(user, data)