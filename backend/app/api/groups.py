"""
Group API Routes
Handles group creation, management, and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import User, Group, Participant, Expense
from app.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupDetailResponse,
    GroupSummaryResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user, verify_group_access

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("", response_model=List[GroupResponse])
def list_my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all groups owned by the current user.
    
    Includes summary statistics for each group:
    - Participant count
    - Total expenses
    - Total amount spent
    
    Example Request:
        GET /api/groups
        Authorization: Bearer token...
    
    Example Response:
        [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Weekend Trip",
                "owner_id": "456e4567...",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "participant_count": 4,
                "total_expenses": 10,
                "total_amount": "450.00"
            }
        ]
    """
    # Query groups with aggregated data
    groups = db.query(Group).filter(Group.owner_id == current_user.id).all()
    
    # Add statistics to each group
    result = []
    for group in groups:
        # Count participants
        participant_count = db.query(Participant).filter(
            Participant.group_id == group.id
        ).count()
        
        # Count expenses and sum amounts
        expense_stats = db.query(
            func.count(Expense.id).label("count"),
            func.coalesce(func.sum(Expense.amount), 0).label("total")
        ).filter(Expense.group_id == group.id).first()
        
        # Create response object
        group_data = GroupResponse(
            id=group.id,
            name=group.name,
            owner_id=group.owner_id,
            created_at=group.created_at,
            updated_at=group.updated_at,
            participant_count=participant_count,
            total_expenses=expense_stats.count,
            total_amount=str(expense_stats.total)
        )
        result.append(group_data)
    
    return result


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new group.
    
    The current user becomes the owner of the group.
    
    Example Request:
        POST /api/groups
        Authorization: Bearer token...
        {
            "name": "Weekend Trip"
        }
    
    Example Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Weekend Trip",
            "owner_id": "456e4567...",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "participant_count": 0,
            "total_expenses": 0,
            "total_amount": "0.00"
        }
    """
    # Create new group
    new_group = Group(
        name=group_data.name,
        owner_id=current_user.id
    )
    
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    # Return with initial statistics
    return GroupResponse(
        id=new_group.id,
        name=new_group.name,
        owner_id=new_group.owner_id,
        created_at=new_group.created_at,
        updated_at=new_group.updated_at,
        participant_count=0,
        total_expenses=0,
        total_amount="0.00"
    )


@router.get("/{group_id}", response_model=GroupDetailResponse)
def get_group(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific group.
    
    Includes:
    - Group details
    - List of all participants
    - Summary statistics
    
    Example Request:
        GET /api/groups/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer token...
    
    Example Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Weekend Trip",
            "owner_id": "456e4567...",
            "created_at": "2024-01-15T10:30:00Z",
            "participants": [
                {
                    "id": "789e4567...",
                    "name": "Alice",
                    "color": "#2DD4BF"
                }
            ],
            "participant_count": 4,
            "total_expenses": 10,
            "total_amount": "450.00"
        }
    """
    # Get statistics
    participant_count = len(group.participants)
    
    expense_stats = db.query(
        func.count(Expense.id).label("count"),
        func.coalesce(func.sum(Expense.amount), 0).label("total")
    ).filter(Expense.group_id == group.id).first()
    
    # Build response
    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        owner_id=group.owner_id,
        created_at=group.created_at,
        updated_at=group.updated_at,
        participant_count=participant_count,
        total_expenses=expense_stats.count,
        total_amount=str(expense_stats.total),
        participants=group.participants
    )


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_update: GroupUpdate,
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Update a group's information.
    
    Currently only the name can be updated.
    
    Example Request:
        PUT /api/groups/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer token...
        {
            "name": "Summer Vacation 2024"
        }
    
    Example Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Summer Vacation 2024",
            "owner_id": "456e4567...",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-16T14:20:00Z",
            "participant_count": 4,
            "total_expenses": 10,
            "total_amount": "450.00"
        }
    """
    # Update name if provided
    if group_update.name is not None:
        group.name = group_update.name
    
    db.commit()
    db.refresh(group)
    
    # Get statistics
    participant_count = db.query(Participant).filter(
        Participant.group_id == group.id
    ).count()
    
    expense_stats = db.query(
        func.count(Expense.id).label("count"),
        func.coalesce(func.sum(Expense.amount), 0).label("total")
    ).filter(Expense.group_id == group.id).first()
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        owner_id=group.owner_id,
        created_at=group.created_at,
        updated_at=group.updated_at,
        participant_count=participant_count,
        total_expenses=expense_stats.count,
        total_amount=str(expense_stats.total)
    )


@router.delete("/{group_id}", response_model=MessageResponse)
def delete_group(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Delete a group.
    
    ⚠️ WARNING: This will cascade delete:
    - All participants in the group
    - All expenses in the group
    - All expense splits
    
    Example Request:
        DELETE /api/groups/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer token...
    
    Example Response:
        {
            "message": "Group deleted successfully"
        }
    """
    db.delete(group)
    db.commit()
    
    return {"message": "Group deleted successfully"}


@router.get("/{group_id}/summary", response_model=GroupSummaryResponse)
def get_group_summary(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for a group.
    
    Example Request:
        GET /api/groups/123e4567-e89b-12d3-a456-426614174000/summary
        Authorization: Bearer token...
    
    Example Response:
        {
            "group_id": "123e4567-e89b-12d3-a456-426614174000",
            "total_spent": "450.00",
            "total_expenses": 10,
            "participant_count": 4,
            "settled": false
        }
    """
    # Count participants
    participant_count = db.query(Participant).filter(
        Participant.group_id == group.id
    ).count()
    
    # Get expense statistics
    expense_stats = db.query(
        func.count(Expense.id).label("count"),
        func.coalesce(func.sum(Expense.amount), 0).label("total")
    ).filter(Expense.group_id == group.id).first()
    
    # TODO: Calculate if group is settled (all balances = 0)
    # For now, assume not settled
    is_settled = False
    
    return GroupSummaryResponse(
        group_id=group.id,
        total_spent=str(expense_stats.total),
        total_expenses=expense_stats.count,
        participant_count=participant_count,
        settled=is_settled
    )