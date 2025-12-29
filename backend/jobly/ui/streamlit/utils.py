"""Utility functions for Streamlit UI."""

import streamlit as st
from typing import Any, Dict, List


def init_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        "user_id": "demo_user",
        "profile_loaded": False,
        "jobs": [],
        "applications": [],
        "contacts": [],
        "interviews": []
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def format_job_card(job: Dict[str, Any]) -> str:
    """Format job data as HTML card.

    Args:
        job: Job data dictionary

    Returns:
        HTML string for job card
    """
    return f"""
    <div style="border: 1px solid #ddd; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
        <h3>{job.get('title', 'Unknown')}</h3>
        <p><strong>{job.get('company', 'Unknown')}</strong></p>
        <p>📍 {job.get('location', 'Unknown')} | 💰 {job.get('salary', 'Not specified')}</p>
        <p>Match Score: {job.get('match_score', 0)}/100</p>
    </div>
    """


def display_metric_card(title: str, value: str, delta: str = None):
    """Display a metric card.

    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta value
    """
    st.metric(label=title, value=value, delta=delta)


def show_success(message: str):
    """Show success message.

    Args:
        message: Success message
    """
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error message.

    Args:
        message: Error message
    """
    st.error(f"❌ {message}")


def show_info(message: str):
    """Show info message.

    Args:
        message: Info message
    """
    st.info(f"ℹ️ {message}")


def confirm_action(message: str) -> bool:
    """Show confirmation dialog.

    Args:
        message: Confirmation message

    Returns:
        True if confirmed, False otherwise
    """
    return st.button(message)


def paginate_list(items: List[Any], items_per_page: int = 10) -> List[Any]:
    """Paginate a list of items.

    Args:
        items: List of items to paginate
        items_per_page: Number of items per page

    Returns:
        Current page items
    """
    if "page" not in st.session_state:
        st.session_state.page = 0

    total_pages = (len(items) - 1) // items_per_page + 1

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("← Previous") and st.session_state.page > 0:
            st.session_state.page -= 1

    with col2:
        st.write(f"Page {st.session_state.page + 1} of {total_pages}")

    with col3:
        if st.button("Next →") and st.session_state.page < total_pages - 1:
            st.session_state.page += 1

    start_idx = st.session_state.page * items_per_page
    end_idx = start_idx + items_per_page

    return items[start_idx:end_idx]


def format_date(dt) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime object

    Returns:
        Formatted date string
    """
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M")
