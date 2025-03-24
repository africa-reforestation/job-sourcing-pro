import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from src.database.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    try:
        # Load environment variables
        load_dotenv()
        database_url = os.getenv('DATABASE_URL')
        logger.info(f"Database URL: {database_url}")

        # Create engine
        engine = create_engine(database_url)
        logger.info("Created database engine")

        # Test connection
        with engine.connect() as connection:
            logger.info("Successfully connected to PostgreSQL database")
            
            # Create schema if it doesn't exist
            connection.execute(text('CREATE SCHEMA IF NOT EXISTS public'))
            connection.commit()
            logger.info("Ensured public schema exists")

            # Get inspector
            inspector = inspect(engine)
            
            # Log existing tables before creation
            existing_tables = inspector.get_table_names(schema='public')
            logger.info(f"Existing tables before creation: {existing_tables}")

            # Create all tables
            Base.metadata.create_all(engine)
            logger.info("Created all tables")

            # Log tables after creation
            tables_after = inspector.get_table_names(schema='public')
            logger.info(f"Tables after creation: {tables_after}")

            # Verify specific tables exist
            expected_tables = ['jobpost', 'filter_keyword']
            for table in expected_tables:
                if table in tables_after:
                    logger.info(f"Table '{table}' was created successfully")
                    # Log table columns
                    columns = inspector.get_columns(table, schema='public')
                    logger.info(f"Columns in {table}: {[col['name'] for col in columns]}")
                else:
                    logger.error(f"Table '{table}' was not created!")

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    create_tables() 