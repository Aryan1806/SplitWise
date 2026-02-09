"""
Expense Model
Represents an expense in a group with split information.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class SplitMode(str, enum.Enum):
    """Enum for different ways to split an expense."""
    EQUAL = "equal"
    CUSTOM_AMOUNT = "custom_amount"
    PERCENTAGE = "percentage"


class Expense(Base):
    """
    Expense model for tracking group expenses.
    
    An expense records:
    - What was purchased (description)
    - How much it cost (amount)
    - Who paid (payer)
    - How it should be split (split_mode)
    - Individual splits for each participant
    
    Relationships:
    - group: The group this expense belongs to
    - payer: The participant who paid for this expense
    - splits: How the expense is divided among participants
    """
    __tablename__ = "expenses"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign Key to Group
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Expense details
    description = Column(
        String(500),
        nullable=False
    )
    
    amount = Column(
        Numeric(10, 2),  # 10 digits total, 2 after decimal
        nullable=False
    )
    
    # Foreign Key to Participant (who paid)
    payer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    expense_date = Column(
        Date,
        nullable=False,
        index=True  # Index for date-based queries
    )
    
    split_mode = Column(
        Enum(SplitMode),
        nullable=False,
        default=SplitMode.EQUAL
    )
    
    category = Column(
        String(100),
        nullable=True,
        index=True  # Index for category filtering
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    group = relationship(
        "Group",
        back_populates="expenses",
        lazy="joined"
    )
    
    payer = relationship(
        "Participant",
        back_populates="expenses_paid",
        foreign_keys=[payer_id],
        lazy="joined"
    )
    
    splits = relationship(
        "ExpenseSplit",
        back_populates="expense",
        cascade="all, delete-orphan",
        lazy="selectin"  # Load splits with expense
    )
    
    def __repr__(self):
        """String representation for debugging."""
        return f"<Expense(id={self.id}, description={self.description}, amount={self.amount})>"