"""
Validators
Common validation functions for data integrity.
"""
from decimal import Decimal
from typing import List
from datetime import date


def validate_positive_amount(amount: Decimal) -> Decimal:
    """
    Validate that an amount is positive.
    
    Args:
        amount: Amount to validate
        
    Returns:
        The amount if valid
        
    Raises:
        ValueError: If amount is not positive
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return amount


def validate_splits_equal_total(splits: List[Decimal], total: Decimal) -> bool:
    """
    Validate that sum of splits equals total amount.
    
    Args:
        splits: List of split amounts
        total: Total amount
        
    Returns:
        True if splits sum to total
        
    Raises:
        ValueError: If splits don't sum to total
    """
    splits_sum = sum(splits)
    if splits_sum != total:
        raise ValueError(
            f"Splits sum ({splits_sum}) doesn't match total ({total})"
        )
    return True


def validate_percentage_total(percentages: List[Decimal]) -> bool:
    """
    Validate that percentages sum to 100.
    
    Args:
        percentages: List of percentage values
        
    Returns:
        True if percentages sum to 100
        
    Raises:
        ValueError: If percentages don't sum to 100
    """
    total = sum(percentages)
    if total != Decimal("100"):
        raise ValueError(
            f"Percentages must sum to 100, got {total}"
        )
    return True


def validate_participant_limit(current_count: int, max_count: int = 4) -> bool:
    """
    Validate participant count doesn't exceed limit.
    
    Args:
        current_count: Current number of participants
        max_count: Maximum allowed participants (default: 4)
        
    Returns:
        True if within limit
        
    Raises:
        ValueError: If limit exceeded
    """
    if current_count >= max_count:
        raise ValueError(
            f"Maximum {max_count} participants allowed per group"
        )
    return True


def validate_expense_date(expense_date: date) -> date:
    """
    Validate expense date is not in the future.
    
    Args:
        expense_date: Date of expense
        
    Returns:
        The date if valid
        
    Raises:
        ValueError: If date is in the future
    """
    if expense_date > date.today():
        raise ValueError("Expense date cannot be in the future")
    return expense_date


def validate_email_format(email: str) -> str:
    """
    Basic email format validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        Lowercased email if valid
        
    Raises:
        ValueError: If email format is invalid
    """
    email = email.lower().strip()
    if "@" not in email or "." not in email.split("@")[1]:
        raise ValueError("Invalid email format")
    return email