"""Dashboard page for overview and metrics."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard - Jobly", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.markdown("Overview of your job search activity")

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Applications",
        value="0",
        delta="0 this week"
    )

with col2:
    st.metric(
        label="Active Leads",
        value="0",
        delta="0 new"
    )

with col3:
    st.metric(
        label="Interviews",
        value="0",
        delta="0 scheduled"
    )

with col4:
    st.metric(
        label="Response Rate",
        value="0%",
        delta="0%"
    )

st.markdown("---")

# Pipeline view
st.subheader("Application Pipeline")

pipeline_data = {
    "Stage": ["Discovered", "Ranked", "Applied", "Interviewing", "Offer"],
    "Count": [0, 0, 0, 0, 0]
}
df_pipeline = pd.DataFrame(pipeline_data)

col1, col2 = st.columns([2, 1])

with col1:
    st.bar_chart(df_pipeline.set_index("Stage"))

with col2:
    st.dataframe(df_pipeline, use_container_width=True, hide_index=True)

st.markdown("---")

# Recent activity
st.subheader("Recent Activity")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📬 Latest Applications")
    st.info("No recent applications")

with col2:
    st.markdown("### 📅 Upcoming Interviews")
    st.info("No upcoming interviews")

st.markdown("---")

# Quick actions
st.subheader("Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Search Jobs", use_container_width=True):
        st.switch_page("pages/2_💼_Jobs.py")

with col2:
    if st.button("📝 Update Profile", use_container_width=True):
        st.switch_page("pages/3_👤_Profile.py")

with col3:
    if st.button("🤝 Network", use_container_width=True):
        st.switch_page("pages/4_🤝_Networking.py")

with col4:
    if st.button("📈 View Analytics", use_container_width=True):
        st.switch_page("pages/7_📈_Analytics.py")
