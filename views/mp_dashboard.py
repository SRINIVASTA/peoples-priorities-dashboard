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
else:
    # Top KPI summary cards
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Logged Grievances", len(df))
    kpi2.metric("Critical Hotspots (Urgency >= 7)", len(df[df['urgency_score'] >= 7]))
    kpi3.metric("Verified Actions Pending", len(df[df['status'] == 'Verified']))

    # Chart presentation matrix
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
