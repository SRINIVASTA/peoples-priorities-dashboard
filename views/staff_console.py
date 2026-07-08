import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🛡️ Operational Staff Console")
st.caption("Edit verification columns and save state changes back to the main database framework.")

# Fetch active database records
conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM complaints", conn)
conn.close()

if df.empty:
    st.info("No incoming data lines to manage.")
elif "latitude" not in df.columns or "longitude" not in df.columns or df["latitude"].isnull().all():
    st.warning("⚠️ Data structure update detected. Please click the Reset Cache button in the sidebar.")
else:
    st.markdown("### 📍 Verification Status Map Tracking")
    st.caption("Color maps active task standing. Ensure 'Pending' nodes are verified quickly.")
    
    # Calculate centering viewport for staff tracking view
    if len(df) == 1:
        avg_lat = df["latitude"].iloc[0]
        avg_lon = df["longitude"].iloc[0]
        map_zoom = 13
    else:
        avg_lat = df["latitude"].mean()
        avg_lon = df["longitude"].mean()
        map_zoom = 11
    
    fig_staff_map = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="status",  # Grouped by status to assist deployment workflows
        hover_name="id",
        hover_data=["category", "urgency_score", "summary"],
        zoom=map_zoom,
        height=400,
        color_discrete_map={"Pending": "red", "Verified": "orange", "Resolved": "green"}
    )
    
    fig_staff_map.update_layout(
        mapbox_style="open-street-map", 
        mapbox=dict(center=dict(lat=avg_lat, lon=avg_lon)),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_staff_map, use_container_width=True)

    st.markdown("### 📝 Edit Operational State Metrics")
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
        disabled=["id", "category", "urgency_score", "summary", "latitude", "longitude"],  # Lock data fields
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
