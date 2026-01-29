

from typing import Tuple, Dict, Any, List
from auth import register_user, login_user, current_user_safe
from finance.finance_service import add_transaction_validated, get_transactions_filtered, update_transaction_validated, delete_transaction
from database.db import get_monthly_summary
from database.models import Transaction
from auth.auth_utils import validate_username_password


def api_register(username: str, password: str) -> Dict[str, Any]:
    ok, msg = validate_username_password(username, password)
    if not ok:
        return {"success": False, "message": msg}
    success, rmsg = register_user(username, password)
    return {"success": success, "message": rmsg}


def api_login(username: str, password: str) -> Dict[str, Any]:
    ok, user = login_user(username, password)
    if ok and user:
        return {"success": True, "user": current_user_safe(user)}
    return {"success": False, "message": "Invalid credentials"}


def api_get_transactions(user_id: int, **filters) -> Dict[str, Any]:
    if not user_id:
        return {"success": False, "message": "Auth required"}
    txs: List[Transaction] = get_transactions_filtered(user_id, **filters)
    
    serialized = [
        {"id": t.id, "user_id": t.user_id, "date": t.date, "amount": t.amount, "category": t.category, "type": t.ttype, "description": t.description}
        for t in txs
    ]
    return {"success": True, "transactions": serialized}


def api_post_transaction(user_id: int, date_iso: str, amount: float, category: str, ttype: str, description: str = None) -> Dict[str, Any]:
    if not user_id:
        return {"success": False, "message": "Auth required"}
    success, msg = add_transaction_validated(user_id, date_iso, amount, category, ttype, description)
    return {"success": success, "message": msg}


def api_update_transaction(user_id: int, tx_id: int, date_iso: str, amount: float, category: str, ttype: str, description: str = None) -> Dict[str, Any]:
    if not user_id:
        return {"success": False, "message": "Auth required"}
    success, msg = update_transaction_validated(user_id, tx_id, date_iso, amount, category, ttype, description)
    return {"success": success, "message": msg}


def api_delete_transaction(user_id: int, tx_id: int) -> Dict[str, Any]:
    if not user_id:
        return {"success": False, "message": "Auth required"}
    success, msg = delete_transaction(user_id, tx_id)
    return {"success": success, "message": msg}


def api_get_monthly_summary(user_id: int) -> Dict[str, Any]:
    if not user_id:
        return {"success": False, "message": "Auth required"}
    summary = get_monthly_summary(user_id)
    return {"success": True, "summary": summary}
