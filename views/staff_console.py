import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🛡️ Operational Staff Console")

conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM complaints", conn)
conn.close()

if df.empty:
    st.info("No incoming data lines to manage.")
else:
    st.markdown("### 📍 Verification Status Map Tracking")
    st.caption("Color maps active task standing. Ensure 'Pending' nodes are verified quickly.")
    
    # Dynamic center calculation for staff view
    avg_lat = df["latitude"].mean()
    avg_lon = df["longitude"].mean()
    
    fig_staff_map = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="status",  
        hover_name="id",
        hover_data=["category", "urgency_score", "summary"],
        zoom=11,
        height=400,
        color_discrete_map={"Pending": "red", "Verified": "orange", "Resolved": "green"}
    )
    
    # Snap staff view map straight onto active target area
    fig_staff_map.update_layout(
        mapbox_style="open-street-map", 
        mapbox=dict(
            center=dict(lat=avg_lat, lon=avg_lon)
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_staff_map, use_container_width=True)

    st.markdown("### 📝 Edit Operational State Metrics")
    edited_df = st.data_editor(
        df,
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Status Verification", options=["Pending", "Verified", "Resolved"], required=True
            )
        },
        disabled=["id", "category", "urgency_score", "summary", "latitude", "longitude"],
        use_container_width=True
    )
    
    if st.button("Commit Grid State Updates"):
        conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
        cursor = conn.cursor()
        for _, row in edited_df.iterrows():
            cursor.execute("UPDATE complaints SET status = ? WHERE id = ?", (row['status'], row['id']))
        conn.commit()
        conn.close()
        st.success("Changes successfully pushed to database file!")
        st.rerun()
