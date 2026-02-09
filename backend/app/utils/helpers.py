"""
Helper Utilities
Common helper functions used throughout the application.
"""
from decimal import Decimal, ROUND_HALF_EVEN
from typing import List
from datetime import datetime


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    Round a Decimal to specified places using banker's rounding.
    
    Banker's rounding (ROUND_HALF_EVEN) rounds .5 to the nearest even number,
    which helps prevent bias in repeated calculations.
    
    Args:
        value: Decimal value to round
        places: Number of decimal places (default: 2)
        
    Returns:
        Rounded Decimal
        
    Examples:
        round_decimal(Decimal("10.125"), 2)  # Returns 10.12
        round_decimal(Decimal("10.135"), 2)  # Returns 10.14
    """
    quantizer = Decimal(10) ** -places
    return value.quantize(quantizer, rounding=ROUND_HALF_EVEN)


def split_amount_equally(amount: Decimal, num_participants: int) -> List[Decimal]:
    """
    Split an amount equally among participants with proper rounding.
    
    Ensures the sum of splits exactly equals the total amount by
    adjusting the first participant's share if needed.
    
    Args:
        amount: Total amount to split
        num_participants: Number of people to split among
        
    Returns:
        List of split amounts
        
    Example:
        split_amount_equally(Decimal("100"), 3)
        # Returns [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
    """
    if num_participants <= 0:
        raise ValueError("Number of participants must be positive")
    
    # Calculate base amount per person
    base_amount = round_decimal(amount / num_participants)
    
    # Create list of equal splits
    splits = [base_amount] * num_participants
    
    # Adjust first participant's share to account for rounding
    total_splits = sum(splits)
    if total_splits != amount:
        difference = amount - total_splits
        splits[0] += difference
    
    return splits


def calculate_percentage_amount(total: Decimal, percentage: Decimal) -> Decimal:
    """
    Calculate amount from percentage.
    
    Args:
        total: Total amount
        percentage: Percentage (0-100)
        
    Returns:
        Calculated amount rounded to 2 decimal places
        
    Example:
        calculate_percentage_amount(Decimal("100"), Decimal("33.33"))
        # Returns Decimal("33.33")
    """
    if percentage < 0 or percentage > 100:
        raise ValueError("Percentage must be between 0 and 100")
    
    amount = (total * percentage) / 100
    return round_decimal(amount)


def format_currency(amount: Decimal) -> str:
    """
    Format a Decimal amount as currency string.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
        
    Example:
        format_currency(Decimal("1234.56"))  # Returns "$1,234.56"
    """
    return f"${amount:,.2f}"


def get_color_for_index(index: int) -> str:
    """
    Get a color from the predefined palette based on index.
    
    Used for assigning colors to participants.
    
    Args:
        index: Index of participant (0-3)
        
    Returns:
        Hex color code
        
    Example:
        get_color_for_index(0)  # Returns "#2DD4BF" (Teal)
    """
    # Color palette from design system
    colors = [
        "#2DD4BF",  # Teal (accent-1)
        "#FCD34D",  # Amber (accent-2)
        "#F43F5E",  # Rose (accent-3)
        "#3B82F6",  # Blue (accent-4)
    ]
    return colors[index % len(colors)]


def parse_date_string(date_str: str) -> datetime:
    """
    Parse date string in ISO format.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        datetime object
        
    Example:
        parse_date_string("2024-01-15")
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    Sanitize and trim a string input.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    
    # Strip whitespace and limit length
    text = text.strip()[:max_length]
    return text