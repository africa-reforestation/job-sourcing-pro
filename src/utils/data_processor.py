"""
Data processing utilities for the Upwork Job Sourcing & Filtering Web App.
"""
import re
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from .config import is_crud_job, get_client_quality_score, extract_budget_from_rate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_upwork_id(href: str) -> Optional[str]:
    """
    Extract Upwork job ID from a job URL.
    
    Args:
        href: The URL or identifier string.
        
    Returns:
        Extracted job ID or None if not found.
    """
    if not href:
        return None
        
    pattern = r'_~(\w+)'
    match = re.search(pattern, href)
    
    if match:
        return match.group(1)
    
    # Fallback to extracting the last path component
    parts = href.strip('/').split('/')
    if parts:
        return parts[-1]
    
    return None

def extract_client_info(client_info: str) -> Dict[str, Any]:
    """
    Extract structured client information from client info string.
    
    Args:
        client_info: Client information string.
        
    Returns:
        Dictionary with extracted client details.
    """
    info = {
        "country": None,
        "reviews": None,
        "rating": None,
        "spent": 0.0,
        "hire_rate": None
    }
    
    if not client_info:
        return info
    
    # Extract country
    country_match = re.search(r'(?:^|\s)([A-Za-z]+(?:\s[A-Za-z]+)*)(?=\s|$)', client_info)
    if country_match:
        info["country"] = country_match.group(1).strip()
    
    # Extract rating
    rating_match = re.search(r'(\d+(?:\.\d+)?)/5', client_info)
    if rating_match:
        info["rating"] = float(rating_match.group(1))
    
    # Extract spent amount
    spent_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)\+?\s(?:spent|paid)', client_info, re.IGNORECASE)
    if spent_match:
        spent_str = spent_match.group(1).replace(',', '')
        info["spent"] = float(spent_str)
    
    # Extract hire rate
    hire_match = re.search(r'(\d+)%\s+hire\s+rate', client_info, re.IGNORECASE)
    if hire_match:
        info["hire_rate"] = int(hire_match.group(1))
    
    return info

def normalize_job_type(job_type: str) -> str:
    """
    Normalize job type string to standard format.
    
    Args:
        job_type: Raw job type string.
        
    Returns:
        Normalized job type: "Fixed" or "Hourly".
    """
    if not job_type:
        return "Fixed"  # Default to Fixed
    
    job_type_lower = job_type.lower()
    
    if "hourly" in job_type_lower:
        return "Hourly"
    elif "fixed" in job_type_lower:
        return "Fixed"
    else:
        return "Fixed"  # Default

def process_job_data(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and normalize raw job data.
    
    Args:
        job: Raw job dictionary.
        
    Returns:
        Processed job dictionary.
    """
    try:
        # Extract upwork_id from id field
        upwork_id = extract_upwork_id(job.get("id"))
        if not upwork_id:
            upwork_id = f"fallback-{random.randint(10000, 99999)}"
        
        # Extract client information
        client_info = extract_client_info(job.get("client_information", ""))
        
        # Determine job priority based on CRUD assessment and client quality
        is_crud = is_crud_job(job.get("description", ""))
        client_score = get_client_quality_score(
            client_info.get("spent", 0), 
            client_info.get("rating", 0)
        )
        
        priority = "Medium"
        if is_crud and client_score >= 60:
            priority = "High"
        elif client_score <= 30:
            priority = "Low"
        
        # Process budget
        budget = extract_budget_from_rate(job.get("rate", ""))
        
        # Normalize job type
        job_type = normalize_job_type(job.get("job_type", ""))
        
        # Construct processed job data
        processed_job = {
            "upwork_id": upwork_id,
            "title": job.get("title", ""),
            "description": job.get("description", ""),
            "job_type": job_type,
            "experience_level": job.get("experience_level", ""),
            "duration": job.get("duration", ""),
            "rate": job.get("rate", ""),
            "date_time": job.get("date_time", ""),
            "country": client_info.get("country"),
            "ratings": client_info.get("rating"),
            "spent": client_info.get("spent"),
            "client_information": job.get("client_information", ""),
            "priority": priority,
            "status": "New"
        }
        
        return processed_job
    
    except Exception as e:
        logging.error(f"Error processing job data: {str(e)}")
        # Return a minimal valid job record
        return {
            "upwork_id": f"error-{random.randint(10000, 99999)}",
            "title": job.get("title", "Error processing job"),
            "description": job.get("description", "Error occurred during processing"),
            "job_type": "Fixed",
            "experience_level": job.get("experience_level", ""),
            "duration": job.get("duration", ""),
            "rate": job.get("rate", ""),
            "date_time": job.get("date_time", datetime.now().isoformat()),
            "status": "New",
            "priority": "Low"
        }

def get_filter_score(job_data: Dict[str, Any], keywords: List[str]) -> int:
    """
    Calculate a filter score for a job based on keywords.
    
    Args:
        job_data: Processed job dictionary.
        keywords: List of keywords to look for.
        
    Returns:
        Score representing keyword match count.
    """
    if not job_data or not keywords:
        return 0
    
    # Combine relevant text fields for searching
    search_text = " ".join([
        job_data.get("title", ""),
        job_data.get("description", ""),
        job_data.get("skills", "")
    ]).lower()
    
    # Count occurrences of each keyword
    score = sum(1 for keyword in keywords if keyword.lower() in search_text)
    
    return score
