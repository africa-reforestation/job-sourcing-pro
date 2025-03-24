"""
Job scheduler module for running periodic job scraping.
"""
import threading
import time
import logging
import datetime
from typing import Optional, Callable, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PeriodicTask:
    """
    A class to run a task at periodic intervals.
    """
    def __init__(self, 
                 interval_seconds: int, 
                 task_function: Callable, 
                 task_name: str = "Periodic Task", 
                 run_on_start: bool = True,
                 **task_kwargs):
        """
        Initialize the periodic task.
        
        Args:
            interval_seconds: Time interval in seconds between task executions
            task_function: Function to execute
            task_name: Name of the task for logging
            run_on_start: Whether to run the task immediately on start
            task_kwargs: Keyword arguments to pass to the task function
        """
        self.interval = interval_seconds
        self.task_function = task_function
        self.task_name = task_name
        self.task_kwargs = task_kwargs
        self.run_on_start = run_on_start
        self.running = False
        self.thread = None
        self.last_run: Optional[datetime.datetime] = None
        self.next_run: Optional[datetime.datetime] = None
        
    def _task_wrapper(self):
        """
        Wrapper to execute the task function periodically.
        """
        if self.run_on_start:
            self._execute_task()
            
        while self.running:
            time.sleep(1)  # Check every second to avoid CPU hogging
            
            # Calculate time until next run
            if self.next_run and datetime.datetime.now() >= self.next_run:
                self._execute_task()
    
    def _execute_task(self):
        """
        Execute the task function and handle exceptions.
        """
        try:
            self.last_run = datetime.datetime.now()
            logging.info(f"Running periodic task: {self.task_name}")
            
            result = self.task_function(**self.task_kwargs)
            
            if isinstance(result, dict) and result.get("status") == "error":
                logging.error(f"Task {self.task_name} failed: {result.get('message')}")
            else:
                logging.info(f"Task {self.task_name} completed successfully")
                
            # Set next run time
            self.next_run = datetime.datetime.now() + datetime.timedelta(seconds=self.interval)
            logging.info(f"Next run of {self.task_name} scheduled for: {self.next_run}")
            
        except Exception as e:
            logging.error(f"Error executing task {self.task_name}: {str(e)}")
            # Set next run time even if there was an error
            self.next_run = datetime.datetime.now() + datetime.timedelta(seconds=self.interval)
    
    def start(self):
        """
        Start the periodic task.
        """
        if not self.running:
            logging.info(f"Starting periodic task: {self.task_name}")
            self.running = True
            self.next_run = datetime.datetime.now()
            self.thread = threading.Thread(target=self._task_wrapper, daemon=True)
            self.thread.start()
            return True
        return False
    
    def stop(self):
        """
        Stop the periodic task.
        """
        if self.running:
            logging.info(f"Stopping periodic task: {self.task_name}")
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            self.thread = None
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the periodic task.
        
        Returns:
            Dictionary with task status details
        """
        return {
            "task_name": self.task_name,
            "running": self.running,
            "interval_seconds": self.interval,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "time_until_next_run": (self.next_run - datetime.datetime.now()).total_seconds() if self.next_run else None
        }

def create_job_scraping_task(scraper_func, interval_minutes: int = 60, run_on_start: bool = True) -> PeriodicTask:
    """
    Create a periodic task for job scraping.
    
    Args:
        scraper_func: Function to run the job scraper
        interval_minutes: Interval in minutes between scraping runs
        run_on_start: Whether to run the scraper immediately on start
        
    Returns:
        PeriodicTask instance
    """
    interval_seconds = interval_minutes * 60
    return PeriodicTask(
        interval_seconds=interval_seconds,
        task_function=scraper_func,
        task_name="Job Scraping",
        run_on_start=run_on_start
    )