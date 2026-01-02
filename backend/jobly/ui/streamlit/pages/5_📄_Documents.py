"""Documents page for resume and cover letter management."""

import streamlit as st

st.set_page_config(page_title="Documents - Jobly", page_icon="📄", layout="wide")

st.title("📄 Documents")
st.markdown("Manage resumes and cover letters")

# Tabs for different document types
tab1, tab2 = st.tabs(["📝 Resumes", "💌 Cover Letters"])

with tab1:
    st.subheader("Resume Management")

    # Generate/Tailor section
    with st.expander("✨ Generate Tailored Resume", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            job_select = st.selectbox(
                "Select Target Job (Optional)",
                ["General Resume", "Job 1", "Job 2"],
                help="Select a job to tailor your resume specifically for it"
            )

        with col2:
            template = st.selectbox(
                "Template",
                ["Professional", "Modern", "Creative", "ATS-Friendly"]
            )

        if st.button("✨ Generate Resume", type="primary", use_container_width=True):
            with st.spinner("Generating resume..."):
                st.success("Resume would be generated here!")

    st.markdown("---")

    st.subheader("My Resumes (0)")

    # Example resume
    with st.expander("Example Resume"):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown("**General_Resume_2024.pdf**")
            st.markdown("Created: 2024-01-15 | Last modified: 2024-01-20")

        with col2:
            st.button("📥 Download", key="resume_dl1")
            st.button("👁️ Preview", key="resume_prev1")

        with col3:
            st.button("✏️ Edit", key="resume_edit1")
            st.button("🗑️ Delete", key="resume_del1")

with tab2:
    st.subheader("Cover Letter Management")

    # Generate section
    with st.expander("✨ Generate Cover Letter", expanded=True):
        job_select_cl = st.selectbox(
            "Select Target Job",
            ["Select a job..."],
            help="Cover letters are job-specific",
            key="cl_job"
        )

        tone = st.select_slider(
            "Tone",
            options=["Formal", "Professional", "Conversational", "Enthusiastic"],
            value="Professional"
        )

        additional_notes = st.text_area(
            "Additional Notes",
            placeholder="Any specific points you want to highlight...",
            height=100
        )

        if st.button("✨ Generate Cover Letter", type="primary", use_container_width=True):
            if job_select_cl == "Select a job...":
                st.warning("Please select a target job first!")
            else:
                with st.spinner("Generating cover letter..."):
                    st.success("Cover letter would be generated here!")

    st.markdown("---")

    st.subheader("My Cover Letters (0)")
    st.info("No cover letters yet. Generate one above!")

st.markdown("---")

# Document stats
st.subheader("📊 Document Stats")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Resumes", "0")

with col2:
    st.metric("Cover Letters", "0")

with col3:
    st.metric("Templates Used", "0")
