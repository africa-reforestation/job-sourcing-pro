"""
Dashboard UI components for the Upwork Job Sourcing & Filtering Web App.
"""
import streamlit as st
from typing import Dict, Any
from .filters import render_filter_sidebar
from .job_listing import display_job_listing, display_job_statistics

def render_dashboard(db_handler) -> None:
    """
    Render the main dashboard UI.
    
    Args:
        db_handler: Database handler instance.
    """
    # Set page configuration
    st.set_page_config(
        page_title="Upwork Job Sourcing & Filtering",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Display header
    st.title("🔍 Upwork Job Sourcing & Filtering")
    st.markdown(
        """
        Find high-value Upwork jobs that match your skills and preferences.
        Use the filters in the sidebar to narrow down your search.
        """
    )
    
    # Render sidebar filters and get selected filters
    filters = render_filter_sidebar(db_handler)
    
    # Display job statistics
    with st.container(border=True):
        st.subheader("Job Dashboard")
        display_job_statistics(db_handler)
    
    # Add some spacing
    st.markdown("---")
    
    # Display jobs based on filters
    st.subheader("Available Jobs")
    
    # Fetch jobs based on filters
    jobs = db_handler.get_jobs(
        status=filters.get("status"),
        priority=filters.get("priority"),
        job_type=filters.get("job_type"),
        keyword=filters.get("keyword"),
        sort_by=filters.get("sort_by", "created_at"),
        sort_order=filters.get("sort_order", "desc")
    )
    
    # Display job listings
    display_job_listing(jobs, db_handler)
