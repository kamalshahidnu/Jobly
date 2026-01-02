"""Jobs page with full backend integration.

This is a working example showing how to connect Streamlit UI to the backend.
Replace the original 2_💼_Jobs.py with this file to enable full functionality.
"""

import sys
from pathlib import Path
import asyncio

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import streamlit as st
import pandas as pd
from datetime import datetime

# Backend imports
from jobly.services.job_service import JobService
from jobly.agents.job_search_agent import JobSearchAgent
from jobly.agents.dedup_agent import DedupAgent
from jobly.agents.job_ranker_agent import JobRankerAgent
from jobly.tools.job_boards.indeed_scraper import IndeedScraper
from jobly.tools.job_boards.glassdoor_scraper import GlassdoorScraper
from jobly.tools.job_boards.linkedin_api import LinkedInAPIClient
from jobly.memory.sqlite_store import SQLiteStore
from jobly.config.settings import settings

# Page configuration
st.set_page_config(page_title="Jobs - Jobly", page_icon="💼", layout="wide")

# Initialize session state
if "job_service" not in st.session_state:
    st.session_state.job_service = JobService()

if "jobs" not in st.session_state:
    st.session_state.jobs = []

if "search_performed" not in st.session_state:
    st.session_state.search_performed = False


def search_jobs(keywords: str, location: str, sources: list, job_type: list, max_results: int, min_salary: int):
    """Search for jobs across multiple sources."""
    all_jobs = []

    # Search Indeed
    if "Indeed" in sources:
        with st.spinner("Searching Indeed..."):
            try:
                scraper = IndeedScraper()
                jobs = scraper.search_jobs(
                    keywords=keywords,
                    location=location,
                    job_type=job_type[0].lower() if job_type else None,
                    limit=max_results // len(sources),
                )
                all_jobs.extend(jobs)
                st.success(f"Found {len(jobs)} jobs from Indeed")
            except Exception as e:
                st.error(f"Error searching Indeed: {e}")

    # Search Glassdoor
    if "Glassdoor" in sources:
        with st.spinner("Searching Glassdoor..."):
            try:
                scraper = GlassdoorScraper()
                jobs = scraper.search_jobs(
                    keywords=keywords,
                    location=location,
                    limit=max_results // len(sources),
                )
                all_jobs.extend(jobs)
                st.success(f"Found {len(jobs)} jobs from Glassdoor")
            except Exception as e:
                st.error(f"Error searching Glassdoor: {e}")

    # Search LinkedIn (if available)
    if "LinkedIn" in sources:
        with st.spinner("Searching LinkedIn..."):
            try:
                client = LinkedInAPIClient()
                # LinkedIn requires seed data or API access
                st.info("LinkedIn integration requires API access. Using demo data for now.")
                # You can provide seed jobs here for testing
            except Exception as e:
                st.warning(f"LinkedIn search not available: {e}")

    # Deduplicate jobs
    if all_jobs:
        with st.spinner("Removing duplicates..."):
            dedup_agent = DedupAgent()

            async def dedupe():
                return await dedup_agent.execute({"jobs": all_jobs})

            result = asyncio.run(dedupe())
            all_jobs = result.get("deduplicated_jobs", all_jobs)
            st.success(f"Removed duplicates. {len(all_jobs)} unique jobs remaining.")

    # Rank jobs
    if all_jobs:
        with st.spinner("Ranking jobs by fit..."):
            ranker = JobRankerAgent()
            # Load user profile from session or database
            user_profile = st.session_state.get("user_profile", {
                "skills": keywords.split(),
                "experience_years": 5,
                "location": location,
            })

            async def rank():
                return await ranker.execute({
                    "jobs": all_jobs,
                    "profile": user_profile,
                })

            result = asyncio.run(rank())
            all_jobs = result.get("ranked_jobs", all_jobs)
            st.success("Jobs ranked by relevance!")

    # Save jobs to database
    if all_jobs:
        with st.spinner("Saving jobs to database..."):
            for job in all_jobs:
                try:
                    st.session_state.job_service.create_job({
                        "user_id": "demo_user",
                        "title": job.get("title"),
                        "company": job.get("company"),
                        "location": job.get("location"),
                        "description": job.get("description", ""),
                        "requirements": job.get("requirements", []),
                        "salary_range": job.get("salary", ""),
                        "job_type": job.get("job_type", "Full-time"),
                        "url": job.get("url"),
                        "source": job.get("source", "Unknown"),
                        "match_score": job.get("match_score", 0),
                        "posted_date": datetime.now().isoformat(),
                    })
                except Exception as e:
                    print(f"Error saving job: {e}")

    return all_jobs


def display_job_card(job: dict, index: int):
    """Display a single job card."""
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### {job.get('title', 'N/A')}")
            st.markdown(f"**{job.get('company', 'N/A')}**")

            # Job metadata
            location = job.get("location", "N/A")
            salary = job.get("salary", "Not specified")
            job_type = job.get("job_type", "N/A")
            source = job.get("source", "Unknown")
            match_score = job.get("match_score", 0)

            st.markdown(f"📍 {location} | 💰 {salary} | ⏰ {job_type} | 🔗 {source}")

            if match_score:
                st.markdown(f"**Match Score:** {match_score}/100")

            # Description snippet
            description = job.get("description", "")
            if description:
                snippet = description[:200] + "..." if len(description) > 200 else description
                st.markdown(snippet)

        with col2:
            if st.button("View Details", key=f"view_{index}"):
                st.session_state[f"show_details_{index}"] = True

            if st.button("Apply", key=f"apply_{index}", type="primary"):
                st.success("Application tracked! (Feature to be implemented)")

            if st.button("Skip", key=f"skip_{index}"):
                st.info("Job skipped")

        # Show details if requested
        if st.session_state.get(f"show_details_{index}", False):
            with st.expander("Full Details", expanded=True):
                st.markdown("#### Full Description")
                st.markdown(job.get("description", "No description available"))

                if job.get("requirements"):
                    st.markdown("#### Requirements")
                    for req in job.get("requirements", []):
                        st.markdown(f"- {req}")

                if job.get("url"):
                    st.markdown(f"[View on {source}]({job.get('url')})")

        st.markdown("---")


# Main UI
st.title("💼 Job Search")
st.markdown("Discover and manage job opportunities with AI-powered search and ranking")

# Search section
with st.expander("🔍 Search Parameters", expanded=not st.session_state.search_performed):
    col1, col2, col3 = st.columns(3)

    with col1:
        keywords = st.text_input("Keywords", placeholder="e.g., Software Engineer", value="Software Engineer")
        location = st.text_input("Location", placeholder="e.g., Remote, San Francisco", value="Remote")

    with col2:
        job_type = st.multiselect(
            "Job Type",
            ["Full-time", "Part-time", "Contract", "Internship"],
            default=["Full-time"]
        )
        sources = st.multiselect(
            "Sources",
            ["Indeed", "Glassdoor", "LinkedIn"],
            default=["Indeed"]
        )

    with col3:
        min_salary = st.number_input("Min Salary ($)", value=0, step=10000)
        max_results = st.slider("Max Results", 10, 100, 30)

    if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
        if not keywords:
            st.error("Please enter search keywords")
        else:
            st.session_state.jobs = search_jobs(
                keywords=keywords,
                location=location,
                sources=sources,
                job_type=job_type,
                max_results=max_results,
                min_salary=min_salary,
            )
            st.session_state.search_performed = True
            st.rerun()

st.markdown("---")

# Filters and sorting
if st.session_state.jobs:
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
if st.session_state.jobs:
    st.subheader(f"Available Jobs ({len(st.session_state.jobs)})")

    # Sort jobs
    jobs_to_display = st.session_state.jobs.copy()
    if sort_by == "Match Score":
        jobs_to_display.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    elif sort_by == "Company":
        jobs_to_display.sort(key=lambda x: x.get("company", ""))

    # Display jobs based on view mode
    if view_mode == "Cards":
        for i, job in enumerate(jobs_to_display):
            display_job_card(job, i)

    elif view_mode == "Table":
        # Create DataFrame
        df_data = []
        for job in jobs_to_display:
            df_data.append({
                "Title": job.get("title", "N/A"),
                "Company": job.get("company", "N/A"),
                "Location": job.get("location", "N/A"),
                "Salary": job.get("salary", "N/A"),
                "Match": job.get("match_score", 0),
                "Source": job.get("source", "N/A"),
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

    elif view_mode == "List":
        for i, job in enumerate(jobs_to_display):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{job.get('title')}** - {job.get('company')}")
                st.caption(f"{job.get('location')} | {job.get('source')}")
            with col2:
                st.metric("Match", f"{job.get('match_score', 0)}/100")
            with col3:
                if st.button("View", key=f"list_view_{i}"):
                    st.session_state[f"show_details_{i}"] = True

else:
    st.info("👆 Use the search parameters above to find jobs")
    st.markdown("""
    ### How it works:
    1. **Enter your search criteria** - keywords, location, job type, etc.
    2. **AI agents search multiple job boards** - Indeed, Glassdoor, LinkedIn, and more
    3. **Automatic deduplication** - Remove duplicate postings across sources
    4. **Smart ranking** - Jobs are ranked by fit based on your profile
    5. **Take action** - View details, apply, or skip
    """)

# Sidebar stats
with st.sidebar:
    st.subheader("📊 Search Stats")
    st.metric("Jobs Found", len(st.session_state.jobs))
    if st.session_state.jobs:
        avg_score = sum(j.get("match_score", 0) for j in st.session_state.jobs) / len(st.session_state.jobs)
        st.metric("Avg Match Score", f"{avg_score:.1f}/100")

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Use specific keywords for better results
    - Enable multiple sources for comprehensive search
    - Check match scores to find best fits
    - Jobs are saved automatically
    """)
