"""Profile page for user profile management."""

import streamlit as st

st.set_page_config(page_title="Profile - Jobly", page_icon="👤", layout="wide")

st.title("👤 Your Profile")
st.markdown("Manage your professional profile")

# Profile status
if not st.session_state.get("profile_loaded", False):
    st.warning("⚠️ No profile loaded. Upload your resume to get started!")

# Resume upload section
st.subheader("📤 Resume Upload")

uploaded_file = st.file_uploader(
    "Upload your resume (PDF, DOCX)",
    type=["pdf", "docx"],
    help="AI will parse your resume to build your profile"
)

if uploaded_file:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

    with col2:
        if st.button("Parse Resume", type="primary", use_container_width=True):
            with st.spinner("Parsing resume..."):
                st.success("Resume would be parsed here!")
                st.session_state.profile_loaded = True

st.markdown("---")

# Profile information
st.subheader("📋 Profile Information")

col1, col2 = st.columns(2)

with col1:
    st.text_input("Full Name", placeholder="John Doe")
    st.text_input("Email", placeholder="john@example.com")
    st.text_input("Phone", placeholder="+1 (555) 123-4567")
    st.text_input("Location", placeholder="San Francisco, CA")

with col2:
    st.number_input("Years of Experience", min_value=0, max_value=50, value=5)
    st.text_input("Current Title", placeholder="Software Engineer")
    st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/johndoe")
    st.text_input("GitHub URL", placeholder="https://github.com/johndoe")

st.markdown("---")

# Skills
st.subheader("🛠️ Skills")

skills_input = st.text_area(
    "Enter your skills (comma-separated)",
    placeholder="Python, JavaScript, React, Node.js, AWS, Docker",
    height=100
)

st.markdown("---")

# Work experience
st.subheader("💼 Work Experience")

with st.expander("Add Work Experience"):
    st.text_input("Company", key="work_company")
    st.text_input("Title", key="work_title")
    col1, col2 = st.columns(2)
    with col1:
        st.date_input("Start Date", key="work_start")
    with col2:
        st.date_input("End Date", key="work_end")
    st.text_area("Description", key="work_desc", height=150)
    st.button("Add Experience", type="primary")

st.info("No work experience added yet")

st.markdown("---")

# Actions
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Profile", type="primary", use_container_width=True):
        st.success("Profile would be saved here!")

with col2:
    if st.button("🔄 Refresh from Resume", use_container_width=True):
        st.info("Profile would be refreshed from resume")

with col3:
    if st.button("📥 Export Profile", use_container_width=True):
        st.info("Profile would be exported")
