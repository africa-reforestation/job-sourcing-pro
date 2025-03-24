from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, JobPost, FilterKeyword, JobType, JobStatus, JobPriority
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Get database URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        logger.info(f"Using database URL: {db_url}")
        
        # Create engine and session
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create test keyword
        keyword = FilterKeyword(
            keyword="python",
            category="Programming",
            active=True
        )
        
        # Create test job
        job = JobPost(
            upwork_id="test123",
            title="Test Python Developer",
            description="This is a test job posting",
            job_type=JobType.HOURLY,
            experience_level="Intermediate",
            duration="1-3 months",
            rate="$30-50/hr",
            date_time="2025-03-24",
            proposal_count=0,
            payment_verified=True,
            country="Remote",
            skills="Python, Django, Flask",
            category="Web Development"
        )
        
        # Add to session
        session.add(keyword)
        session.add(job)
        
        # Commit changes
        session.commit()
        logger.info("Test entries created successfully!")
        
        # Verify entries
        keywords = session.query(FilterKeyword).all()
        jobs = session.query(JobPost).all()
        
        logger.info("\nKeywords in database:")
        for k in keywords:
            logger.info(k.to_dict())
            
        logger.info("\nJobs in database:")
        for j in jobs:
            logger.info(j.to_dict())
        
    except Exception as e:
        logger.error(f"Error testing database: {str(e)}")
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    test_database() 