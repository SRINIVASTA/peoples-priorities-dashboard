import streamlit as st
import sqlite3

st.set_page_config(
    page_title="People's Priorities Dashboard",
    page_icon="🏛️",
    layout="wide"
)

with st.sidebar:
    st.markdown("### 🔑 Authentication")
    user_key = st.text_input(
        "Enter your Gemini API Key:", 
        type="password",  
        placeholder=""    
    )
    if user_key:
        st.session_state["TEMPORARY_GEMINI_KEY"] = user_key
        st.success("API Key loaded into active memory!")
    else:
        st.warning("Running in Offline Demo mode. Enter key to activate live AI.")

# Initialize Local Serverless Database file with Lat/Lon fields
conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
cursor = conn.cursor()
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
