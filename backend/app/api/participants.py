"""
Participant API Routes
Handles participant creation, management, and retrieval within groups.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Participant, Group
from app.schemas.participant import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user, verify_group_access, verify_participant_access
from app.utils.validators import validate_participant_limit
from app.utils.helpers import get_color_for_index

router = APIRouter(tags=["Participants"])


@router.get("/groups/{group_id}/participants", response_model=List[ParticipantResponse])
def list_participants(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    List all participants in a group.
    
    Example Request:
        GET /api/groups/123e4567.../participants
        Authorization: Bearer token...
    
    Example Response:
        [
            {
                "id": "789e4567...",
                "group_id": "123e4567...",
                "name": "Alice",
                "color": "#2DD4BF",
                "avatar_url": null,
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": "012e4567...",
                "group_id": "123e4567...",
                "name": "Bob",
                "color": "#FCD34D",
                "avatar_url": null,
                "created_at": "2024-01-15T10:35:00Z"
            }
        ]
    """
    return group.participants


@router.post(
    "/groups/{group_id}/participants",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED
)
def add_participant(
    group_id: UUID,
    participant_data: ParticipantCreate,
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Add a new participant to a group.
    
    Validation:
    - Maximum 4 participants per group
    - Participant name must be unique within group
    - Auto-assigns color if not provided
    
    Example Request:
        POST /api/groups/123e4567.../participants
        Authorization: Bearer token...
        {
            "name": "Charlie"
        }
    
    Example Response:
        {
            "id": "345e4567...",
            "group_id": "123e4567...",
            "name": "Charlie",
            "color": "#F43F5E",
            "avatar_url": null,
            "created_at": "2024-01-15T10:40:00Z"
        }
    """
    # Check participant limit
    current_count = db.query(Participant).filter(
        Participant.group_id == group_id
    ).count()
    
    try:
        validate_participant_limit(current_count, max_count=4)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Check for duplicate name in group
    existing_participant = db.query(Participant).filter(
        Participant.group_id == group_id,
        Participant.name == participant_data.name
    ).first()
    
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Participant with name '{participant_data.name}' already exists in this group"
        )
    
    # Auto-assign color if not provided
    color = participant_data.color
    if color is None:
        color = get_color_for_index(current_count)
    
    # Create participant
    new_participant = Participant(
        group_id=group_id,
        name=participant_data.name,
        color=color,
        avatar_url=participant_data.avatar_url
    )
    
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    
    return new_participant


@router.put("/participants/{participant_id}", response_model=ParticipantResponse)
def update_participant(
    participant_update: ParticipantUpdate,
    participant: Participant = Depends(verify_participant_access),
    db: Session = Depends(get_db)
):
    """
    Update a participant's information.
    
    Can update: name, color, avatar_url
    All fields are optional.
    
    Example Request:
        PUT /api/participants/789e4567...
        Authorization: Bearer token...
        {
            "name": "Alice Smith",
            "color": "#FF5733"
        }
    
    Example Response:
        {
            "id": "789e4567...",
            "group_id": "123e4567...",
            "name": "Alice Smith",
            "color": "#FF5733",
            "avatar_url": null,
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    # Update name if provided
    if participant_update.name is not None:
        # Check for duplicate name in group (excluding current participant)
        existing = db.query(Participant).filter(
            Participant.group_id == participant.group_id,
            Participant.name == participant_update.name,
            Participant.id != participant.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Participant with name '{participant_update.name}' already exists in this group"
            )
        
        participant.name = participant_update.name
    
    # Update color if provided
    if participant_update.color is not None:
        participant.color = participant_update.color
    
    # Update avatar_url if provided
    if participant_update.avatar_url is not None:
        participant.avatar_url = participant_update.avatar_url
    
    db.commit()
    db.refresh(participant)
    
    return participant


@router.delete("/participants/{participant_id}", response_model=MessageResponse)
def delete_participant(
    participant: Participant = Depends(verify_participant_access),
    db: Session = Depends(get_db)
):
    """
    Delete a participant from a group.
    
    ⚠️ WARNING: This will cascade delete:
    - All expenses where this participant was the payer
    - All expense splits involving this participant
    
    Example Request:
        DELETE /api/participants/789e4567...
        Authorization: Bearer token...
    
    Example Response:
        {
            "message": "Participant deleted successfully"
        }
    """
    # Check if participant has any expenses as payer
    expense_count = len(participant.expenses_paid)
    
    if expense_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete participant. They are the payer for {expense_count} expense(s). "
                   f"Please delete or reassign those expenses first."
        )
    
    db.delete(participant)
    db.commit()
    
    return {"message": "Participant deleted successfully"}