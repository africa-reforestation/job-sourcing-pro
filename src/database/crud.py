import logging
import os
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import create_engine, func, desc, asc, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, JobPost, FilterKeyword, JobStatus, JobPriority, JobType
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get database connection details from environment variables
        db_user = os.getenv('PGUSER')
        db_password = os.getenv('PGPASSWORD')
        db_host = os.getenv('PGHOST')
        db_port = os.getenv('PGPORT', '5432')
        db_name = os.getenv('PGDATABASE')
        
        # Log connection details (without password)
        logger.info(f"Database connection details:")
        logger.info(f"User: {db_user}")
        logger.info(f"Host: {db_host}")
        logger.info(f"Port: {db_port}")
        logger.info(f"Database: {db_name}")
        
        # Construct database URL with schema
        db_url = os.getenv('DATABASE_URL')
        if not db_url and all([db_user, db_password, db_host, db_port, db_name]):
            db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?options=-csearch_path%3Dpublic"
            logger.info("Constructed database URL from individual parameters")
        
        if not db_url:
            error_msg = "Database connection information missing. Please provide DATABASE_URL or individual connection parameters."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            logger.info("Attempting to create database engine...")
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test the connection with a simple query
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1")).scalar()
                logger.info("Database connection test successful")
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created/verified")
            
        except SQLAlchemyError as e:
            error_msg = f"Failed to initialize database connection: {str(e)}"
            logger.error(error_msg)
            raise SQLAlchemyError(error_msg)

    def get_session(self):
        return self.Session()

    # Job Post operations
    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job entry."""
        session = None
        try:
            session = self.Session()
            
            # Check if job already exists
            existing_job = session.query(JobPost).filter_by(upwork_id=job_data.get('upwork_id')).first()
            if existing_job:
                return {"status": "error", "message": "Job already exists", "job_id": existing_job.id}
            
            new_job = JobPost(**job_data)
            session.add(new_job)
            session.commit()
            return {"status": "success", "job_id": new_job.id}
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Database error creating job: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if session:
                session.close()

    def get_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a job by ID."""
        session = None
        try:
            session = self.Session()
            job = session.query(JobPost).filter_by(id=job_id).first()
            if not job:
                return None
            return job.to_dict()
        except SQLAlchemyError as e:
            logging.error(f"Database error retrieving job: {str(e)}")
            return None
        finally:
            if session:
                session.close()

    def update_job(self, job_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing job."""
        session = None
        try:
            session = self.Session()
            job = session.query(JobPost).filter_by(id=job_id).first()
            if not job:
                return {"status": "error", "message": "Job not found"}
            
            for key, value in update_data.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            session.commit()
            return {"status": "success", "message": "Job updated successfully"}
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Database error updating job: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if session:
                session.close()

    def delete_job(self, job_id: int) -> Dict[str, Any]:
        """Delete a job by ID."""
        session = None
        try:
            session = self.Session()
            job = session.query(JobPost).filter_by(id=job_id).first()
            if not job:
                return {"status": "error", "message": "Job not found"}
            
            session.delete(job)
            session.commit()
            return {"status": "success", "message": "Job deleted successfully"}
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Database error deleting job: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if session:
                session.close()

    def get_jobs(self, 
                 status: Optional[Union[JobStatus, str]] = None,
                 priority: Optional[Union[JobPriority, str]] = None,
                 job_type: Optional[Union[JobType, str]] = None,
                 keyword: Optional[str] = None,
                 sort_by: str = "created_at",
                 sort_order: str = "desc",
                 limit: int = 100,
                 offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get jobs with filters and pagination.
        """
        session = None
        try:
            session = self.Session()
            query = session.query(JobPost)
            
            if status:
                if isinstance(status, str):
                    status = JobStatus(status)
                query = query.filter(JobPost.status == status)
            
            if priority:
                if isinstance(priority, str):
                    priority = JobPriority(priority)
                query = query.filter(JobPost.priority == priority)
            
            if job_type:
                if isinstance(job_type, str):
                    job_type = JobType(job_type)
                query = query.filter(JobPost.job_type == job_type)
            
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.filter(
                    (JobPost.title.ilike(search_pattern)) | 
                    (JobPost.description.ilike(search_pattern)) |
                    (JobPost.skills.ilike(search_pattern))
                )
            
            # Apply sorting
            if sort_order.lower() == "asc":
                query = query.order_by(asc(getattr(JobPost, sort_by)))
            else:
                query = query.order_by(desc(getattr(JobPost, sort_by)))
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Get jobs
            jobs = query.all()
            return [job.to_dict() for job in jobs]
        
        except SQLAlchemyError as e:
            logging.error(f"Database error fetching jobs: {str(e)}")
            return []
        finally:
            if session:
                session.close()

    # Filter Keywords operations
    def create_keyword(self, keyword_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new filter keyword."""
        session = None
        try:
            session = self.Session()
            
            # Check if keyword already exists
            existing_keyword = session.query(FilterKeyword).filter_by(keyword=keyword_data.get('keyword')).first()
            if existing_keyword:
                return {"status": "error", "message": "Keyword already exists", "keyword_id": existing_keyword.id}
            
            new_keyword = FilterKeyword(**keyword_data)
            session.add(new_keyword)
            session.commit()
            return {"status": "success", "keyword_id": new_keyword.id}
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Database error creating keyword: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if session:
                session.close()

    def get_keywords(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get all filter keywords."""
        session = None
        try:
            session = self.Session()
            query = session.query(FilterKeyword)
            
            if active_only:
                query = query.filter_by(active=True)
            
            keywords = query.all()
            return [keyword.to_dict() for keyword in keywords]
        except SQLAlchemyError as e:
            logging.error(f"Database error fetching keywords: {str(e)}")
            return []
        finally:
            if session:
                session.close()

    def update_keyword(self, keyword_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing keyword."""
        session = None
        try:
            session = self.Session()
            keyword = session.query(FilterKeyword).filter_by(id=keyword_id).first()
            if not keyword:
                return {"status": "error", "message": "Keyword not found"}
            
            for key, value in update_data.items():
                if hasattr(keyword, key):
                    setattr(keyword, key, value)
            
            session.commit()
            return {"status": "success", "message": "Keyword updated successfully"}
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Database error updating keyword: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if session:
                session.close()

    def delete_keyword(self, keyword_id: int) -> Dict[str, Any]:
        """Delete a keyword by ID."""
        session = None
        try:
            session = self.Session()
            keyword = session.query(FilterKeyword).filter_by(id=keyword_id).first()
            if not keyword:
                return {"status": "error", "message": "Keyword not found"}
            
            session.delete(keyword)
            session.commit()
            return {"status": "success", "message": "Keyword deleted successfully"}
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Database error deleting keyword: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if session:
                session.close()

    def get_job_stats(self) -> Dict[str, Any]:
        """Get job statistics."""
        session = None
        try:
            session = self.Session()
            
            # Total job count
            total_jobs = session.query(func.count(JobPost.id)).scalar()
            
            # Jobs by status
            status_counts = {}
            for status in JobStatus:
                count = session.query(func.count(JobPost.id)).filter(JobPost.status == status).scalar()
                status_counts[status.value] = count
            
            # Jobs by priority
            priority_counts = {}
            for priority in JobPriority:
                count = session.query(func.count(JobPost.id)).filter(JobPost.priority == priority).scalar()
                priority_counts[priority.value] = count
            
            # Jobs by type
            type_counts = {}
            for job_type in JobType:
                count = session.query(func.count(JobPost.id)).filter(JobPost.job_type == job_type).scalar()
                type_counts[job_type.value] = count
            
            return {
                "total_jobs": total_jobs,
                "status_counts": status_counts,
                "priority_counts": priority_counts,
                "type_counts": type_counts
            }
        except SQLAlchemyError as e:
            logging.error(f"Database error retrieving job stats: {str(e)}")
            return {
                "total_jobs": 0,
                "status_counts": {},
                "priority_counts": {},
                "type_counts": {}
            }
        finally:
            if session:
                session.close()
