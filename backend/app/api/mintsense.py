"""
MintSense AI API Routes
Handles AI-powered features (to be implemented in Step 4).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.database import get_db
from app.models import Group
from app.dependencies import verify_group_access

router = APIRouter(prefix="/mintsense", tags=["MintSense AI"])


class ParseExpenseRequest(BaseModel):
    """Request to parse natural language into expense data."""
    text: str
    group_id: UUID


class ParseExpenseResponse(BaseModel):
    """Parsed expense data from natural language."""
    description: str
    amount: float
    payer_name: str | None = None
    participant_names: list[str] = []
    category: str | None = None


class CategorizeRequest(BaseModel):
    """Request to auto-categorize an expense."""
    description: str


class CategorizeResponse(BaseModel):
    """Suggested category for an expense."""
    category: str
    confidence: float


@router.post("/parse-expense", response_model=ParseExpenseResponse)
def parse_expense(
    request: ParseExpenseRequest,
    db: Session = Depends(get_db)
):
    """
    Parse natural language text into structured expense data.
    
    Example:
    Input: "I paid $50 for dinner with John and Sarah"
    Output: {
        "description": "Dinner",
        "amount": 50.0,
        "payer_name": "Current User",
        "participant_names": ["John", "Sarah"],
        "category": "Food & Dining"
    }
    
    TODO: Implement AI parsing in Step 4
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI parsing not yet implemented. Will be added in Step 4."
    )


@router.post("/categorize", response_model=CategorizeResponse)
def categorize_expense(
    request: CategorizeRequest,
    db: Session = Depends(get_db)
):
    """
    Auto-categorize an expense based on description.
    
    Example:
    Input: "Uber to airport"
    Output: {
        "category": "Transport",
        "confidence": 0.95
    }
    
    TODO: Implement AI categorization in Step 4
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI categorization not yet implemented. Will be added in Step 4."
    )


@router.get("/groups/{group_id}/summary")
def generate_group_summary(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Generate a natural language summary of group expenses.
    
    Example:
    "Your group 'Weekend Trip' has spent $450 total. 
    Alice has paid the most at $200, while Bob owes $75. 
    Consider settling balances before the next trip!"
    
    TODO: Implement AI summary in Step 4
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI summary not yet implemented. Will be added in Step 4."
    )


@router.post("/groups/{group_id}/suggest-settlement")
def suggest_settlement_with_ai(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Use AI to suggest optimal settlement strategy with explanations.
    
    TODO: Implement AI settlement suggestions in Step 4
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI settlement suggestions not yet implemented. Will be added in Step 4."
    )