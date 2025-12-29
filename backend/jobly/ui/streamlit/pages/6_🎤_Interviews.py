"""Interviews page for interview preparation and tracking."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Interviews - Jobly", page_icon="🎤", layout="wide")

st.title("🎤 Interviews")
st.markdown("Prepare for and track your interviews")

# Tabs
tab1, tab2, tab3 = st.tabs(["📅 Upcoming", "📚 Preparation", "📝 History"])

with tab1:
    st.subheader("Upcoming Interviews")

    # Add interview
    with st.expander("➕ Schedule New Interview"):
        col1, col2 = st.columns(2)

        with col1:
            job_title = st.text_input("Job Title", key="int_job")
            company = st.text_input("Company", key="int_company")
            interview_type = st.selectbox(
                "Interview Type",
                ["Phone Screen", "Technical", "Behavioral", "System Design", "Onsite", "Final"]
            )

        with col2:
            interview_date = st.date_input("Date", key="int_date")
            interview_time = st.time_input("Time", key="int_time")
            interviewer = st.text_input("Interviewer", key="int_interviewer")

        notes = st.text_area("Notes", key="int_notes", height=100)

        if st.button("📅 Schedule Interview", type="primary"):
            st.success("Interview would be scheduled here!")

    st.markdown("---")

    # List of interviews
    st.info("No upcoming interviews scheduled")

    # Example interview
    with st.expander("Example Interview"):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("### Technical Interview - Software Engineer")
            st.markdown("**Company:** Tech Corp")
            st.markdown("**Date:** Tomorrow at 2:00 PM")
            st.markdown("**Type:** Technical Round")
            st.markdown("**Interviewer:** John Doe")

        with col2:
            st.button("🎯 Prepare", key="prep1")
            st.button("✏️ Edit", key="edit1")
            st.button("❌ Cancel", key="cancel1")

with tab2:
    st.subheader("📚 Interview Preparation")

    job_for_prep = st.selectbox(
        "Select Job/Interview",
        ["Select an interview..."],
        key="prep_job"
    )

    if job_for_prep == "Select an interview...":
        st.info("Select an upcoming interview to generate preparation materials")
    else:
        if st.button("✨ Generate Prep Materials", type="primary", use_container_width=True):
            with st.spinner("Generating interview prep materials..."):
                # Example prep materials
                st.success("Preparation materials generated!")

                st.markdown("### 🎯 Key Talking Points")
                st.markdown("""
                - Your experience with Python and system design
                - Recent project on microservices architecture
                - Leadership experience from previous role
                """)

                st.markdown("### 💡 Likely Questions")
                with st.expander("Technical Questions"):
                    st.markdown("1. Design a URL shortening service")
                    st.markdown("2. Implement a LRU cache")
                    st.markdown("3. Explain your approach to testing")

                with st.expander("Behavioral Questions"):
                    st.markdown("1. Tell me about a challenging project")
                    st.markdown("2. How do you handle conflicts in a team?")
                    st.markdown("3. Describe a time you failed")

                st.markdown("### ❓ Questions to Ask")
                st.markdown("""
                - What does a typical day look like?
                - How does the team handle technical debt?
                - What are the biggest challenges facing the team?
                """)

with tab3:
    st.subheader("📝 Interview History")

    st.info("No past interviews recorded")

    # Stats
    st.markdown("---")
    st.subheader("📊 Interview Stats")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Interviews", "0")

    with col2:
        st.metric("Success Rate", "0%")

    with col3:
        st.metric("Avg Preparation Time", "0h")

    with col4:
        st.metric("Next Interview", "None")
