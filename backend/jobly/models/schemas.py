"""Pydantic schemas for data validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    """User profile schema."""
    id: Optional[str] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    resume_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class JobPosting(BaseModel):
    """Job posting schema."""
    id: Optional[str] = None
    title: str
    company: str
    location: Optional[str] = None
    description: str
    requirements: List[str] = []
    url: Optional[str] = None
    source: Optional[str] = None
    posted_date: Optional[datetime] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Application(BaseModel):
    """Job application schema."""
    id: Optional[str] = None
    user_id: str
    job_id: str
    status: str
    applied_date: datetime = Field(default_factory=datetime.utcnow)
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Contact(BaseModel):
    """Contact schema for networking."""
    id: Optional[str] = None
    name: str
    email: Optional[EmailStr] = None
    linkedin_url: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    last_contacted: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
