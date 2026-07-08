import streamlit as st
import sqlite3
import os

st.set_page_config(
    page_title="People's Priorities Dashboard",
    page_icon="🏛️",
    layout="wide"
)

# 1. Secure Password Key Input Frame inside Sidebar
with st.sidebar:
    st.markdown("### 🔑 Authentication")
    user_key = st.text_input(
        "Enter your Gemini API Key:", 
        type="password",  # Hides your key behind bullet points
        placeholder=""    # Kept completely blank as requested
    )
    
    if user_key:
        st.session_state["TEMPORARY_GEMINI_KEY"] = user_key
        st.success("API Key loaded into active memory!")
    else:
        st.warning("Running in Offline Demo mode. Enter key to activate live AI.")

    st.markdown("---")
    st.markdown("### ⚙️ System Tools")
    
    # SYSTEM RESET BUTTON: Clears old misplaced database rows instantly
    if st.button("🗑️ Reset All Cache Data", use_container_width=True):
        if os.path.exists("peoples_priorities.db"):
            try:
                conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS complaints")
                conn.commit()
                conn.close()
                st.success("Database wiped successfully! Please log a fresh ticket.")
                st.rerun()
            except Exception as e:
                st.error(f"Reset Error: {str(e)}")

# 2. Initialize Local Serverless Database file with spatial data columns
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

# 3. Setup Multi-Page Navigation 
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
