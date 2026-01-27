"""
Thin helpers for transaction objects. For the canonical Transaction dataclass
we reuse database.models.Transaction to avoid duplication.
"""

from database.models import Transaction as DBTransaction
from typing import Dict


def to_dict(tx: DBTransaction) -> Dict:
    """
    Convert a DB Transaction dataclass to a plain dict (useful for display / export).
    """
    return {
        "id": tx.id,
        "user_id": tx.user_id,
        "date": tx.date,
        "amount": tx.amount,
        "category": tx.category,
        "type": tx.ttype,
        "description": tx.description
    }
