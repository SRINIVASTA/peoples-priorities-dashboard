import streamlit as st
import sqlite3
import pandas as pd

st.title("🛡️ Operational Staff Console")
st.caption("Edit verification columns and save state changes back to the main database framework.")

# Fetch active database records
conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM complaints", conn)
conn.close()

if df.empty:
    st.info("No incoming data lines to manage.")
else:
    # Creates an editable data spreadsheet interface inside the UI frame
    edited_df = st.data_editor(
        df,
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Status Verification", 
                options=["Pending", "Verified", "Resolved"], 
                required=True
            )
        },
        disabled=["id", "category", "urgency_score", "summary"],  # Lock core data fields
        use_container_width=True
    )
    
    # Save button handles syncing changes back to your local file
    if st.button("Commit Grid State Updates"):
        conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
        cursor = conn.cursor()
        for _, row in edited_df.iterrows():
            cursor.execute(
                "UPDATE complaints SET status = ? WHERE id = ?", 
                (row['status'], row['id'])
            )
        conn.commit()
        conn.close()
        st.success("Changes successfully pushed to database file!")
        st.rerun()
