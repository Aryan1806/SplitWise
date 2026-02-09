"""
Balance API Routes
Handles balance calculations and settlement suggestions.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import Group
from app.schemas.balance import (
    ParticipantBalance,
    BalanceEdge,
    GroupBalanceResponse,
    Settlement,
    SettlementSuggestion
)
from app.dependencies import verify_group_access
from app.services.balance_service import BalanceService

router = APIRouter(tags=["Balances"])


@router.get("/groups/{group_id}/balances", response_model=GroupBalanceResponse)
def get_group_balances(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Get complete balance information for a group.
    
    Returns:
    - Individual participant balances (what they paid vs what they owe)
    - Balance matrix (who owes whom)
    - Settlement status
    
    Example Request:
        GET /api/groups/123e4567.../balances
        Authorization: Bearer token...
    
    Example Response:
        {
            "group_id": "123e4567...",
            "participant_balances": [
                {
                    "participant_id": "789e4567...",
                    "participant_name": "Alice",
                    "color": "#2DD4BF",
                    "total_paid": "150.00",
                    "total_share": "100.00",
                    "net_balance": "50.00"
                },
                {
                    "participant_id": "012e4567...",
                    "participant_name": "Bob",
                    "color": "#FCD34D",
                    "total_paid": "50.00",
                    "total_share": "100.00",
                    "net_balance": "-50.00"
                }
            ],
            "balance_matrix": [
                {
                    "from_participant_id": "012e4567...",
                    "from_participant_name": "Bob",
                    "to_participant_id": "789e4567...",
                    "to_participant_name": "Alice",
                    "amount": "50.00"
                }
            ],
            "is_settled": false
        }
    """
    # Calculate balances
    balances = BalanceService.calculate_participant_balances(group.id, db)
    
    # Build participant balance responses
    participant_balances = []
    for participant_id, balance_data in balances.items():
        participant = balance_data["participant"]
        participant_balance = ParticipantBalance(
            participant_id=participant_id,
            participant_name=participant.name,
            color=participant.color or "#000000",
            total_paid=balance_data["total_paid"],
            total_share=balance_data["total_share"],
            net_balance=balance_data["net_balance"]
        )
        participant_balances.append(participant_balance)
    
    # Sort by net_balance (highest first)
    participant_balances.sort(key=lambda x: x.net_balance, reverse=True)
    
    # Generate balance matrix
    matrix_edges = BalanceService.generate_balance_matrix(balances)
    balance_edges = []
    for edge in matrix_edges:
        balance_edge = BalanceEdge(
            from_participant_id=edge["from_participant_id"],
            from_participant_name=edge["from_participant_name"],
            to_participant_id=edge["to_participant_id"],
            to_participant_name=edge["to_participant_name"],
            amount=edge["amount"]
        )
        balance_edges.append(balance_edge)
    
    # Check if settled
    is_settled = BalanceService.is_group_settled(balances)
    
    return GroupBalanceResponse(
        group_id=group.id,
        participant_balances=participant_balances,
        balance_matrix=balance_edges,
        is_settled=is_settled
    )


@router.get("/groups/{group_id}/settlements", response_model=SettlementSuggestion)
def get_settlement_suggestions(
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Get optimized settlement suggestions for a group.
    
    Uses greedy algorithm to minimize number of transactions.
    
    Example Request:
        GET /api/groups/123e4567.../settlements
        Authorization: Bearer token...
    
    Example Response:
        {
            "settlements": [
                {
                    "from_participant_id": "012e4567...",
                    "from_participant_name": "Bob",
                    "to_participant_id": "789e4567...",
                    "to_participant_name": "Alice",
                    "amount": "50.00",
                    "description": "Bob pays Alice $50.00"
                }
            ],
            "total_transactions": 1,
            "total_amount": "50.00"
        }
    """
    # Calculate balances
    balances = BalanceService.calculate_participant_balances(group.id, db)
    
    # Generate settlement suggestions
    settlement_data = BalanceService.generate_settlement_suggestions(balances)
    
    # Build settlement responses
    settlements = []
    total_amount = Decimal("0.00")
    
    for settlement in settlement_data:
        settlement_obj = Settlement(
            from_participant_id=settlement["from_participant_id"],
            from_participant_name=settlement["from_participant_name"],
            to_participant_id=settlement["to_participant_id"],
            to_participant_name=settlement["to_participant_name"],
            amount=settlement["amount"],
            description=settlement["description"]
        )
        settlements.append(settlement_obj)
        total_amount += settlement["amount"]
    
    return SettlementSuggestion(
        settlements=settlements,
        total_transactions=len(settlements),
        total_amount=total_amount
    )


@router.get("/groups/{group_id}/participant-balance/{participant_id}", response_model=ParticipantBalance)
def get_participant_balance(
    participant_id: UUID,
    group: Group = Depends(verify_group_access),
    db: Session = Depends(get_db)
):
    """
    Get balance information for a specific participant.
    
    Example Request:
        GET /api/groups/123e4567.../participant-balance/789e4567...
        Authorization: Bearer token...
    
    Example Response:
        {
            "participant_id": "789e4567...",
            "participant_name": "Alice",
            "color": "#2DD4BF",
            "total_paid": "150.00",
            "total_share": "100.00",
            "net_balance": "50.00"
        }
    """
    # Calculate all balances
    balances = BalanceService.calculate_participant_balances(group.id, db)
    
    # Get specific participant balance
    if participant_id not in balances:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found in this group"
        )
    
    balance_data = balances[participant_id]
    participant = balance_data["participant"]
    
    return ParticipantBalance(
        participant_id=participant_id,
        participant_name=participant.name,
        color=participant.color or "#000000",
        total_paid=balance_data["total_paid"],
        total_share=balance_data["total_share"],
        net_balance=balance_data["net_balance"]
    )