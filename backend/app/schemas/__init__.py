"""
Schemas Package
Exports all Pydantic schemas for API validation.
"""
# User schemas
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB
)

# Auth schemas
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    TokenData,
    PasswordChangeRequest,
    MessageResponse
)

# Group schemas
from app.schemas.group import (
    GroupBase,
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupDetailResponse,
    GroupSummaryResponse
)

# Participant schemas
from app.schemas.participant import (
    ParticipantBase,
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    ParticipantWithBalance
)

# Expense schemas
from app.schemas.expense import (
    ExpenseSplitCreate,
    ExpenseSplitResponse,
    ExpenseBase,
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseDetailResponse,
    ExpenseListResponse
)

# Balance schemas
from app.schemas.balance import (
    ParticipantBalance,
    BalanceEdge,
    GroupBalanceResponse,
    Settlement,
    SettlementSuggestion
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Auth
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "TokenData",
    "PasswordChangeRequest",
    "MessageResponse",
    # Group
    "GroupBase",
    "GroupCreate",
    "GroupUpdate",
    "GroupResponse",
    "GroupDetailResponse",
    "GroupSummaryResponse",
    # Participant
    "ParticipantBase",
    "ParticipantCreate",
    "ParticipantUpdate",
    "ParticipantResponse",
    "ParticipantWithBalance",
    # Expense
    "ExpenseSplitCreate",
    "ExpenseSplitResponse",
    "ExpenseBase",
    "ExpenseCreate",
    "ExpenseUpdate",
    "ExpenseResponse",
    "ExpenseDetailResponse",
    "ExpenseListResponse",
    # Balance
    "ParticipantBalance",
    "BalanceEdge",
    "GroupBalanceResponse",
    "Settlement",
    "SettlementSuggestion",
]