"""
Participant Schemas
Pydantic models for Participant-related requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


class ParticipantBase(BaseModel):
    """Base Participant schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Participant name cannot be empty")
        return v.strip()


class ParticipantCreate(ParticipantBase):
    """
    Schema for creating a new participant.
    
    Color is optional - will be auto-assigned if not provided.
    
    Example:
        {
            "name": "Alice",
            "color": "#2DD4BF",
            "avatar_url": "https://example.com/avatar.jpg"
        }
    """
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    avatar_url: Optional[str] = Field(None, max_length=500)


class ParticipantUpdate(BaseModel):
    """
    Schema for updating a participant.
    
    All fields are optional.
    
    Example:
        {
            "name": "Alice Smith",
            "color": "#F43F5E"
        }
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    avatar_url: Optional[str] = Field(None, max_length=500)


class ParticipantResponse(ParticipantBase):
    """
    Schema for participant response data.
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "group_id": "456e4567-e89b-12d3-a456-426614174001",
            "name": "Alice",
            "color": "#2DD4BF",
            "avatar_url": null,
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    id: UUID
    group_id: UUID
    color: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ParticipantWithBalance(ParticipantResponse):
    """
    Participant response with balance information.
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Alice",
            "color": "#2DD4BF",
            "total_paid": "150.00",
            "total_share": "100.00",
            "net_balance": "50.00"
        }
    """
    total_paid: Decimal = Decimal("0.00")
    total_share: Decimal = Decimal("0.00")
    net_balance: Decimal = Decimal("0.00")