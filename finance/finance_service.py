"""
Higher-level finance helpers that validate input and provide filtering/export capabilities.
They wrap the lower-level database functions (so UI stays simple).
"""

from typing import List, Tuple, Optional
from datetime import datetime, date
import csv
import os

from database.db import add_transaction as db_add_transaction, get_transactions_by_user, get_balance, get_monthly_summary, update_transaction as db_update_transaction, delete_transaction as db_delete_transaction
from database.models import Transaction as DBTransaction
from config import settings
from .transaction import to_dict


def add_transaction_validated(user_id: int, date_iso: str, amount: float, category: str, ttype: str, description: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate transaction data (simple checks) then call DB insert.
    """
    # Validate user_id
    if user_id is None:
        return False, "User not authenticated."

    # Validate date
    try:
        # Accept YYYY-MM-DD
        datetime.fromisoformat(date_iso)
    except Exception:
        return False, "Invalid date format. Use YYYY-MM-DD."

    # Validate amount
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be greater than zero."
    except Exception:
        return False, "Invalid amount."

    if ttype not in ("income", "expense"):
        return False, "Type must be 'income' or 'expense'."

    if not category or not category.strip():
        return False, "Category is required."

    return db_add_transaction(user_id, date_iso, amount, category.strip(), ttype, description)


def get_transactions_filtered(user_id: int, limit: int = 500, start_date: Optional[str] = None, end_date: Optional[str] = None, category: Optional[str] = None) -> List[DBTransaction]:
    """
    Get transactions by user and optionally filter by date range and category.
    Dates must be ISO YYYY-MM-DD if provided.
    """
    txs = get_transactions_by_user(user_id, limit=limit)
    filtered = []
    for t in txs:
        ok = True
        if start_date:
            try:
                ok &= (t.date >= start_date)
            except Exception:
                pass
        if end_date:
            try:
                ok &= (t.date <= end_date)
            except Exception:
                pass
        if category:
            ok &= (t.category == category)
        if ok:
            filtered.append(t)
    return filtered


def update_transaction_validated(user_id: int, tx_id: int, date_iso: str, amount: float, category: str, ttype: str, description: Optional[str] = None) -> Tuple[bool, str]:
    if user_id is None:
        return False, "User not authenticated."

    try:
        datetime.fromisoformat(date_iso)
    except Exception:
        return False, "Invalid date format. Use YYYY-MM-DD."

    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be greater than zero."
    except Exception:
        return False, "Invalid amount."

    if ttype not in ("income", "expense"):
        return False, "Type must be 'income' or 'expense'."

    if not category or not category.strip():
        return False, "Category is required."

    return db_update_transaction(tx_id, user_id, date_iso, amount, category.strip(), ttype, description)


def delete_transaction(user_id: int, tx_id: int) -> Tuple[bool, str]:
    if user_id is None:
        return False, "User not authenticated."
    return db_delete_transaction(tx_id, user_id)


def calculate_balance(user_id: int) -> float:
    return get_balance(user_id)


def export_transactions_csv(user_id: int, filepath: Optional[str] = None, txs: Optional[List[DBTransaction]] = None) -> Tuple[bool, str]:
    """
    Export transactions to CSV. If filepath is None, save to data/transactions_export_<user>_<date>.csv
    Returns (success, filepath_or_error)
    """
    if txs is None:
        txs = get_transactions_by_user(user_id, limit=10000)

    if filepath is None:
        fn = f"transactions_export_{user_id}_{date.today().isoformat()}.csv"
        filepath = os.path.join(settings.DATA_DIR, fn)

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "user_id", "date", "amount", "category", "type", "description"])
            for t in txs:
                writer.writerow([
                    t.id, t.user_id, t.date, t.amount, t.category, t.ttype, t.description or ""
                ])
        return True, filepath
    except Exception as e:
        return False, f"Error exporting CSV: {e}"
