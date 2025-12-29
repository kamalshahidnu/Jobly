"""Analytics page for insights and statistics."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Analytics - Jobly", page_icon="📈", layout="wide")

st.title("📈 Analytics & Insights")
st.markdown("Track your job search performance")

# Date range selector
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    start_date = st.date_input("From", datetime.now() - timedelta(days=30))

with col2:
    end_date = st.date_input("To", datetime.now())

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Key metrics
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Applications Sent",
        value="0",
        delta="0 this week"
    )

with col2:
    st.metric(
        label="Response Rate",
        value="0%",
        delta="0%"
    )

with col3:
    st.metric(
        label="Interview Rate",
        value="0%",
        delta="0%"
    )

with col4:
    st.metric(
        label="Offer Rate",
        value="0%",
        delta="0%"
    )

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Applications Over Time")

    # Example data
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'Applications': np.zeros(len(dates))
    })

    st.line_chart(data.set_index('Date'))

with col2:
    st.subheader("🎯 Application Status Distribution")

    # Example data
    status_data = pd.DataFrame({
        'Status': ['Applied', 'Interviewing', 'Rejected', 'Offer'],
        'Count': [0, 0, 0, 0]
    })

    st.bar_chart(status_data.set_index('Status'))

st.markdown("---")

# Response time analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏱️ Response Time")

    response_data = {
        "Metric": ["Average", "Median", "Fastest", "Slowest"],
        "Days": [0, 0, 0, 0]
    }
    df_response = pd.DataFrame(response_data)

    st.dataframe(df_response, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🏢 Top Companies")

    company_data = {
        "Company": ["No data yet"],
        "Applications": [0]
    }
    df_companies = pd.DataFrame(company_data)

    st.dataframe(df_companies, use_container_width=True, hide_index=True)

st.markdown("---")

# Success metrics
st.subheader("🎯 Success Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Conversion Funnel")
    funnel_data = {
        "Stage": ["Applied", "Responded", "Interviewed", "Offered", "Accepted"],
        "Count": [0, 0, 0, 0, 0],
        "Rate": ["100%", "0%", "0%", "0%", "0%"]
    }
    df_funnel = pd.DataFrame(funnel_data)
    st.dataframe(df_funnel, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### Best Performing")
    st.markdown("**Job Source:** N/A")
    st.markdown("**Job Type:** N/A")
    st.markdown("**Application Method:** N/A")

with col3:
    st.markdown("### Recommendations")
    st.info("Apply to more jobs to get insights!")

st.markdown("---")

# Activity heatmap
st.subheader("🔥 Activity Heatmap")

# Create example heatmap data
heatmap_data = pd.DataFrame(
    np.zeros((7, 24)),
    index=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    columns=[f"{i:02d}:00" for i in range(24)]
)

st.info("Heatmap would show your application activity by day/time")

st.markdown("---")

# Export section
st.subheader("📥 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export Analytics Report", use_container_width=True):
        st.info("Analytics report would be exported")

with col2:
    if st.button("📄 Export Applications CSV", use_container_width=True):
        st.info("Applications data would be exported")

with col3:
    if st.button("📈 Export Charts", use_container_width=True):
        st.info("Charts would be exported")
