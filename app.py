"""
Main application file for Upwork Job Sourcing & Filtering Web App.
"""
import os
import streamlit as st
import logging
from src.database.crud import DatabaseHandler
from src.ui.dashboard import render_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """
    Main application entry point.
    """
    try:
        # Initialize database handler
        db_handler = DatabaseHandler()
        
        # Render the dashboard
        render_dashboard(db_handler)
        
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        logging.error(f"Application error: {str(e)}")
        
        # Show error details in an expander for debugging
        with st.expander("Error Details"):
            st.exception(e)
        
        # Initialize default keywords if database is available but empty
        try:
            db_handler = DatabaseHandler()
            keywords = db_handler.get_keywords()
            
            if not keywords:
                default_keywords = [
                    "airtable", "zapier", "calendly", "crud", "automation",
                    "python", "streamlit", "django", "flask", "fastapi"
                ]
                
                st.info("Initializing default keywords...")
                
                for keyword in default_keywords:
                    db_handler.create_keyword({"keyword": keyword, "active": True})
                
                st.success("Default keywords initialized")
                st.button("Refresh Page", on_click=st.rerun)
        except Exception as init_error:
            st.error(f"Could not initialize default data: {str(init_error)}")

if __name__ == "__main__":
    main()
