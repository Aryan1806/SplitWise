"""
User Schemas
Pydantic models for User-related requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base User schema with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    Used in registration endpoint.
    
    Example:
        {
            "email": "john@example.com",
            "full_name": "John Doe",
            "password": "securepassword123"
        }
    """
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets minimum requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    
    All fields are optional.
    
    Example:
        {
            "full_name": "John Smith"
        }
    """
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """
    Schema for user response data.
    
    Returned by API endpoints.
    Never includes password!
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "full_name": "John Doe",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows creating from ORM models


class UserInDB(UserResponse):
    """
    Schema for user stored in database.
    
    Internal use only - includes hashed_password.
    """
    hashed_password: str