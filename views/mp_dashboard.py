import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Constituency Intelligence Dashboard")
st.subheader("Aggregated metrics across local problem corridors")

# Read active data table straight out of your local SQLite file
conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM complaints", conn)
conn.close()

if df.empty:
    st.info("The database file is currently empty. Visit the Citizen Portal to submit sample records.")
elif "latitude" not in df.columns or "longitude" not in df.columns or df["latitude"].isnull().all():
    st.warning("⚠️ Data structure update detected. Please click the Reset Cache button in the sidebar.")
else:
    # Top KPI summary cards
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Logged Grievances", len(df))
    kpi2.metric("Critical Hotspots (Urgency >= 7)", len(df[df['urgency_score'] >= 7]))
    kpi3.metric("Verified Actions Pending", len(df[df['status'] == 'Verified']))

    st.markdown("### 🗺️ Constituency Hotspot Density Map")
    st.caption("Map view camera automatically frames your exact reported neighborhood corridors.")
    
    # Dynamic camera centering adjustments based on rows logged
    if len(df) == 1:
        avg_lat = df["latitude"].iloc[0]
        avg_lon = df["longitude"].iloc[0]
        map_zoom = 13  # Zoom in closely if there's only one complaint
    else:
        avg_lat = df["latitude"].mean()
        avg_lon = df["longitude"].mean()
        map_zoom = 11  # Show the whole city view if multiple locations are active
    
    fig_map = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
        color="category", 
        size="urgency_score",
        hover_name="id",
        hover_data=["summary", "status", "urgency_score"],
        zoom=map_zoom,
        height=500
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map", 
        mapbox=dict(center=dict(lat=avg_lat, lon=avg_lon)),
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
