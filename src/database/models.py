from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Enum as SQLAlchemyEnum, MetaData
from sqlalchemy.ext.declarative import declarative_base
import datetime

# Create metadata with explicit schema
metadata = MetaData(schema='public')
Base = declarative_base(metadata=metadata)

class JobType(str, Enum):
    FIXED = "Fixed"
    HOURLY = "Hourly"

class JobStatus(str, Enum):
    NEW = "New"
    INTERESTED = "Interested"
    NOT_INTERESTED = "Not Interested"
    APPLIED = "Applied"

class JobPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class JobPost(Base):
    __tablename__ = 'jobpost'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    upwork_id = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    job_type = Column(SQLAlchemyEnum(JobType), nullable=False)
    experience_level = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    rate = Column(String, nullable=True)
    date_time = Column(String, nullable=False)
    proposal_count = Column(Integer, default=0)
    payment_verified = Column(Boolean, default=False)
    country = Column(String, nullable=True)
    ratings = Column(Float, nullable=True)
    spent = Column(Float, nullable=True)
    skills = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    client_information = Column(Text, nullable=True)
    status = Column(SQLAlchemyEnum(JobStatus), default=JobStatus.NEW)
    priority = Column(SQLAlchemyEnum(JobPriority), default=JobPriority.MEDIUM)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "upwork_id": self.upwork_id,
            "title": self.title,
            "description": self.description,
            "job_type": self.job_type.value if self.job_type else None,
            "experience_level": self.experience_level,
            "duration": self.duration,
            "rate": self.rate,
            "date_time": self.date_time,
            "proposal_count": self.proposal_count,
            "payment_verified": self.payment_verified,
            "country": self.country,
            "ratings": self.ratings,
            "spent": self.spent,
            "skills": self.skills,
            "category": self.category,
            "client_information": self.client_information,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class FilterKeyword(Base):
    __tablename__ = 'filter_keyword'
    __table_args__ = {'schema': 'public'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "keyword": self.keyword,
            "category": self.category,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
