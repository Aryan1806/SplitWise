"""
Auth Schemas
Pydantic models for authentication requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """
    Schema for login request.
    
    Example:
        {
            "email": "john@example.com",
            "password": "securepassword123"
        }
    """
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """
    Schema for token response after successful login.
    
    Example:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token request.
    
    Example:
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    """
    refresh_token: str


class TokenData(BaseModel):
    """
    Schema for decoded token data.
    
    Internal use for token validation.
    """
    user_id: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """
    Schema for password change request.
    
    Example:
        {
            "current_password": "oldpassword123",
            "new_password": "newpassword456"
        }
    """
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class MessageResponse(BaseModel):
    """
    Generic message response.
    
    Example:
        {
            "message": "Password changed successfully"
        }
    """
    message: str