"""Main Streamlit application."""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Jobly - AI Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_user"

if "profile_loaded" not in st.session_state:
    st.session_state.profile_loaded = False

# Sidebar
with st.sidebar:
    st.markdown("## 💼 Jobly")
    st.markdown("AI-Powered Job Search Assistant")
    st.markdown("---")

    # User info
    st.markdown(f"**User:** {st.session_state.user_id}")
    st.markdown(f"**Profile:** {'✅ Loaded' if st.session_state.profile_loaded else '⚠️ Not loaded'}")

    st.markdown("---")

    # Navigation hint
    st.info("👈 Use the sidebar to navigate between pages")

    st.markdown("---")

    # Quick stats (placeholder)
    st.markdown("### Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Applications", "0")
    with col2:
        st.metric("Responses", "0")

# Main content
st.markdown('<p class="main-header">Welcome to Jobly 👋</p>', unsafe_allow_html=True)

st.markdown("""
## Your AI-Powered Job Search Assistant

Jobly automates your entire job search workflow with 17 specialized AI agents:

### 🚀 What Jobly Does

1. **Profile Management** - Parse your resume and build your profile
2. **Job Discovery** - Search and scrape jobs from multiple sources
3. **Smart Ranking** - AI ranks jobs based on your profile fit
4. **Document Generation** - Tailor resumes and cover letters
5. **Networking** - Discover contacts and craft outreach messages
6. **Application Tracking** - Monitor applications and interviews
7. **Analytics** - Get insights on your job search performance

### 🎯 Getting Started

1. Go to **Profile** page to upload your resume
2. Visit **Jobs** page to discover opportunities
3. Use **Networking** to connect with hiring managers
4. Track progress on the **Dashboard**

### 📊 Navigation

Use the sidebar to navigate between different sections:
- 📊 **Dashboard** - Overview and metrics
- 💼 **Jobs** - Job discovery and management
- 👤 **Profile** - Your profile and resume
- 🤝 **Networking** - Contacts and outreach
- 📄 **Documents** - Resumes and cover letters
- 🎤 **Interviews** - Interview preparation
- 📈 **Analytics** - Performance insights
""")

# Call to action
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Upload Resume"):
        st.switch_page("pages/3_👤_Profile.py")

with col2:
    if st.button("🔍 Find Jobs"):
        st.switch_page("pages/2_💼_Jobs.py")

with col3:
    if st.button("📊 View Dashboard"):
        st.switch_page("pages/1_📊_Dashboard.py")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and AI")
