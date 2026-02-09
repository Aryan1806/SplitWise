"""
User API Routes
Handles user profile management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile.
    
    Same as GET /auth/me but under /users endpoint.
    
    Example Request:
        GET /api/users/me
        Authorization: Bearer token...
    
    Example Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "full_name": "John Doe",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Can update: full_name, email
    All fields are optional.
    
    Example Request:
        PUT /api/users/me
        Authorization: Bearer token...
        {
            "full_name": "John Smith"
        }
    
    Example Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "full_name": "John Smith",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T20:45:00Z"
        }
    """
    # Update fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        # Check if new email is already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/me", response_model=MessageResponse)
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user's account.
    
    ⚠️ WARNING: This will cascade delete:
    - All groups owned by the user
    - All participants in those groups
    - All expenses in those groups
    - All expense splits
    
    Example Request:
        DELETE /api/users/me
        Authorization: Bearer token...
    
    Example Response:
        {
            "message": "Account deleted successfully"
        }
    """
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}