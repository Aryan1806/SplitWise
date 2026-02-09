"""
Expense Schemas
Pydantic models for Expense-related requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from app.models.expense import SplitMode


class ExpenseSplitCreate(BaseModel):
    """
    Schema for creating an expense split.
    
    Example:
        {
            "participant_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "33.33",
            "percentage": null
        }
    """
    participant_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Ensure amount is positive."""
        if v <= 0:
            raise ValueError("Split amount must be positive")
        return v


class ExpenseSplitResponse(BaseModel):
    """
    Schema for expense split response.
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "expense_id": "456e4567-e89b-12d3-a456-426614174001",
            "participant_id": "789e4567-e89b-12d3-a456-426614174002",
            "participant_name": "Alice",
            "amount": "33.33",
            "percentage": null
        }
    """
    id: UUID
    expense_id: UUID
    participant_id: UUID
    participant_name: Optional[str] = None
    amount: Decimal
    percentage: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    """Base Expense schema with common fields."""
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    expense_date: date
    category: Optional[str] = Field(None, max_length=100)
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is not just whitespace."""
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Ensure amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @field_validator("expense_date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        """Ensure date is not in the future."""
        if v > date.today():
            raise ValueError("Expense date cannot be in the future")
        return v


class ExpenseCreate(ExpenseBase):
    """
    Schema for creating a new expense.
    
    Example:
        {
            "description": "Dinner at Olive Garden",
            "amount": "120.00",
            "payer_id": "123e4567-e89b-12d3-a456-426614174000",
            "expense_date": "2024-01-15",
            "split_mode": "equal",
            "category": "Food & Dining",
            "splits": [
                {
                    "participant_id": "123e4567-e89b-12d3-a456-426614174000",
                    "amount": "40.00"
                },
                {
                    "participant_id": "456e4567-e89b-12d3-a456-426614174001",
                    "amount": "40.00"
                },
                {
                    "participant_id": "789e4567-e89b-12d3-a456-426614174002",
                    "amount": "40.00"
                }
            ]
        }
    """
    payer_id: UUID
    split_mode: SplitMode = SplitMode.EQUAL
    splits: List[ExpenseSplitCreate] = Field(..., min_length=1)
    
    @field_validator("splits")
    @classmethod
    def validate_splits(cls, v: List[ExpenseSplitCreate], info) -> List[ExpenseSplitCreate]:
        """Validate that splits sum to total amount."""
        # This validator runs before we have access to amount
        # We'll do comprehensive validation in the service layer
        if not v:
            raise ValueError("At least one split is required")
        return v


class ExpenseUpdate(BaseModel):
    """
    Schema for updating an expense.
    
    All fields are optional.
    
    Example:
        {
            "description": "Dinner at Chipotle",
            "amount": "45.00"
        }
    """
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    payer_id: Optional[UUID] = None
    expense_date: Optional[date] = None
    category: Optional[str] = Field(None, max_length=100)
    split_mode: Optional[SplitMode] = None
    splits: Optional[List[ExpenseSplitCreate]] = None


class ExpenseResponse(ExpenseBase):
    """
    Schema for expense response data.
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "group_id": "456e4567-e89b-12d3-a456-426614174001",
            "description": "Dinner at Olive Garden",
            "amount": "120.00",
            "payer_id": "789e4567-e89b-12d3-a456-426614174002",
            "payer_name": "Alice",
            "expense_date": "2024-01-15",
            "split_mode": "equal",
            "category": "Food & Dining",
            "created_at": "2024-01-15T20:30:00Z",
            "updated_at": "2024-01-15T20:30:00Z"
        }
    """
    id: UUID
    group_id: UUID
    payer_id: UUID
    payer_name: Optional[str] = None
    split_mode: SplitMode
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExpenseDetailResponse(ExpenseResponse):
    """
    Detailed expense response including splits.
    
    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "description": "Dinner at Olive Garden",
            "amount": "120.00",
            "payer_name": "Alice",
            "splits": [
                {
                    "participant_name": "Alice",
                    "amount": "40.00"
                },
                {
                    "participant_name": "Bob",
                    "amount": "40.00"
                },
                {
                    "participant_name": "Charlie",
                    "amount": "40.00"
                }
            ]
        }
    """
    splits: List[ExpenseSplitResponse] = []


class ExpenseListResponse(BaseModel):
    """
    Schema for paginated expense list.
    
    Example:
        {
            "expenses": [...],
            "total": 25,
            "page": 1,
            "page_size": 10
        }
    """
    expenses: List[ExpenseResponse]
    total: int
    page: int = 1
    page_size: int = 10