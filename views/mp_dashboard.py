import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Constituency Intelligence Dashboard")

# Read active data table straight out of your local SQLite file
conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM complaints", conn)
conn.close()

if df.empty:
    st.info("The database file is currently empty. Visit the Citizen Portal to submit sample records.")
elif "latitude" not in df.columns or "longitude" not in df.columns or df["latitude"].isnull().all():
    st.warning("⚠️ Data structure update detected. Please log a fresh complaint in the Citizen Portal to generate the map.")
else:
    # Top KPI summary cards
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Logged Grievances", len(df))
    kpi2.metric("Critical Hotspots (Urgency >= 7)", len(df[df['urgency_score'] >= 7]))
    kpi3.metric("Verified Actions Pending", len(df[df['status'] == 'Verified']))

    st.markdown("### 🗺️ Constituency Hotspot Density Map")
    st.caption("Bubble size indicates issue severity score. Color indicates complaint division.")
    
    # DYNAMIC AUTO-CENTER CORRECTION: 
    # Calculate the exact center point based on all matching user rows currently logged
    avg_lat = df["latitude"].mean()
    avg_lon = df["longitude"].mean()
    
    fig_map = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
        color="category", 
        size="urgency_score",
        hover_name="id",
        hover_data=["summary", "status", "urgency_score"],
        zoom=11,  # Adjusts zoom tightly (Higher number means closer zoom)
        height=500
    )
    
    # Force layout engine to snap directly to the calculated coordinates
    fig_map.update_layout(
        mapbox_style="open-street-map", 
        mapbox=dict(
            center=dict(lat=avg_lat, lon=avg_lon)  # Centers the camera position exactly
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_map, use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### Total Case Load Volume")
        cat_distribution = df['category'].value_counts().reset_index()
        fig_pie = px.pie(cat_distribution, values='count', names='category', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_right:
        st.markdown("### Severity Distribution Map Matrix")
        fig_bar = px.bar(df, x="category", y="urgency_score", color="status", barmode="group")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### Complete Operational Database Logs")
    st.dataframe(df, use_container_width=True)
