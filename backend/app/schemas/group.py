"""
Group Schemas
Pydantic models for Group-related requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class GroupBase(BaseModel):
    """Base Group schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Group name cannot be empty")
        return v.strip()


class GroupCreate(GroupBase):
    """
    Schema for creating a new group.
    
    Example:
        {
            "name": "Weekend Trip"
        }
    """
    pass


class GroupUpdate(BaseModel):
    """
    Schema for updating a group.
    
    All fields are optional.
    
    Example:
        {
            "name": "Summer Vacation 2024"
        }
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class GroupResponse(GroupBase):
    """
    Schema for group response data.
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Weekend Trip",
            "owner_id": "456e4567-e89b-12d3-a456-426614174001",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "participant_count": 4,
            "total_expenses": 10,
            "total_amount": "450.00"
        }
    """
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    participant_count: Optional[int] = 0
    total_expenses: Optional[int] = 0
    total_amount: Optional[str] = "0.00"
    
    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    """
    Detailed group response including participants.
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Weekend Trip",
            "owner_id": "456e4567-e89b-12d3-a456-426614174001",
            "created_at": "2024-01-15T10:30:00Z",
            "participants": [
                {"id": "...", "name": "Alice", "color": "#2DD4BF"},
                {"id": "...", "name": "Bob", "color": "#FCD34D"}
            ]
        }
    """
    participants: List["ParticipantResponse"] = []


class GroupSummaryResponse(BaseModel):
    """
    Summary statistics for a group.
    
    Example:
        {
            "group_id": "123e4567-e89b-12d3-a456-426614174000",
            "total_spent": "450.00",
            "total_expenses": 10,
            "participant_count": 4,
            "settled": false
        }
    """
    group_id: UUID
    total_spent: str
    total_expenses: int
    participant_count: int
    settled: bool


# Forward reference for circular import
from app.schemas.participant import ParticipantResponse
GroupDetailResponse.model_rebuild()