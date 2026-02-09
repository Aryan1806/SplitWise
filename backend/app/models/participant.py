"""
Group Model
Represents a group where expenses are tracked and split.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Group(Base):
    """
    Group model for organizing expenses.
    
    A group has:
    - One owner (user who created it)
    - Multiple participants (max 3 + owner = 4 total)
    - Multiple expenses
    
    Relationships:
    - owner: The user who created this group
    - participants: All participants in this group
    - expenses: All expenses in this group
    """
    __tablename__ = "groups"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Group details
    name = Column(
        String(255),
        nullable=False
    )
    
    # Foreign Key to User (owner)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),  # Delete group if owner deleted
        nullable=False,
        index=True  # Index for faster queries
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
    owner = relationship(
        "User",
        back_populates="groups",
        lazy="joined"  # Eagerly load owner with group
    )
    
    participants = relationship(
        "Participant",
        back_populates="group",
        cascade="all, delete-orphan",  # Delete participants when group deleted
        lazy="selectin"  # Load participants in separate query
    )
    
    expenses = relationship(
        "Expense",
        back_populates="group",
        cascade="all, delete-orphan",  # Delete expenses when group deleted
        lazy="select"  # Load on demand
    )
    
    def __repr__(self):
        """String representation for debugging."""
        return f"<Group(id={self.id}, name={self.name}, owner_id={self.owner_id})>" 