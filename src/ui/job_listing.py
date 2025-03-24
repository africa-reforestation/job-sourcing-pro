"""
UI components for displaying job listings in the web application.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
import re
from ..database.models import JobStatus, JobPriority

def display_job_listing(jobs: List[Dict[str, Any]], db_handler) -> None:
    """
    Display the job listings in the UI.
    
    Args:
        jobs: List of job data dictionaries.
        db_handler: Database handler instance.
    """
    if not jobs:
        st.info("No jobs found matching your criteria.")
        return
    
    # Display job count
    st.write(f"Found {len(jobs)} jobs")
    
    # Display each job in a card
    for job in jobs:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Job title with priority indicator
                priority_colors = {
                    "High": "🟢",
                    "Medium": "🟡",
                    "Low": "🔴"
                }
                priority_indicator = priority_colors.get(job.get("priority"), "⚪")
                st.markdown(f"### {priority_indicator} {job.get('title')}")
                
                # Job meta information
                meta_col1, meta_col2, meta_col3 = st.columns(3)
                with meta_col1:
                    st.caption(f"Posted: {job.get('date_time', 'Unknown')}")
                with meta_col2:
                    st.caption(f"Type: {job.get('job_type', 'Unknown')}")
                with meta_col3:
                    st.caption(f"Rate: {job.get('rate', 'Not specified')}")
                
                # Client information
                if job.get("client_information"):
                    st.markdown("#### Client Info")
                    st.caption(job.get("client_information"))
                
                # Job description (truncated)
                description = job.get("description", "")
                max_length = 300
                truncated = description[:max_length] + "..." if len(description) > max_length else description
                st.markdown("#### Description")
                st.write(truncated)
                
                # View full description expander
                with st.expander("View Full Description"):
                    st.write(description)
            
            with col2:
                # Display current status
                current_status = job.get("status", "New")
                st.write(f"Status: {current_status}")
                
                # Job actions
                status_options = [status.value for status in JobStatus]
                new_status = st.selectbox(
                    "Change Status",
                    status_options,
                    index=status_options.index(current_status) if current_status in status_options else 0,
                    key=f"status_{job.get('id')}"
                )
                
                # Priority selection
                current_priority = job.get("priority", "Medium")
                priority_options = [priority.value for priority in JobPriority]
                new_priority = st.selectbox(
                    "Priority",
                    priority_options,
                    index=priority_options.index(current_priority) if current_priority in priority_options else 1,
                    key=f"priority_{job.get('id')}"
                )
                
                # Update button
                if st.button("Update", key=f"update_{job.get('id')}"):
                    update_data = {}
                    
                    if new_status != current_status:
                        update_data["status"] = new_status
                    
                    if new_priority != current_priority:
                        update_data["priority"] = new_priority
                    
                    if update_data:
                        result = db_handler.update_job(job.get("id"), update_data)
                        if result["status"] == "success":
                            st.success("Job updated")
                            # Use rerun to refresh the page
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('message')}")
                
                # Upwork link if available
                if job.get("upwork_id"):
                    upwork_url = f"https://www.upwork.com/jobs/{job.get('upwork_id')}"
                    st.link_button("View on Upwork", upwork_url)

def display_job_statistics(db_handler) -> None:
    """
    Display job statistics in the UI.
    
    Args:
        db_handler: Database handler instance.
    """
    stats = db_handler.get_job_stats()
    
    # Create columns for different stat categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Jobs", stats["total_jobs"])
        st.caption("By Status")
        for status, count in stats["status_counts"].items():
            st.write(f"• {status}: {count}")
    
    with col2:
        st.caption("By Priority")
        for priority, count in stats["priority_counts"].items():
            st.write(f"• {priority}: {count}")
    
    with col3:
        st.caption("By Type")
        for job_type, count in stats["type_counts"].items():
            st.write(f"• {job_type}: {count}")
