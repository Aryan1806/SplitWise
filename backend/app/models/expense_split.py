"""
ExpenseSplit Model
Tracks how an expense is split among participants.
"""
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ExpenseSplit(Base):
    """
    ExpenseSplit model for tracking individual participant shares.
    
    Each split represents one participant's share of an expense.
    
    For example, if an expense of $100 is split equally among 3 people:
    - Split 1: participant_id=A, amount=33.34
    - Split 2: participant_id=B, amount=33.33
    - Split 3: participant_id=C, amount=33.33
    
    Relationships:
    - expense: The expense this split belongs to
    - participant: The participant this split is for
    """
    __tablename__ = "expense_splits"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign Key to Expense
    expense_id = Column(
        UUID(as_uuid=True),
        ForeignKey("expenses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Foreign Key to Participant
    participant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Split details
    amount = Column(
        Numeric(10, 2),
        nullable=False
    )
    
    percentage = Column(
        Numeric(5, 2),  # For percentage splits (0.00 to 100.00)
        nullable=True
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    expense = relationship(
        "Expense",
        back_populates="splits",
        lazy="joined"
    )
    
    participant = relationship(
        "Participant",
        back_populates="expense_splits",
        lazy="joined"
    )
    
    # Constraints
    __table_args__ = (
        # Ensure each participant appears only once per expense
        UniqueConstraint('expense_id', 'participant_id', name='uq_expense_participant'),
    )
    
    def __repr__(self):
        """String representation for debugging."""
        return f"<ExpenseSplit(expense_id={self.expense_id}, participant_id={self.participant_id}, amount={self.amount})>"