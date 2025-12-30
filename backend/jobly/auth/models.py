"""Authentication models."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    """User registration model."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """User login model."""

    email: EmailStr
    password: str


class User(BaseModel):
    """User model."""

    user_id: str
    email: str
    name: str
    phone: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class UserResponse(BaseModel):
    """User response model (without sensitive data)."""

    user_id: str
    email: str
    name: str
    phone: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token data model."""

    user_id: Optional[str] = None
    email: Optional[str] = None
