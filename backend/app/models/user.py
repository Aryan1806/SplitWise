"""
User Model
Represents a user in the system with authentication credentials.
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """
    User model for authentication and profile management.
    
    Relationships:
    - groups: All groups owned by this user
    """
    __tablename__ = "users"
    
    # Primary Key - Using UUID for better security and distribution
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Authentication fields
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True  # Index for faster lookups during login
    )
    
    hashed_password = Column(
        String(255),
        nullable=False
    )
    
    # Profile information
    full_name = Column(
        String(255),
        nullable=False
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set on creation
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # Automatically update on modification
        nullable=False
    )
    
    # Relationships
    groups = relationship(
        "Group",
        back_populates="owner",
        cascade="all, delete-orphan",  # Delete groups when user deleted
        lazy="select"
    )
    
    def __repr__(self):
        """String representation for debugging."""
        return f"<User(id={self.id}, email={self.email}, name={self.full_name})>"