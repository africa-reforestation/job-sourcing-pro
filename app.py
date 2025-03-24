"""
Main application file for Upwork Job Sourcing & Filtering Web App.
"""
import os
import streamlit as st
import logging
from dotenv import load_dotenv
from src.database.crud import DatabaseHandler
from src.ui.dashboard import render_dashboard
from src.scraper.upwork_scraper import UpworkScraper
from src.scheduler.job_scheduler import create_job_scraping_task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug: Print environment variables
logger.info("Environment variables:")
logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
logger.info(f"PGUSER: {os.getenv('PGUSER')}")
logger.info(f"PGHOST: {os.getenv('PGHOST')}")
logger.info(f"PGPORT: {os.getenv('PGPORT')}")
logger.info(f"PGDATABASE: {os.getenv('PGDATABASE')}")

# Set page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Upwork Job Sourcing & Filtering",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variable to hold the scheduler task instance
job_scraper_task = None

def initialize_job_scraper():
    """
    Initialize the job scraper scheduler.
    """
    global job_scraper_task
    
    try:
        # If task is already running, return its status
        if job_scraper_task is not None and job_scraper_task.running:
            return {
                "status": "success", 
                "message": "Job scraper already running", 
                "task": job_scraper_task.get_status()
            }
        
        # Initialize the scraper
        scraper = UpworkScraper()
        
        # Create and start the periodic task (run every 60 minutes)
        job_scraper_task = create_job_scraping_task(
            scraper_func=scraper.run_job_scraping,
            interval_minutes=60,  # Run every hour
            run_on_start=True     # Run immediately when started
        )
        
        # Start the task
        job_scraper_task.start()
        
        return {
            "status": "success",
            "message": "Job scraper started successfully",
            "task": job_scraper_task.get_status()
        }
        
    except Exception as e:
        logging.error(f"Failed to initialize job scraper: {str(e)}")
        return {"status": "error", "message": str(e)}

def main():
    """
    Main application entry point.
    """
    try:
        # Start the job scraper scheduler
        scraper_status = initialize_job_scraper()
        if scraper_status.get("status") == "error":
            st.sidebar.error(f"Job scraper initialization failed: {scraper_status.get('message', 'Unknown error')}")
        else:
            # Using more explicit approach to avoid typing issues
            task_info = {}
            if "task" in scraper_status and isinstance(scraper_status["task"], dict):
                task_info = scraper_status["task"]
            
            next_run = "Unknown"
            if "next_run" in task_info:
                next_run = task_info["next_run"]
                
            st.sidebar.success(f"Job scraper active. Next run: {next_run}")
        
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
