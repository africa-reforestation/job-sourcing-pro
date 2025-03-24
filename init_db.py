from src.database.models import Base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        load_dotenv()
        logger.info("Loaded environment variables")
        
        # Get database connection details from environment variables
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        logger.info(f"Using database URL: {db_url}")
        
        # Create database engine
        engine = create_engine(db_url, echo=True)
        logger.info("Created database engine")
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Created all database tables")
        
        print("Database tables created successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 