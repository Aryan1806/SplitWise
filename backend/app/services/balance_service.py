"""
Balance Service
Handles balance calculations and settlement suggestions.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from uuid import UUID
from decimal import Decimal
from collections import defaultdict

from app.models import Expense, ExpenseSplit, Participant


class BalanceService:
    """
    Service for calculating balances and generating settlement suggestions.
    
    Core concepts:
    - total_paid: How much a participant paid for expenses
    - total_share: How much a participant owes (their share of all expenses)
    - net_balance: total_paid - total_share
        - Positive: They are owed money (creditor)
        - Negative: They owe money (debtor)
        - Zero: They're settled up
    """
    
    @staticmethod
    def calculate_participant_balances(group_id: UUID, db: Session) -> Dict:
        """
        Calculate net balances for all participants in a group.
        
        Returns a dictionary:
        {
            "participant_id": {
                "participant": Participant object,
                "total_paid": Decimal,
                "total_share": Decimal,
                "net_balance": Decimal
            }
        }
        """
        # Get all participants
        participants = db.query(Participant).filter(
            Participant.group_id == group_id
        ).all()
        
        # Initialize balances
        balances = {}
        for participant in participants:
            balances[participant.id] = {
                "participant": participant,
                "total_paid": Decimal("0.00"),
                "total_share": Decimal("0.00"),
                "net_balance": Decimal("0.00")
            }
        
        # Calculate total paid (expenses where participant was payer)
        expenses = db.query(Expense).filter(
            Expense.group_id == group_id
        ).all()
        
        for expense in expenses:
            if expense.payer_id in balances:
                balances[expense.payer_id]["total_paid"] += expense.amount
        
        # Calculate total share (sum of all splits for each participant)
        splits = db.query(ExpenseSplit).join(
            Expense
        ).filter(
            Expense.group_id == group_id
        ).all()
        
        for split in splits:
            if split.participant_id in balances:
                balances[split.participant_id]["total_share"] += split.amount
        
        # Calculate net balances
        for participant_id in balances:
            total_paid = balances[participant_id]["total_paid"]
            total_share = balances[participant_id]["total_share"]
            balances[participant_id]["net_balance"] = total_paid - total_share
        
        return balances
    
    @staticmethod
    def generate_balance_matrix(balances: Dict) -> List[Dict]:
        """
        Generate a matrix showing who owes whom.
        
        This is a simplified view - not optimized for minimum transactions.
        
        Returns a list of edges:
        [
            {
                "from_participant_id": UUID,
                "from_participant_name": str,
                "to_participant_id": UUID,
                "to_participant_name": str,
                "amount": Decimal
            }
        ]
        """
        edges = []
        
        # Separate into creditors (owed money) and debtors (owe money)
        creditors = []  # People who are owed money
        debtors = []    # People who owe money
        
        for participant_id, balance_data in balances.items():
            net_balance = balance_data["net_balance"]
            if net_balance > Decimal("0.01"):  # Small threshold for rounding
                creditors.append({
                    "id": participant_id,
                    "name": balance_data["participant"].name,
                    "amount": net_balance
                })
            elif net_balance < Decimal("-0.01"):
                debtors.append({
                    "id": participant_id,
                    "name": balance_data["participant"].name,
                    "amount": abs(net_balance)
                })
        
        # Create edges from debtors to creditors
        for debtor in debtors:
            for creditor in creditors:
                if debtor["amount"] > Decimal("0.01") and creditor["amount"] > Decimal("0.01"):
                    # Amount to transfer
                    transfer_amount = min(debtor["amount"], creditor["amount"])
                    
                    edges.append({
                        "from_participant_id": debtor["id"],
                        "from_participant_name": debtor["name"],
                        "to_participant_id": creditor["id"],
                        "to_participant_name": creditor["name"],
                        "amount": transfer_amount
                    })
                    
                    # Update remaining amounts
                    debtor["amount"] -= transfer_amount
                    creditor["amount"] -= transfer_amount
        
        return edges
    
    @staticmethod
    def generate_settlement_suggestions(balances: Dict) -> List[Dict]:
        """
        Generate optimized settlement suggestions using greedy algorithm.
        
        This minimizes the number of transactions needed to settle all debts.
        
        Algorithm:
        1. Separate participants into creditors and debtors
        2. Sort both by amount (largest first)
        3. Match largest creditor with largest debtor
        4. Create settlement for min(creditor_amount, debtor_amount)
        5. Repeat until all settled
        
        Returns list of settlements:
        [
            {
                "from_participant_id": UUID,
                "from_participant_name": str,
                "to_participant_id": UUID,
                "to_participant_name": str,
                "amount": Decimal,
                "description": str
            }
        ]
        """
        # Separate into creditors and debtors
        creditors = []
        debtors = []
        
        for participant_id, balance_data in balances.items():
            net_balance = balance_data["net_balance"]
            participant = balance_data["participant"]
            
            if net_balance > Decimal("0.01"):  # Creditor (owed money)
                creditors.append({
                    "id": participant_id,
                    "name": participant.name,
                    "amount": net_balance
                })
            elif net_balance < Decimal("-0.01"):  # Debtor (owes money)
                debtors.append({
                    "id": participant_id,
                    "name": participant.name,
                    "amount": abs(net_balance)
                })
        
        # Sort by amount (largest first) for greedy algorithm
        creditors.sort(key=lambda x: x["amount"], reverse=True)
        debtors.sort(key=lambda x: x["amount"], reverse=True)
        
        settlements = []
        
        # Use two pointers to match creditors and debtors
        i, j = 0, 0
        
        while i < len(creditors) and j < len(debtors):
            creditor = creditors[i]
            debtor = debtors[j]
            
            # Amount to settle
            settle_amount = min(creditor["amount"], debtor["amount"])
            
            # Create settlement
            settlements.append({
                "from_participant_id": debtor["id"],
                "from_participant_name": debtor["name"],
                "to_participant_id": creditor["id"],
                "to_participant_name": creditor["name"],
                "amount": settle_amount,
                "description": f"{debtor['name']} pays {creditor['name']} ${settle_amount:.2f}"
            })
            
            # Update amounts
            creditor["amount"] -= settle_amount
            debtor["amount"] -= settle_amount
            
            # Move pointers
            if creditor["amount"] < Decimal("0.01"):
                i += 1
            if debtor["amount"] < Decimal("0.01"):
                j += 1
        
        return settlements
    
    @staticmethod
    def is_group_settled(balances: Dict) -> bool:
        """
        Check if all balances in a group are settled (within rounding tolerance).
        
        Returns:
            True if all net_balances are approximately zero
        """
        for balance_data in balances.values():
            if abs(balance_data["net_balance"]) > Decimal("0.01"):
                return False
        return True