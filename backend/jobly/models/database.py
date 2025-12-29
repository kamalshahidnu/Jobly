"""Database models and ORM configuration."""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    location = Column(String)
    skills = Column(JSON)
    experience_years = Column(Integer)
    resume_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Job(Base):
    """Job database model."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    description = Column(Text)
    requirements = Column(JSON)
    url = Column(String)
    source = Column(String)
    posted_date = Column(DateTime)
    salary_range = Column(String)
    job_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApplicationModel(Base):
    """Application database model."""
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    job_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    applied_date = Column(DateTime, default=datetime.utcnow)
    resume_version = Column(String)
    cover_letter = Column(Text)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContactModel(Base):
    """Contact database model."""
    __tablename__ = "contacts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    linkedin_url = Column(String)
    company = Column(String)
    position = Column(String)
    notes = Column(Text)
    last_contacted = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database connection setup
def get_engine(database_url: str = "sqlite:///./jobly.db"):
    """Create database engine."""
    return create_engine(database_url, echo=False)


def get_session(engine):
    """Create database session."""
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine)
