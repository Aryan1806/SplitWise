"""
Expense API Routes
Handles expense creation, management, and retrieval with split calculations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

from app.database import get_db
from app.models import Expense, ExpenseSplit, Participant, Group
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseDetailResponse,
    ExpenseListResponse,
    ExpenseSplitResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user, verify_group_access, get_pagination_params
from app.utils.validators import validate_splits_equal_total
from app.utils.helpers import split_amount_equally
from app.models.expense import SplitMode

router = APIRouter(tags=["Expenses"])


def validate_and_create_splits(
    expense: Expense,
    splits_data: List,
    db: Session
):
    """
    Helper function to validate and create expense splits.
    
    Validates:
    - All participant IDs exist and belong to the group
    - Split amounts sum to total expense amount
    - Percentages sum to 100 (if percentage mode)
    
    Args:
        expense: The expense object
        splits_data: List of split data from request
        db: Database session
    
    Raises:
        HTTPException: If validation fails
    """
    # Get all valid participant IDs for this group
    valid_participant_ids = set(
        p.id for p in db.query(Participant).filter(
            Participant.group_id == expense.group_id
        ).all()
    )
    
    # Validate all participants exist
    split_participant_ids = [s.participant_id for s in splits_data]
    for pid in split_participant_ids:
        if pid not in valid_participant_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Participant {pid} not found in this group"
            )
    
    # Validate splits based on mode
    if expense.split_mode == SplitMode.EQUAL:
        # For equal splits, auto-calculate amounts
        num_participants = len(splits_data)
        equal_splits = split_amount_equally(expense.amount, num_participants)
        
        # Create splits with calculated amounts
        for i, split_data in enumerate(splits_data):
            expense_split = ExpenseSplit(
                expense_id=expense.id,
                participant_id=split_data.participant_id,
                amount=equal_splits[i],
                percentage=None
            )
            db.add(expense_split)
    
    elif expense.split_mode == SplitMode.CUSTOM_AMOUNT:
        # Validate amounts sum to total
        split_amounts = [split_data.amount for split_data in splits_data]
        try:
            validate_splits_equal_total(split_amounts, expense.amount)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Create splits with provided amounts
        for split_data in splits_data:
            expense_split = ExpenseSplit(
                expense_id=expense.id,
                participant_id=split_data.participant_id,
                amount=split_data.amount,
                percentage=None
            )
            db.add(expense_split)
    
    elif expense.split_mode == SplitMode.PERCENTAGE:
        # Validate percentages sum to 100
        percentages = [split_data.percentage for split_data in splits_data]
        total_percentage = sum(percentages)
        
        if abs(total_percentage - Decimal("100")) > Decimal("0.01"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Percentages must sum to 100, got {total_percentage}"
            )
        
        # Calculate amounts from percentages
        for split_data in splits_data:
            amount = (expense.amount * split_data.percentage) / 100
            # Round to 2 decimal places
            amount = amount.quantize(Decimal('0.01'))
            
            expense_split = ExpenseSplit(
                expense_id=expense.id,
                participant_id=split_data.participant_id,
                amount=amount,
                percentage=split_data.percentage
            )
            db.add(expense_split)


@router.get("/groups/{group_id}/expenses", response_model=ExpenseListResponse)
def list_expenses(
    group: Group = Depends(verify_group_access),
    pagination: dict = Depends(get_pagination_params),
    category: Optional[str] = Query(None),
    participant_id: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List expenses for a group with filtering and pagination.
    
    Filters:
    - category: Filter by category
    - participant_id: Filter by payer or involved participant
    - date_from, date_to: Filter by date range
    - search: Search in description
    
    Example Request:
        GET /api/groups/123e4567.../expenses?page=1&page_size=10&category=Food
        Authorization: Bearer token...
    
    Example Response:
        {
            "expenses": [...],
            "total": 25,
            "page": 1,
            "page_size": 10
        }
    """
    # Base query
    query = db.query(Expense).filter(Expense.group_id == group.id)
    
    # Apply filters
    if category:
        query = query.filter(Expense.category == category)
    
    if participant_id:
        # Filter by payer or participant in splits
        query = query.filter(
            or_(
                Expense.payer_id == participant_id,
                Expense.id.in_(
                    db.query(ExpenseSplit.expense_id).filter(
                        ExpenseSplit.participant_id == participant_id
                    )
                )
            )
        )
    
    if date_from:
        query = query.filter(Expense.expense_date >= date_from)
    
    if date_to:
        query = query.filter(Expense.expense_date <= date_to)
    
    if search:
        query = query.filter(Expense.description.ilike(f"%{search}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order
    expenses = query.order_by(Expense.expense_date.desc()).offset(
        pagination["skip"]
    ).limit(pagination["limit"]).all()
    
    # Add payer names to responses
    expense_responses = []
    for expense in expenses:
        response = ExpenseResponse.from_orm(expense)
        response.payer_name = expense.payer.name
        expense_responses.append(response)
    
    return ExpenseListResponse(
        expenses=expense_responses,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"]
    )


@router.post(
    "/groups/{group_id}/expenses",
    response_model=ExpenseDetailResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense(
    group_id: UUID,
    expense_data: ExpenseCreate,
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Create a new expense with splits.
    
    Steps:
    1. Validate payer exists in group
    2. Create expense
    3. Validate and create splits
    4. Return expense with splits
    
    Example Request:
        POST /api/groups/123e4567.../expenses
        Authorization: Bearer token...
        {
            "description": "Dinner",
            "amount": "120.00",
            "payer_id": "789e4567...",
            "expense_date": "2024-01-15",
            "split_mode": "equal",
            "category": "Food & Dining",
            "splits": [
                {"participant_id": "789e4567...", "amount": "40.00"},
                {"participant_id": "012e4567...", "amount": "40.00"},
                {"participant_id": "345e4567...", "amount": "40.00"}
            ]
        }
    """
    # Validate payer exists in group
    payer = db.query(Participant).filter(
        Participant.id == expense_data.payer_id,
        Participant.group_id == group_id
    ).first()
    
    if not payer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payer not found in this group"
        )
    
    # Create expense
    new_expense = Expense(
        group_id=group_id,
        description=expense_data.description,
        amount=expense_data.amount,
        payer_id=expense_data.payer_id,
        expense_date=expense_data.expense_date,
        split_mode=expense_data.split_mode,
        category=expense_data.category
    )
    
    db.add(new_expense)
    db.flush()  # Get expense ID without committing
    
    # Validate and create splits
    validate_and_create_splits(new_expense, expense_data.splits, db)
    
    db.commit()
    db.refresh(new_expense)
    
    # Build detailed response
    split_responses = []
    for split in new_expense.splits:
        split_response = ExpenseSplitResponse.from_orm(split)
        split_response.participant_name = split.participant.name
        split_responses.append(split_response)
    
    response = ExpenseDetailResponse.from_orm(new_expense)
    response.payer_name = new_expense.payer.name
    response.splits = split_responses
    
    return response


@router.get("/expenses/{expense_id}", response_model=ExpenseDetailResponse)
def get_expense(
    expense_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific expense.
    
    Includes all splits with participant names.
    """
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Verify user owns the group
    if expense.group.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this expense"
        )
    
    # Build response with splits
    split_responses = []
    for split in expense.splits:
        split_response = ExpenseSplitResponse.from_orm(split)
        split_response.participant_name = split.participant.name
        split_responses.append(split_response)
    
    response = ExpenseDetailResponse.from_orm(expense)
    response.payer_name = expense.payer.name
    response.splits = split_responses
    
    return response


@router.delete("/expenses/{expense_id}", response_model=MessageResponse)
def delete_expense(
    expense_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an expense.
    
    This will cascade delete all splits.
    """
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Verify user owns the group
    if expense.group.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this expense"
        )
    
    db.delete(expense)
    db.commit()
    
    return {"message": "Expense deleted successfully"}