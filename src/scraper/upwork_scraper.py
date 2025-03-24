"""
Upwork job scraper using ScrapegraphAI.
"""
import os
import logging
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperGraph
from ..database.crud import DatabaseHandler
from ..utils.data_processor import process_job_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Pydantic models for job data validation
class JobLink(BaseModel):
    link: str = Field(description="The link to the job")

class UpworkJobs(BaseModel):
    jobs: List[JobLink] = Field(description="The list of scraped jobs")

class JobInformation(BaseModel):
    id: str = Field(description="The unique job title href link")
    title: str = Field(description="The title of the job")
    date_time: str = Field(description="The date and time the job was posted")
    description: str = Field(description="The full description of the job")
    job_type: str = Field(description="The type of the job (Fixed or Hourly)")
    experience_level: str = Field(description="The experience level of the job")
    duration: str = Field(description="The duration of the job")
    rate: Optional[str] = Field(description="The payment rate for the job")
    client_information: Optional[str] = Field(description="Client information including location, rating, etc.")

class Jobs(BaseModel):
    projects: List[JobInformation]

class UpworkScraper:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logging.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY not set in environment")
        self.api_key = api_key
    
    def get_scrape_config(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Generate scraper configuration based on keywords.
        """
        # Join keywords with OR for the search
        search_query = " OR ".join(keywords)
        
        return {
            "llm": {
                "provider": "groq",
                "api_key": self.api_key,
                "model": "llama3-70b-8192"
            },
            "system_message": """
            You are a web scraping assistant focused on extracting job listings from Upwork.
            Your task is to:
            1. Navigate to the Upwork search page
            2. Search for the requested keywords
            3. Extract all job listings from the search results
            4. For each job, visit its page and extract detailed information
            
            Be thorough and extract all available details for each job listing.
            """,
            "url": "https://www.upwork.com/nx/search/jobs",
            "input": {
                "search_query": search_query
            }
        }
    
    def scrape_job_listings(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape job listings from Upwork based on keywords.
        """
        try:
            logging.info(f"Starting job scraping with keywords: {keywords}")
            
            # Check if the environment is properly set up for scraping
            if not self.api_key or not self.api_key.strip():
                logging.error("No valid API key found for Groq")
                raise ValueError("Missing or invalid Groq API key. Please check your configuration.")
                
            # Get the scraper configuration
            config = self.get_scrape_config(keywords)
            
            logging.info("Attempting to initialize scraper with available configuration")
            
            try:
                # Set up essential parameters for the graph
                prompt = """
                Please scrape job listings from Upwork based on the given search query.
                For each job, extract the title, description, job type, experience level, duration, rate, and client information.
                """
                source = "https://www.upwork.com/nx/search/jobs"
                
                logging.info("Creating SmartScraperGraph with prompt, source, and config")
                
                # Create the graph with proper parameters
                graph = SmartScraperGraph(
                    prompt=prompt,
                    source=source,
                    config=config
                )
                
                logging.info("Graph configured successfully")
                
                # Execute the scraper graph
                logging.info("Executing scraper graph with Groq LLM...")
                result = graph.run(output_schema=Jobs)
                logging.info("Scraper graph execution completed successfully")
                
                # Process the scraped jobs
                scraped_jobs = []
                if hasattr(result, 'projects') and result.projects:
                    logging.info(f"Scraped {len(result.projects)} jobs")
                    for job in result.projects:
                        # Convert Pydantic model to dict and process
                        job_dict = job.dict()
                        processed_job = process_job_data(job_dict)
                        scraped_jobs.append(processed_job)
                    return scraped_jobs
                else:
                    logging.warning("No jobs found in scraper result")
                    return []
                
            except AttributeError as ae:
                logging.error(f"Attribute error in scraper: {str(ae)}")
                error_info = str(ae)
                
                if "'llm'" in error_info:
                    logging.error("This appears to be an issue with the LLM configuration")
                    logging.error("Please check your Groq API key and model configuration")
                    return []
                else:
                    logging.error(f"Unexpected attribute error: {error_info}")
                    return []
                    
            except Exception as e:
                logging.error(f"Unexpected error in scraper graph: {str(e)}")
                logging.error(f"Exception type: {type(e).__name__}")
                return []
                
        except Exception as e:
            logging.error(f"Critical error in job scraping: {str(e)}")
            logging.error(f"Exception type: {type(e).__name__}")
            return []
    
    def save_scraped_jobs(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Save scraped jobs to the database.
        """
        stats = {"total": len(jobs), "added": 0, "errors": 0, "duplicates": 0}
        
        for job in jobs:
            result = self.db_handler.create_job(job)
            
            if result["status"] == "success":
                stats["added"] += 1
            elif "already exists" in result.get("message", ""):
                stats["duplicates"] += 1
            else:
                stats["errors"] += 1
                logging.error(f"Error saving job: {result.get('message')}")
        
        return stats
    
    def run_job_scraping(self, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the complete job scraping process.
        """
        start_time = time.time()
        
        if not keywords:
            # If no keywords provided, fetch active keywords from the database
            keyword_records = self.db_handler.get_keywords(active_only=True)
            keywords = [record["keyword"] for record in keyword_records]
        
        if not keywords:
            logging.warning("No keywords available for scraping")
            return {
                "status": "error",
                "message": "No keywords available for scraping",
                "elapsed_time": 0,
                "stats": {"total": 0, "added": 0, "errors": 0, "duplicates": 0}
            }
        
        try:
            # Scrape jobs
            scraped_jobs = self.scrape_job_listings(keywords)
            
            # Save jobs to database
            stats = self.save_scraped_jobs(scraped_jobs)
            
            elapsed_time = time.time() - start_time
            
            return {
                "status": "success",
                "message": f"Scraped {stats['total']} jobs, added {stats['added']}, {stats['duplicates']} duplicates",
                "elapsed_time": elapsed_time,
                "stats": stats
            }
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            logging.error(f"Error in job scraping run: {str(e)}")
            
            return {
                "status": "error",
                "message": str(e),
                "elapsed_time": elapsed_time,
                "stats": {"total": 0, "added": 0, "errors": 0, "duplicates": 0}
            }
