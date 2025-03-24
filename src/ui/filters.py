"""
UI components for filtering jobs in the web application.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from ..database.models import JobType, JobStatus, JobPriority

def render_filter_sidebar(db_handler) -> Dict[str, Any]:
    """
    Render the filter sidebar and return the selected filters.
    
    Args:
        db_handler: Database handler instance.
        
    Returns:
        Dictionary containing the selected filters.
    """
    with st.sidebar:
        st.title("Job Filters")
        
        # Status filter
        status_options = ["All"] + [status.value for status in JobStatus]
        selected_status = st.selectbox("Status", status_options)
        
        # Priority filter
        priority_options = ["All"] + [priority.value for priority in JobPriority]
        selected_priority = st.selectbox("Priority", priority_options)
        
        # Job type filter
        job_type_options = ["All"] + [job_type.value for job_type in JobType]
        selected_job_type = st.selectbox("Job Type", job_type_options)
        
        # Keyword search
        keyword_search = st.text_input("Search Keywords")
        
        # Sorting options
        sort_options = {
            "Newest First": ("created_at", "desc"),
            "Oldest First": ("created_at", "asc"),
            "Budget: High to Low": ("rate", "desc"),
            "Budget: Low to High": ("rate", "asc"),
            "Title (A-Z)": ("title", "asc"),
            "Title (Z-A)": ("title", "desc")
        }
        selected_sort = st.selectbox("Sort By", list(sort_options.keys()))
        
        # Apply filters button
        apply_filters = st.button("Apply Filters")
        
        # Reset filters button
        reset_filters = st.button("Reset Filters")
        
        # Create and manage keywords section
        st.divider()
        st.subheader("Manage Filter Keywords")
        
        # Display existing keywords
        keywords = db_handler.get_keywords()
        
        if keywords:
            st.write("Active Keywords:")
            for keyword in keywords:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {keyword['keyword']}" + (" (inactive)" if not keyword['active'] else ""))
                with col2:
                    if st.button("🗑️", key=f"delete_{keyword['id']}"):
                        db_handler.delete_keyword(keyword['id'])
                        st.rerun()
        else:
            st.write("No keywords defined yet.")
        
        # Add new keyword
        new_keyword = st.text_input("Add keyword", key="new_keyword_input")
        if st.button("Add", key="add_keyword_button"):
            if new_keyword:
                db_handler.create_keyword({"keyword": new_keyword, "active": True})
                st.rerun()
            else:
                st.error("Please enter a keyword")
        
        # Run scraper button
        st.divider()
        if st.button("Run Job Scraper", type="primary"):
            from ..scraper.upwork_scraper import UpworkScraper
            with st.spinner("Scraping jobs..."):
                scraper = UpworkScraper()
                result = scraper.run_job_scraping()
                
                if result["status"] == "success":
                    st.success(f"Scraped {result['stats']['total']} jobs, added {result['stats']['added']} new jobs")
                else:
                    st.error(f"Error: {result['message']}")
                
                # Wait 3 seconds to show the message before rerunning
                import time
                time.sleep(3)
                st.rerun()
    
    # Process filter selections
    filters = {
        "status": None if selected_status == "All" else selected_status,
        "priority": None if selected_priority == "All" else selected_priority,
        "job_type": None if selected_job_type == "All" else selected_job_type,
        "keyword": keyword_search if keyword_search else None,
        "sort_by": sort_options[selected_sort][0],
        "sort_order": sort_options[selected_sort][1]
    }
    
    # Handle reset filters
    if reset_filters:
        # Use streamlit's rerun to reset to default values
        st.rerun()
    
    return filters
