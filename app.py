import streamlit as st
import sqlite3

st.set_page_config(
    page_title="People's Priorities Dashboard",
    page_icon="🏛️",
    layout="wide"
)

# Render a clean sidebar key input frame
with st.sidebar:
    st.markdown("### 🔑 Authentication")
    user_key = st.text_input(
        "Enter your Gemini API Key:", 
        type="password",  
        placeholder=""
    )
    if user_key:
        st.session_state["TEMPORARY_GEMINI_KEY"] = user_key
        st.success("API Key loaded into memory!")
    else:
        st.warning("Please enter your key to activate AI features.")

# FORCE RESET: This creates a clean table with matching columns on Streamlit Cloud
conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
cursor = conn.cursor()

# We drop the old structural format if it exists to clean out column mismatch errors
cursor.execute("DROP TABLE IF EXISTS complaints")

# Create the fresh table structure with explicit geolocation columns
cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        category TEXT,
        urgency_score INTEGER,
        summary TEXT,
        status TEXT,
        latitude REAL,
        longitude REAL
    )
""")
conn.commit()
conn.close()

# App Navigation Setup
pages = {
    "For Citizens": [
        st.Page("views/citizen_chat.py", title="🗣️ Report an Issue", icon="💬")
    ],
    "For MPs & Staff": [
        st.Page("views/mp_dashboard.py", title="📊 View MP Dashboard", icon="📈"),
        st.Page("views/staff_console.py", title="🛡️ Staff Verification Console", icon="⚙️")
    ]
}

pg = st.navigation(pages)
pg.run()
