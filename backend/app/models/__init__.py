"""
Models Package
Exports all database models for easy importing.
"""
from app.models.user import User
from app.models.group import Group
from app.models.participant import Participant
from app.models.expense import Expense, SplitMode
from app.models.expense_split import ExpenseSplit

# This allows us to import like: from app.models import User, Group, etc.
__all__ = [
    "User",
    "Group",
    "Participant",
    "Expense",
    "ExpenseSplit",
    "SplitMode"
]