"""Jobs page for job discovery and management."""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Jobs - Jobly", page_icon="💼", layout="wide")

st.title("💼 Job Search")
st.markdown("Discover and manage job opportunities")

# Search section
with st.expander("🔍 Search Parameters", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        keywords = st.text_input("Keywords", placeholder="e.g., Software Engineer")
        location = st.text_input("Location", placeholder="e.g., Remote, San Francisco")

    with col2:
        job_type = st.multiselect(
            "Job Type",
            ["Full-time", "Part-time", "Contract", "Internship"],
            default=["Full-time"]
        )
        sources = st.multiselect(
            "Sources",
            ["LinkedIn", "Indeed", "Glassdoor", "Company Sites"],
            default=["LinkedIn"]
        )

    with col3:
        min_salary = st.number_input("Min Salary ($)", value=0, step=10000)
        max_results = st.slider("Max Results", 10, 100, 50)

    if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
        with st.spinner("Searching for jobs..."):
            st.success("Search would be performed here!")

st.markdown("---")

# Filters and sorting
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "Status",
        ["All", "New", "Ranked", "Applied", "Interviewing"]
    )

with col2:
    sort_by = st.selectbox(
        "Sort By",
        ["Match Score", "Date Posted", "Salary", "Company"]
    )

with col3:
    view_mode = st.radio(
        "View",
        ["Cards", "List", "Table"],
        horizontal=True
    )

st.markdown("---")

# Jobs display
st.subheader(f"Available Jobs (0)")

# Placeholder for jobs
if True:  # No jobs condition
    st.info("👆 Use the search parameters above to find jobs")
    st.markdown("""
    ### How it works:
    1. Enter your search criteria (keywords, location, etc.)
    2. AI agents will search multiple job boards
    3. Jobs are automatically deduplicated and ranked
    4. Review matches and take action
    """)

# Example of how job cards would look
with st.expander("Example Job Card"):
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### Senior Software Engineer")
        st.markdown("**Company:** Tech Corp")
        st.markdown("📍 San Francisco, CA | 💰 $150k-$200k | ⏰ Full-time")
        st.markdown("**Match Score:** 85/100")
        st.markdown("Posted 2 days ago")

    with col2:
        st.button("View Details", key="example1")
        st.button("Apply", key="example2", type="primary")
        st.button("Skip", key="example3")
