"""
Balance Schemas
Pydantic models for balance calculations and settlements.
"""
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from typing import List, Dict


class ParticipantBalance(BaseModel):
    """
    Balance information for a single participant.
    
    Example:
        {
            "participant_id": "123e4567-e89b-12d3-a456-426614174000",
            "participant_name": "Alice",
            "color": "#2DD4BF",
            "total_paid": "150.00",
            "total_share": "100.00",
            "net_balance": "50.00"
        }
    """
    participant_id: UUID
    participant_name: str
    color: str
    total_paid: Decimal
    total_share: Decimal
    net_balance: Decimal  # positive = owed to them, negative = they owe
    
    class Config:
        from_attributes = True


class BalanceEdge(BaseModel):
    """
    Represents who owes whom in the balance matrix.
    
    Example:
        {
            "from_participant_id": "123e4567-e89b-12d3-a456-426614174000",
            "from_participant_name": "Bob",
            "to_participant_id": "456e4567-e89b-12d3-a456-426614174001",
            "to_participant_name": "Alice",
            "amount": "25.00"
        }
    """
    from_participant_id: UUID
    from_participant_name: str
    to_participant_id: UUID
    to_participant_name: str
    amount: Decimal


class GroupBalanceResponse(BaseModel):
    """
    Complete balance information for a group.
    
    Example:
        {
            "group_id": "123e4567-e89b-12d3-a456-426614174000",
            "participant_balances": [
                {
                    "participant_id": "...",
                    "participant_name": "Alice",
                    "total_paid": "150.00",
                    "total_share": "100.00",
                    "net_balance": "50.00"
                }
            ],
            "balance_matrix": [
                {
                    "from_participant_name": "Bob",
                    "to_participant_name": "Alice",
                    "amount": "25.00"
                }
            ],
            "is_settled": false
        }
    """
    group_id: UUID
    participant_balances: List[ParticipantBalance]
    balance_matrix: List[BalanceEdge]
    is_settled: bool


class Settlement(BaseModel):
    """
    A single settlement transaction.
    
    Example:
        {
            "from_participant_id": "123e4567-e89b-12d3-a456-426614174000",
            "from_participant_name": "Bob",
            "to_participant_id": "456e4567-e89b-12d3-a456-426614174001",
            "to_participant_name": "Alice",
            "amount": "50.00",
            "description": "Bob pays Alice $50.00"
        }
    """
    from_participant_id: UUID
    from_participant_name: str
    to_participant_id: UUID
    to_participant_name: str
    amount: Decimal
    description: str


class SettlementSuggestion(BaseModel):
    """
    Suggested settlement plan to minimize transactions.
    
    Example:
        {
            "settlements": [
                {
                    "from_participant_name": "Bob",
                    "to_participant_name": "Alice",
                    "amount": "50.00",
                    "description": "Bob pays Alice $50.00"
                },
                {
                    "from_participant_name": "Charlie",
                    "to_participant_name": "Alice",
                    "amount": "25.00",
                    "description": "Charlie pays Alice $25.00"
                }
            ],
            "total_transactions": 2,
            "total_amount": "75.00"
        }
    """
    settlements: List[Settlement]
    total_transactions: int
    total_amount: Decimal