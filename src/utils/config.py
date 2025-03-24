"""
Configuration utilities for the Upwork Job Sourcing & Filtering Web App.
"""
import os
import json
from typing import Dict, Any, List

# Default application settings
DEFAULT_CONFIG = {
    "job_fetch_interval_minutes": 15,
    "max_jobs_per_fetch": 50,
    "default_keywords": ["airtable", "zapier", "calendly", "crud", "automation"],
    "default_categories": ["crud operation", "ai jobs", "automation"],
    "job_staleness_days": 7,
    "min_client_budget": 100,
    "min_client_spent": 1000,
    "min_client_rating": 4.0,
    "crud_indicator_keywords": ["crud", "create", "read", "update", "delete", "database", 
                                "simple app", "basic application", "data entry", "form"],
    "low_complexity_keywords": ["simple", "basic", "straightforward", "easy", "quick",
                                "beginner", "entry-level", "standard"],
    "notification_enabled": True
}

def get_config(key: str = None) -> Any:
    """
    Get configuration value(s).
    
    Args:
        key: Specific configuration key to retrieve.
        
    Returns:
        Configuration value or entire configuration dictionary.
    """
    if key:
        return DEFAULT_CONFIG.get(key)
    return DEFAULT_CONFIG

def is_crud_job(job_description: str) -> bool:
    """
    Determine if a job description indicates a CRUD-type application.
    
    Args:
        job_description: The job description text.
        
    Returns:
        Boolean indicating if the job appears to be a CRUD application.
    """
    crud_keywords = get_config("crud_indicator_keywords")
    low_complexity = get_config("low_complexity_keywords")
    
    # Count occurrences of CRUD keywords
    crud_count = sum(1 for keyword in crud_keywords if keyword.lower() in job_description.lower())
    
    # Count occurrences of low complexity keywords
    complexity_count = sum(1 for keyword in low_complexity if keyword.lower() in job_description.lower())
    
    # Job is likely a CRUD app if it has multiple CRUD keywords and complexity indicators
    return crud_count >= 2 and complexity_count >= 1

def get_client_quality_score(spent: float, rating: float) -> float:
    """
    Calculate a client quality score based on spent amount and rating.
    
    Args:
        spent: Amount the client has spent on Upwork.
        rating: Client rating (1-5 scale).
        
    Returns:
        Client quality score (0-100).
    """
    min_spent = get_config("min_client_spent")
    min_rating = get_config("min_client_rating")
    
    # Normalize spent to a 0-50 score
    spent_score = min(50, (spent / min_spent) * 25)
    
    # Normalize rating to a 0-50 score
    rating_score = min(50, (rating / 5) * 50)
    
    return spent_score + rating_score

def extract_budget_from_rate(rate_str: str) -> float:
    """
    Extract the budget amount from a rate string.
    
    Args:
        rate_str: Rate string (e.g., "$15-$25/hr", "$500")
        
    Returns:
        Extracted budget as a float, or 0 if not extractable.
    """
    if not rate_str:
        return 0.0
    
    # Remove currency symbols and other non-numeric characters
    rate_str = rate_str.replace('$', '').replace(',', '')
    
    # Extract numbers from the string
    import re
    numbers = re.findall(r'\d+(?:\.\d+)?', rate_str)
    
    if not numbers:
        return 0.0
    
    # For a range, use the lower value
    return float(numbers[0])
